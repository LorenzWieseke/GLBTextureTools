import os
import subprocess
import bpy

from .. Functions import gui_functions
from .. Functions import node_functions
from .. Functions import image_functions
from .. Functions import visibility_functions
from .. Functions import basic_functions
from .. Functions import material_functions
from .. Bake import bake_manager
from .. Functions import constants


class GTT_VerifyMaterialsOperator(bpy.types.Operator):
    """Check for each visbile material if it has a PBR Shader so the GLTF Export works fine"""
    bl_idname = "object.verify_materials"
    bl_label = "Verify Materials"
    
    def execute(self, context):

        vis_mats = material_functions.get_all_visible_materials()
       
        for mat in vis_mats:
            check_ok = node_functions.check_pbr(self,mat)
            if not check_ok:
                self.report({'INFO'}, "No PBR Shader in " + mat.name)

        objects_in_scene = bpy.data.objects
        for obj in objects_in_scene:
            for slot in obj.material_slots:
                if slot.material is None:
                    self.report({'INFO'}, "Empty Material Slot on " + obj.name)
        return {'FINISHED'}
    


# ----------------------- LIGHTAP OPERATORS--------------------#
class GTT_SelectLightmapObjectsOperator(bpy.types.Operator):
    """Select all Objects in the list that have the according lightmap attached to them. Makes it easy to rebake multiple Objects"""
    bl_idname = "object.select_lightmap_objects"
    bl_label = "Select Lightmap Objects"
    
    @classmethod
    def poll(cls, context):
        if context.scene.bake_settings.baking_groups == '-- Baking Groups --':
            return False
        return True

    def execute(self, context):

        C = context
        O = bpy.ops

        bake_settings = C.scene.bake_settings
        active_lightmap = bake_settings.baking_groups
        objects = [ob for ob in bpy.context.view_layer.objects if ob.visible_get()]

        O.object.select_all(action='DESELECT')
        for obj in objects:
            if obj.lightmap_name == active_lightmap or obj.ao_map_name == active_lightmap:
                C.view_layer.objects.active = obj
                obj.select_set(True)

        return {'FINISHED'}

# ----------------------- TEXTURE OPERATORS--------------------#

class GTT_GetMaterialByTextureOperator(bpy.types.Operator):
    bl_idname = "scene.select_mat_by_tex"
    bl_label = "Select Material By Texture"
    bl_description = "Selecting all materials in scene that use the selected texture"
    bl_options = {"REGISTER"}

    bpy.types.Scene.materials_found = []
    
    @classmethod
    def poll(cls, context):
        D = bpy.data
        images = D.images

        display = True

        # image to index not found
        try:
            sel_image_texture = images[context.scene.texture_settings.texture_index]
            if sel_image_texture.name in ('Viewer Node', 'Render Result'):
                display = False
        except:
            display = False
        return display


    def execute(self, context):
        D = bpy.data
        
        images = D.images
        sel_image_texture = images[context.scene.texture_settings.texture_index]
        materials = D.materials

        # to print materials with current image texture
        materials_found = context.scene.materials_found
        materials_found.clear()

        for mat in materials:
            nodes = mat.node_tree.nodes
            tex_node_type = constants.Node_Types.image_texture
            tex_nodes = node_functions.get_nodes_by_type(nodes,tex_node_type)
            
            # if texture node in current node tree
            if len(tex_nodes) > 0:
                images = [node.image for node in tex_nodes]
                if sel_image_texture in images:
                    materials_found.append(mat.name)
                    # object_functions.select_obj_by_mat(self,mat)
                    

        return {"FINISHED"}

class GTT_ScaleImageOperator(bpy.types.Operator):
    """Scale all Images on selected Material to specific resolution"""
    bl_idname = "image.scale_image"
    bl_label = "Scale Images"
    
    @classmethod
    def poll(cls, context):
        D = bpy.data
        images = D.images

        display = True
        
        # if operate on all textures is checked we don't need to get the index
        if context.scene.texture_settings.operate_on_all_textures:
            return True
        
        # image to index not found 
        try:
            sel_image_texture = images[context.scene.texture_settings.texture_index]
            if sel_image_texture.name in ('Viewer Node','Render Result'):
                display = False
        except:
            display = False
        return display

    def invoke(self,context,event):
        D = bpy.data
        
        texture_settings = context.scene.texture_settings
        image_size = [int(context.scene.img_bake_size),int(context.scene.img_bake_size)]
        
        images_in_scene = D.images
        all_images = image_functions.get_all_images_in_ui_list()

        if texture_settings.operate_on_all_textures:
            for img in all_images:
                image_functions.scale_image(img,image_size)
        else:
            sel_image_texture = images_in_scene[texture_settings.texture_index]
            image_functions.scale_image(sel_image_texture,image_size)

        return {'FINISHED'}
    
    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'PASS_THROUGH'}



