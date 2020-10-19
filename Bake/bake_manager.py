import bpy
from . import bake_utilities

from .. Functions import constants
from .. Functions import visibility_functions


def bake_texture(self, selected_objects, bake_settings):
    parent_operator = self
    # ----------------------- CREATE INSTANCE --------------------#
    lightmap_utilities = bake_utilities.BakeUtilities(parent_operator, selected_objects, bake_settings)  

    # -----------------------SET UV--------------------#
    lightmap_utilities.set_active_uv_to_lightmap()
    
    # -----------------------SETUP UV'S--------------------#
    lightmap_utilities.unwrap_selected()

    # -----------------------SETUP ENGINE--------------------#
    lightmap_utilities.setup_engine()

    # -----------------------CANGE PREVIEW MODE --------------------#
    bpy.ops.object.preview_bake_texture()
    
    # -----------------------CLEAN PREV LIGHTMAP --------------------#
    bpy.ops.material.remove_lightmap()

    # -----------------------SETUP NODES--------------------#
    lightmap_utilities.add_node_setup()
    
    # ----------------------- BAKING --------------------#
    if bake_settings.lightmap:
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

    # ----------------------- CREATE INSTANCE --------------------#
    pbr_utilities = bake_utilities.PbrBakeUtilities(parent_operator,selected_objects,bake_settings)

    # -----------------------TESTING--------------------#
    if not pbr_utilities.ready_for_bake():
        return
    # -----------------------SETUP ENGINE--------------------#

    pbr_utilities.setup_engine()

    # -----------------------SETUP BAKE PLANE--------------------#
    pbr_utilities.add_bake_plane()

    pbr_utilities.bake_pbr()

    pbr_utilities.create_bake_material()

    pbr_utilities.preview_bake_material()

    pbr_utilities.cleanup_nodes()

    return
