import os
import subprocess
import bpy
# from bpy.props import *

from .. Functions import node_functions
from .. Functions import image_functions
from .. Functions import object_functions
from .. Bake import bake_utilities
from .. Bake import bake_manager
from .. Functions import constants


# ----------------------- LIGHTAP OPERATORS--------------------#
class GTT_SelectLightmapObjectsOperator(bpy.types.Operator):
    """Select all Objects in the list that have the according lightmap attached to them. Makes it easy to rebake multiple Objects"""
    bl_idname = "object.select_lightmap_objects"
    bl_label = "Select Lightmap Objects"
    
    @classmethod
    def poll(cls, context):
        if context.scene.bake_settings.lightmap_bakes == '':
            return False
        return True

    def execute(self, context):

        C = context
        D = bpy.data
        O = bpy.ops

        bake_settings = C.scene.bake_settings
        objects = D.objects
        bake_settings.bake_image_name = bake_settings.lightmap_bakes

        O.object.select_all(action='DESELECT')
        for obj in objects:
            if obj.bake_texture_name == bake_settings.lightmap_bakes:
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
            tex_nodes = node_functions.get_node_by_type(nodes,tex_node_type)
            
            # if texture node in current node tree
            if len(tex_nodes) > 0:
                images = [node.image for node in tex_nodes]
                if sel_image_texture in images:
                    materials_found.append(mat.name)
                    object_functions.select_obj_by_mat(self,mat)
                    

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

        # image to index not found 
        try:
            sel_image_texture = images[context.scene.texture_settings.texture_index]
            if sel_image_texture.name in ('Viewer Node','Render Result'):
                display = False
        except:
            display = False
        return display

    def execute(self, context):
        D = bpy.data
        
        selected_objects = context.selected_objects
        texture_settings = context.scene.texture_settings
        image_size = [int(context.scene.img_bake_size),int(context.scene.img_bake_size)]
        

        images = D.images
        sel_image_texture = images[texture_settings.texture_index]
        all_images = image_functions.get_all_images_in_selected_objects(selected_objects)

        if texture_settings.operate_on_all_textures:
            for img in all_images:
                image_functions.scale_image(img,image_size)
        else:
            image_functions.scale_image(sel_image_texture,image_size)

        return {'FINISHED'}

class GTT_NodeToTextureOperator(bpy.types.Operator):
    """Bake all attached Textures"""
    bl_idname = "object.node_to_texture_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        return True

    def execute(self, context):

        # ----------------------- VAR  --------------------#
        active_object = context.object
        selected_objects = context.selected_objects

        # get selcted objects once more without all that curve and emtpy crap
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
        texture_settings.toggle_lightmap_texture = False
    
        # ----------------------- LIGHTMAP  --------------------#
        if bake_settings.lightmap or bake_settings.ao_map:
            bake_manager.bake_texture(self,selected_objects,bake_settings)
        
            if bake_settings.show_texture_after_bake:
                texture_settings.toggle_lightmap_texture = True
                        
            for obj in selected_objects:
                obj.bake_texture_name = bake_settings.bake_image_name

        # ----------------------- PBR Texture --------------------#
        if bake_settings.pbr_nodes:
            selected_objects = context.selected_objects            
            bake_manager.bake_on_plane(self,selected_objects,bake_settings)

        return {'FINISHED'}

# ----------------------- VIEW OPERATORS--------------------#

class GTT_SwitchBakeMaterialOperator(bpy.types.Operator):
    """Click to switch to baked material"""
    bl_idname = "object.switch_bake_mat_operator"
    bl_label = "PBR Baked Material"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.type == 'MESH' and
        context.object.active_material is not None and "_Bake" not in context.object.active_material.name)

    def execute(self, context):

        active_obj = context.object
        active_mat = context.object.active_material

        all_mats = bpy.data.materials
        mat_bake = all_mats.get(active_mat.name + "_Bake") 
        
        # for obj in bpy.data.objects:
        for slot in active_obj.material_slots:
            if mat_bake is not None and slot.material is active_mat:
                slot.material = mat_bake
            else:
                self.report({'INFO'}, 'Bake PBR textures first')

        return {'FINISHED'}

class GTT_SwitchOrgMaterialOperator(bpy.types.Operator):
    """Click to switch to original material"""
    bl_idname = "object.switch_org_mat_operator"
    bl_label = "Org. Material"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.type == 'MESH' and
        context.object.active_material is not None and "_Bake" in context.object.active_material.name)

    def execute(self, context):

        active_obj = context.object
        active_mat = context.object.active_material

        all_mats = bpy.data.materials
        index = active_mat.name.find("_Bake")
        mat_org = all_mats.get(active_mat.name[0:index]) 

        # for obj in bpy.data.objects:
        for slot in active_obj.material_slots:
            mat = slot.material
            if mat_org is not None and mat_org.name in mat.name:
                slot.material = mat_org

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
    bl_idname = "material.remove_lightmap"
    bl_label = "Remove Lightmap"

    def execute(self, context):

        selected_objects = context.selected_objects
        bake_settings = context.scene.bake_settings
        all_materials = set()
        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)

        for mat in all_materials:
            node_functions.remove_node(mat,bake_settings.texture_node_lightmap)

        #remove ligtmap flag
        for obj in selected_objects:
            obj.has_lightmap = False 
            
        return {'FINISHED'}

class GTT_RemoveAOOperator(bpy.types.Operator):
    bl_idname = "material.remove_ao_map"
    bl_label = "Remove AO map"

    def execute(self, context):
        bake_settings = context.scene.bake_settings
        selected_objects = context.selected_objects
        all_materials = set()
        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)

        for mat in all_materials:
            node_functions.remove_node(mat,bake_settings.texture_node_ao)
            node_functions.remove_node(mat,"Second_UV")
            node_functions.remove_node(mat,"glTF Settings")
            
        return {'FINISHED'}

class GTT_CleanTexturesOperator(bpy.types.Operator):
    bl_idname = "image.clean_textures"
    bl_label = "Clean Textures"

    def execute(self, context):
        for image in bpy.data.images:
            if not image.users or list(image.size) == [0,0]:
                bpy.data.images.remove(image)
        return {'FINISHED'}

class GTT_CleanMaterialsOperator(bpy.types.Operator):

    bl_idname = "material.clean_materials"
    bl_label = "Clean Materials"

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)

        return {'FINISHED'}

# ----------------------- FILE OPERATORS--------------------#

class GTT_OpenTexturesFolderOperator(bpy.types.Operator):
    bl_idname = "scene.open_textures_folder"
    bl_label = "Open Folder"
    bl_description = "Open Texture folder if it exists, bake or scale texture to create texture folder"

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


 
