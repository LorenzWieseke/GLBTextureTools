import bpy
from .constants import *
from . import functions
from .bake import Bake_On_Plane, Bake_AO
from .create_new_material import create_bake_material

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
            sel_image_texture = images[context.scene.texture_index]
            if sel_image_texture.name in ('Viewer Node', 'Render Result'):
                display = False
        except:
            display = False
        return display


    def execute(self, context):
        D = bpy.data
        
        images = D.images
        sel_image_texture = images[context.scene.texture_index]
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


class CleanTexturesOperator(bpy.types.Operator):
    bl_idname = "image.clean_textures"
    bl_label = "CleanTextures"

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
            sel_image_texture = images[context.scene.texture_index]
            if sel_image_texture.name in ('Viewer Node','Render Result'):
                display = False
        except:
            display = False
        return display

    def execute(self, context):

        C = context
        D = bpy.data

        images = D.images
        sel_image_texture = images[context.scene.texture_index]

        # get image size for baking
        imageSize = [int(C.scene.img_bake_size),int(C.scene.img_bake_size)]
        functions.scale_image(sel_image_texture,imageSize)

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

        active_object = context.object
        selected_objects = context.selected_objects
        material_slots = active_object.material_slots

          # ----------------------- CHECK SELECTION  --------------------#

        if active_object.type != 'MESH':
            self.report({'INFO'}, 'No Mesh selected')
            return {'FINISHED'}
        
        for obj in selected_objects:
            if obj.type != 'MESH':
                obj.select_set(False)

        # get selcted objects once more without all that curve and emtpy crap
        selected_objects = context.selected_objects

          # ----------------------- AO  --------------------#

        if context.scene.bake_settings.ao_map:
            Bake_AO(selected_objects)
            context.scene.toggle_ao = False

          # ----------------------- Texture --------------------#

        # for each material, set it to fake to save it und copy it with org. name + "_Bake"
        for materials in material_slots:
            material = materials.material

            if context.scene.bake_settings.pbr_nodes:
                material.use_fake_user = True

                # error checking
                check_ok = functions.check_only_one_pbr(self,material) and functions.check_is_org_material(self,material)
                if not check_ok :
                    continue
                
                Bake_On_Plane(material)

                create_bake_material(material)

                # select active object an change to baked material
                bpy.context.view_layer.objects.active = active_object
                active_object.select_set(True)
                bpy.ops.object.switch_bake_mat_op()

        return {'FINISHED'}



class BakeAllObjectsOperator(bpy.types.Operator):
    """By checking the incoming links in the PBR Shader, new Textures are generated that will include all the node transformations."""
    bl_idname = "object.bake_all_objects"
    bl_label = "Bake all Objects"

    def execute(self, context):
        materials = bpy.data.materials

        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.object

        for mat in materials:
            if "Bake" not in mat.name:
                bpy.context.view_layer.objects.active = plane
                bpy.context.active_object.active_material = mat
                bpy.ops.object.node_to_texture_operator()

        # delete plane
        bpy.data.objects.get("Plane").select_set(True)
        bpy.ops.object.delete()

        return {'FINISHED'}

class SwitchBakeMaterialOperator(bpy.types.Operator):
    """Click to switch to baked material"""
    bl_idname = "object.switch_bake_mat_op"
    bl_label = "Baked Material"

    def execute(self, context):

        active_obj = context.object
        active_mat = context.object.active_material

        all_mats = bpy.data.materials
        mat_bake = all_mats.get(active_mat.name + "_Bake") 

        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                if mat_bake is not None and slot.material is active_mat:
                    slot.material = mat_bake

        return {'FINISHED'}


class SwitchOrgMaterialOperator(bpy.types.Operator):
    """Click to switch to original material"""
    bl_idname = "object.switch_org_mat_op"
    bl_label = "Org. Material"

    def execute(self, context):

        active_obj = context.object
        active_mat = context.object.active_material

        all_mats = bpy.data.materials
        index = active_mat.name.find("_Bake")
        mat_org = all_mats.get(active_mat.name[0:index]) 

        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                mat = slot.material
                if mat_org is not None and mat_org.name in mat.name:
                    slot.material = mat_org

        return {'FINISHED'}

class AddUVOperator(bpy.types.Operator):
    """Add uv layer with layer name entered above"""
    bl_idname = "object.add_uv"
    bl_label = "Add UV"

    uv_name:bpy.props.StringProperty()

    def execute(self, context):
        sel_objects = context.selected_objects

        for obj in sel_objects:
            if obj.type != "MESH":
                continue
            uv_layers = obj.data.uv_layers
            uv_layers.new(name=self.uv_name)

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


 