class GTT_NodeToTextureOperator(bpy.types.Operator):
    """Bake all attached Textures"""
    bl_idname = "object.node_to_texture_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) < 1:
            return False
        else:
            return True

    def execute(self, context):

        # ----------------------- VAR  --------------------#
        active_object = context.object
        selected_objects = context.selected_objects
        bake_settings = context.scene.bake_settings
        texture_settings = context.scene.texture_settings

        # ----------------------- CHECK SELECTION  --------------------#

        if active_object.type != 'MESH':
            self.report({'INFO'}, 'No Mesh selected')
            return {'FINISHED'}
            
        for obj in selected_objects:
            if obj.type != 'MESH':
                obj.select_set(False)

            if len(obj.material_slots) == 0:
                self.report({'INFO'}, 'No Material on ' + obj.name)
                return {'FINISHED'}

        # ----------------------- SET VISIBLITY TO MATERIAL  --------------------#
        texture_settings.preview_bake_texture = False
    
        # ----------------------- LIGHTMAP  --------------------#
        if bake_settings.lightmap or bake_settings.ao_map:
            bake_manager.bake_texture(self,selected_objects,bake_settings)
        
            if bake_settings.show_texture_after_bake:
                texture_settings.preview_bake_texture = True
                        
            for obj in selected_objects:
                if bake_settings.ao_map:
                    obj.ao_map_name = bake_settings.bake_image_name
                if bake_settings.lightmap:
                    obj.lightmap_name = bake_settings.bake_image_name
                    
            gui_functions.update_active_element_in_bake_list()

        # ----------------------- PBR Texture --------------------#
        if bake_settings.pbr_nodes:
            bake_manager.bake_on_plane(self,selected_objects,bake_settings)

        return {'FINISHED'}

# ----------------------- VIEW OPERATORS--------------------#

class GTT_SwitchBakeMaterialOperator(bpy.types.Operator):
    """Switch to baked material"""
    bl_idname = "object.switch_bake_mat_operator"
    bl_label = "Baked Material"

    def execute(self, context):

        show_bake_material = True
        visibility_functions.switch_baked_material(show_bake_material,context.scene.affect)
        
        return {'FINISHED'}

class GTT_SwitchOrgMaterialOperator(bpy.types.Operator):
    """Switch from baked to original material"""
    bl_idname = "object.switch_org_mat_operator"
    bl_label = "Org. Material"

    def execute(self, context):

        show_bake_material = False
        visibility_functions.switch_baked_material(show_bake_material,context.scene.affect)

        return {'FINISHED'}

class GTT_PreviewBakeTextureOperator(bpy.types.Operator):
    """Connect baked texture to emission to see result"""
    bl_idname = "object.preview_bake_texture"
    bl_label = "Preview Bake Texture"
    
    connect : bpy.props.BoolProperty()
    def execute(self, context):
        context.scene.texture_settings.preview_bake_texture = self.connect
        visibility_functions.preview_bake_texture(self,context)

        return {'FINISHED'}


        
class GTT_LightmapEmissionOperator(bpy.types.Operator):
    """Connect baked Lightmap to Emission input of Principled Shader"""
    bl_idname = "object.lightmap_to_emission"
    bl_label = "Lightmap to Emission"

    connect : bpy.props.BoolProperty()
    def execute(self, context):

        visibility_functions.lightmap_to_emission(self,context,self.connect)
            

        return {'FINISHED'}

class GTT_PreviewLightmap(bpy.types.Operator):
    """Connect baked Lightmap to Base Color input of Principled Shader"""
    bl_idname = "object.preview_lightmap"
    bl_label = "Lightmap to Base Color"

    connect : bpy.props.BoolProperty()
    def execute(self, context):
        context.scene.texture_settings.preview_lightmap = self.connect
        visibility_functions.preview_lightmap(self,context)
            
        return {'FINISHED'}


# ----------------------- UV OPERATORS--------------------#

class GTT_AddUVOperator(bpy.types.Operator):
    """Add uv layer with layer name entered above"""
    bl_idname = "object.add_uv"
    bl_label = "Add UV to all selected objects"

    uv_name:bpy.props.StringProperty()

    def execute(self, context):
        sel_objects = context.selected_objects

        for obj in sel_objects:
            if obj.type != "MESH":
                continue
            uv_layers = obj.data.uv_layers
            if self.uv_name in uv_layers:
                print("UV Name already take, choose another one")
                continue
            uv_layers.new(name=self.uv_name)
            uv_layers.get(self.uv_name).active = True

        return {'FINISHED'}

class GTT_RemoveUVOperator(bpy.types.Operator):
    """Delete all uv layers found in uv_slot entered above"""
    bl_idname = "object.remove_uv"
    bl_label = "Remove UV"

    uv_slot: bpy.props.IntProperty()

    
    def execute(self, context):
        sel_objects = context.selected_objects
        self.uv_slot -= 1

        for obj in sel_objects:
            if obj.type != "MESH":
                continue
            uv_layers = obj.data.uv_layers

            if len(uv_layers) > self.uv_slot:
                uv_layers.remove(uv_layers[self.uv_slot])

        return {'FINISHED'}

