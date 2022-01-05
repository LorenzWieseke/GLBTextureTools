import bpy
from ..Bake import bake_manager
from .. Functions import gui_functions


class GTT_BakeOperator(bpy.types.Operator):
    """Bake all attached Textures"""
    bl_idname = "object.gtt_bake_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) < 1:
            return False
        else:
            return True
        
    def deselect_everything_but_mesh(self,selected_objects):
        for obj in selected_objects:
            if obj.type != 'MESH':
                obj.select_set(False)

        
    def execute(self,context):

        # ----------------------- VAR  --------------------#
        active_object = context.object
        selected_objects = context.selected_objects
        bake_settings = context.scene.bake_settings
        texture_settings = context.scene.texture_settings
        self.deselect_everything_but_mesh(selected_objects)

        # ----------------------- CHECK SELECTION  --------------------#

        if len(selected_objects) > 0:
            active_object = selected_objects[0]
            
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
    
        # ----------------------- LIGHTMAP / AO --------------------#
        if bake_settings.lightmap_bake or bake_settings.ao_bake:
            bake_manager.bake_texture(self,selected_objects,bake_settings)
        
            if bake_settings.show_texture_after_bake and bake_settings.denoise:
                texture_settings.preview_bake_texture = True
                        
            for obj in selected_objects:
                if bake_settings.ao_bake:
                    obj.ao_map_name = bake_settings.bake_image_name
                if bake_settings.lightmap_bake:
                    obj.lightmap_name = bake_settings.bake_image_name
                    
            gui_functions.update_active_element_in_bake_list()

        # ----------------------- PBR Texture --------------------#
        if bake_settings.pbr_bake:
            bake_manager.bake_on_plane(self,selected_objects,bake_settings)

        
        return {'FINISHED'}
        
 


