import bpy
from . import bake_utilities

from .. Functions import constants
from .. Functions import visibility_functions


def bake_texture(self, selected_objects, bake_settings):
    parent_operator = self
    # ----------------------- CREATE INSTANCE --------------------#
    lightmap_utilities = bake_utilities.BakeUtilities(parent_operator, selected_objects, bake_settings)  

    
    # -----------------------SET LIGHTMAP UV--------------------#
    lightmap_utilities.set_active_uv_to_lightmap()
    
    # -----------------------SETUP UV'S--------------------#
    lightmap_utilities.unwrap_selected()

    # -----------------------SETUP ENGINE--------------------#
    lightmap_utilities.setup_engine()

    # -----------------------SWITCH BACK TO SHOW ORG MATERIAL --------------------#
    visibility_functions.preview_bake_texture(self,context=bpy.context)
    
    # ----------------------- CREATE NEW MATERIAL FOR BAKING --------------------#
    lightmap_utilities.create_bake_material("_AO")
     
    # -----------------------SETUP NODES--------------------#
    lightmap_utilities.add_node_setup()
        
    # ----------------------- BAKING --------------------#
    if bake_settings.lightmap:
        # bpy.ops.material.clean_lightmap()
        visibility_functions.preview_lightmap(self,bpy.context)
        lightmap_utilities.save_metal_value()
        lightmap_utilities.bake(constants.Bake_Types.lightmap)
        lightmap_utilities.load_metal_value()
        lightmap_utilities.add_lightmap_flag()
    
    if bake_settings.ao_map:
        lightmap_utilities.bake(constants.Bake_Types.ao)

    lightmap_utilities.cleanup()
    return


def bake_on_plane(self,selected_objects,bake_settings):

    parent_operator = self
    
    for active_object in selected_objects:

        # ----------------------- CREATE INSTANCE --------------------#
        pbr_utilities = bake_utilities.PbrBakeUtilities(parent_operator,active_object,bake_settings)

        # -----------------------TESTING--------------------#
        if not pbr_utilities.ready_for_bake():
            return
        # -----------------------SETUP ENGINE--------------------#

        pbr_utilities.setup_engine()

        # -----------------------SETUP BAKE PLANE--------------------#
        
        pbr_utilities.bake_materials_on_object()
        
        # pbr_utilities.add_bake_plane()

        # pbr_utilities.bake_pbr()

        # pbr_utilities.create_pbr_bake_material("_Bake")
        
        # pbr_utilities.create_nodes_after_pbr_bake()
        
        # if not bake_settings.bake_all_materials:
            
        #     pbr_utilities.preview_bake_material()

        # pbr_utilities.cleanup_nodes()

    return
