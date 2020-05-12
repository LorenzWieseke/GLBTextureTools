import os
import subprocess
import bpy
from .constants import *
from . import functions
from .bake import Bake_On_Plane, Bake_Texture
from .create_new_material import create_bake_material
from bpy.props import EnumProperty,BoolProperty,PointerProperty, IntProperty,StringProperty

# ----------------------- LIGHTAP OPERATORS--------------------#
class SelectLightmapObjectsOperator(bpy.types.Operator):
    """Select all Objects in the list that have the according lightmap attached to them. Makes it easy to rebake multiple Objects"""
    bl_idname = "object.select_lightmap_objects"
    bl_label = "Select Lightmap Objects"
    
    @classmethod
    def poll(cls, context):
        # if len(context.scene.bake_settings.lightmap_list) > 0:
        #     return True
        # return False
        return True

    def execute(self, context):

        C = context
        D = bpy.data

        bake_settings = context.scene.bake_settings
        objects = D.objects
        bake_settings.bake_image_name = bake_settings.lightmap_bakes

        for obj in objects:
            if obj.bake_texture_name == bake_settings.lightmap_bakes:
                obj.select_set(True)

        return {'FINISHED'}

# ----------------------- TEXTURE OPERATORS--------------------#

class GetMaterialByTextureOperator(bpy.types.Operator):
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
            tex_node_type = Node_Types.image_texture
            tex_nodes = functions.find_node_by_type(nodes,tex_node_type)
            
            # if texture node in current node tree
            if len(tex_nodes) > 0:
                images = [node.image for node in tex_nodes]
                if sel_image_texture in images:
                    materials_found.append(mat.name)
                    functions.select_obj_by_mat(self,mat)
                    

        return {"FINISHED"}


class CleanBakesOperator(bpy.types.Operator):
    bl_idname = "image.clean_bakes"
    bl_label = "CleanTextures"

    def execute(self, context):
        for image in bpy.data.images:
            if not image.users or list(image.size) == [0,0]:
                bpy.data.images.remove(image)
        return {'FINISHED'}

class ScaleImageOperator(bpy.types.Operator):
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

        C = context
        D = bpy.data

        images = D.images
        sel_image_texture = images[context.scene.texture_settings.texture_index]

        # get image size for baking
        image_size = [int(C.scene.img_bake_size),int(C.scene.img_bake_size)]
        functions.scale_image(sel_image_texture,image_size)

        return {'FINISHED'}

class NodeToTextureOperator(bpy.types.Operator):
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
            Bake_Texture(selected_objects,bake_settings)
        
        if bake_settings.show_texture_after_bake:
            texture_settings.toggle_lightmap_texture = True
        
        # add image to bake image list
        item = (bake_settings.bake_image_name,bake_settings.bake_image_name,"")
        if not item in bake_settings.lightmap_list:
            bake_settings.lightmap_list.append(item)
        
        for obj in selected_objects:
            obj.bake_texture_name = bake_settings.bake_image_name

 

        # ----------------------- PBR Texture --------------------#

        # for each material, set it to fake to save it und copy it with org. name + "_Bake"
        # for materials in material_slots:
        #     material = materials.material

        if bake_settings.pbr_nodes:
            material = context.active_object.active_material
            material.use_fake_user = True

            # error checking
            check_ok = functions.check_only_one_pbr(self,material) and functions.check_is_org_material(self,material)
            if not check_ok :
                return
            
            Bake_On_Plane(material,bake_settings)

            create_bake_material(material)

            # select active object an change to baked material
            bpy.context.view_layer.objects.active = active_object
            active_object.select_set(True)
            bpy.ops.object.switch_bake_mat_operator()

        return {'FINISHED'}

# ----------------------- VIEW OPERATORS--------------------#

class SwitchBakeMaterialOperator(bpy.types.Operator):
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

class SwitchOrgMaterialOperator(bpy.types.Operator):
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

class AddUVOperator(bpy.types.Operator):
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

class RemoveUVOperator(bpy.types.Operator):
    """Delete all uv layers found in uv_slot entered above"""
    bl_idname = "object.remove_uv"
    bl_label = "Remove UV"

    uv_slot:bpy.props.IntProperty()

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

class SetActiveUVOperator(bpy.types.Operator):
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
class RemoveLightmapOperator(bpy.types.Operator):
    bl_idname = "material.remove_lightmap"
    bl_label = "Remove Lightmap"

    def execute(self, context):

        selected_objects = context.selected_objects
        all_materials = set()
        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)

        for mat in all_materials:
            functions.remove_node(mat,"Lightmap")

        #remove ligtmap flag
        for obj in selected_objects:
            obj.has_lightmap = False 
            
        return {'FINISHED'}

class RemoveAOOperator(bpy.types.Operator):
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
            functions.remove_node(mat,"AO")
            functions.remove_node(mat,"Second_UV")
            functions.remove_node(mat,"glTF Settings")

        #remove ligtmap flag
        for obj in selected_objects:
            obj.has_lightmap = False
            
        return {'FINISHED'}

class CleanTexturesOperator(bpy.types.Operator):
    bl_idname = "image.clean_textures"
    bl_label = "Clean Textures"

    def execute(self, context):
        for image in bpy.data.images:
            if not image.users or list(image.size) == [0,0]:
                bpy.data.images.remove(image)
        return {'FINISHED'}

class CleanMaterialsOperator(bpy.types.Operator):

    bl_idname = "material.clean_materials"
    bl_label = "Clean Materials"

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)

        # for obj in bpy.data.objects:
        #     functions.select_object(self,obj)
        #     bpy.ops.object.material_slot_remove_unused()
        return {'FINISHED'}

# ----------------------- FILE OPERATORS--------------------#

class OpenTexturesFolderOperator(bpy.types.Operator):
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


 