class GTT_SetActiveUVOperator(bpy.types.Operator):
    """Set the acive uv to the slot entered above"""
    bl_idname = "object.set_active_uv"
    bl_label = "Set Active UV"

    uv_slot:bpy.props.IntProperty()

    def execute(self, context):
        sel_objects = context.selected_objects
        self.uv_slot -= 1

        for obj in sel_objects:
            if obj.type != "MESH":
                continue
            uv_layers = obj.data.uv_layers

            if len(uv_layers) > self.uv_slot:
                uv_layers.active_index = self.uv_slot

        return {'FINISHED'}
# ----------------------- CLEAN OPERATORS--------------------#

# class CleanBakesOperator(bpy.types.Operator):
class GTT_RemoveLightmapOperator(bpy.types.Operator):
    """Remove Lightmap and UV Node"""
    bl_idname = "material.clean_lightmap"
    bl_label = "Clean Lightmap"

    def execute(self, context):

        selected_objects = context.selected_objects
        bake_settings = context.scene.bake_settings
        all_materials = set()
        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)

        for mat in all_materials:
            if mat is None:
                continue
            node_functions.remove_node(mat,bake_settings.texture_node_lightmap)
            node_functions.remove_node(mat,"Mulitply Lightmap")
            node_functions.remove_node(mat,"Second_UV")

        #remove lightmap flag
        for obj in selected_objects:
            obj.hasLightmap = False 
            if obj.get('lightmap_name') is not None :
                del obj["lightmap_name"]
            
        return {'FINISHED'}

class GTT_RemoveAOOperator(bpy.types.Operator):
    """Remove AO Node and clear baking flags on object"""
    bl_idname = "material.clean_ao_map"
    bl_label = "Clean AO map"

    def execute(self, context):
        visibility_functions.switch_baked_material(False,"scene","_AO")
        bpy.ops.material.clean_materials()
        
        bake_settings = context.scene.bake_settings
        selected_objects = context.selected_objects
        all_materials = set()
        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)

        for mat in all_materials:
            if mat is None:
                continue
                
            node_functions.remove_node(mat,bake_settings.texture_node_ao)
            # node_functions.remove_node(mat,"Second_UV")
            node_functions.remove_node(mat,"glTF Settings")
        
        #remove flag
        for obj in selected_objects:
            if obj.get('ao_map_name') is not None :
                del obj["ao_map_name"]
            if obj.get('bake_version') is not None :
                del obj["bake_version"]
                
        return {'FINISHED'}

class GTT_CleanTexturesOperator(bpy.types.Operator):
    """Remove unreferenced images"""
    bl_idname = "image.clean_textures"
    bl_label = "Clean Textures"

    def execute(self, context):
        for image in bpy.data.images:
            if not image.users or list(image.size) == [0,0]:
                bpy.data.images.remove(image)
        return {'FINISHED'}

class GTT_CleanMaterialsOperator(bpy.types.Operator):
    """Clean materials with no users and remove empty material slots"""
    bl_idname = "material.clean_materials"
    bl_label = "Clean Materials"

    def execute(self, context):
        material_functions.clean_empty_materials()
        material_functions.clean_no_user_materials()

        return {'FINISHED'}

class GTT_CleanUnusedImagesOperator(bpy.types.Operator):
    """Clean all images from Hard Disk that are not used in scene"""
    bl_idname = "scene.clean_unused_images"
    bl_label = "Clean Images"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        images_in_folder = []
        images_in_blender = bpy.data.images         
        image_paths_in_blender = []
    
        filePath = bpy.data.filepath
        path = os.path.dirname(filePath) + "\\textures"

        # find images on hard drive
        if os.path.exists(path):
            for path, subdirs, files in os.walk(path):
                for name in files:
                    images_in_folder.append(path+"\\"+name)
        
        for img in images_in_blender:
            image_paths_in_blender.append(img.filepath)

        images_intersection = basic_functions.Intersection(image_paths_in_blender,images_in_folder)
        images_to_clean = basic_functions.Diff(images_in_folder,images_intersection)

        print("Deleting files :")
        for img in images_to_clean:
            os.remove(img)
            print(img)
        return {'FINISHED'}


# ----------------------- FILE OPERATORS--------------------#

class GTT_OpenTexturesFolderOperator(bpy.types.Operator):
    """Open Texture folder if it exists, bake or scale texture to create texture folder"""
    bl_idname = "scene.open_textures_folder"
    bl_label = "Open Folder"

    texture_path="\\textures\\"
    
    @classmethod
    def poll(self, context):
        filePath = bpy.data.filepath
        path = os.path.dirname(filePath)
        if os.path.exists(path + self.texture_path):
            return True
        return False

    def execute(self, context):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath) + self.texture_path
        
        if filepath is not "":
            subprocess.call("explorer " + directory, shell=True)
        else:
            self.report({'INFO'}, 'You need to save Blend file first !')

        return {"FINISHED"}

        


 
