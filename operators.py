import bpy
from .constants import *
from .functions import *
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
            tex_nodes = find_node_by_type(nodes,tex_node_type)
            
            # if texture node in current node tree
            if len(tex_nodes) > 0:
                images = [node.image for node in tex_nodes]
                if sel_image_texture in images:
                    materials_found.append(mat.name)
                    select_obj_by_mat(self,mat)
                    

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
        scale_image(sel_image_texture,imageSize)

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
                check_ok = check_only_one_pbr(self,material) and check_is_org_material(self,material)
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
        mats = bpy.data.materials

        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                mat = slot.material
                matBake = mats.get(mat.name + "_Bake")
                if matBake is not None:
                    slot.material = matBake

        return {'FINISHED'}


class SwitchOrgMaterialOperator(bpy.types.Operator):
    """Click to switch to original material"""
    bl_idname = "object.switch_org_mat_op"
    bl_label = "Org. Material"

    def execute(self, context):

        mats = bpy.data.materials

        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                matBake = slot.material
                if "_Bake" in matBake.name:
                    index = matBake.name.find("_Bake")
                    orgMatName = matBake.name[0:index]

                    orgMat = mats.get(orgMatName)
                    if orgMat is not None:
                        slot.material = orgMat

        return {'FINISHED'}

# class ShowAOOperator(bpy.types.Operator):
#     bl_idname = "scene.show_ao"
#     bl_label = "Show AO"
#     bl_description = "Switch all Materials to Show AO"
#     bl_options = {"REGISTER"}

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):
       

        
#         return {"FINISHED"}




 
