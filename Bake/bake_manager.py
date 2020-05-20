import bpy
from . import bake_utilities

from .. Functions import constants
from .. Functions import visibility_functions


def bake_texture(self, selected_objects, bake_settings):
    parent_operator = self
    # ----------------------- CREATE INSTANCE --------------------#
    ligthmap_utilities = bake_utilities.BakeUtilities(parent_operator, selected_objects, bake_settings)  

    # -----------------------SETUP UV'S--------------------#
    ligthmap_utilities.unwrap_selected()

    # -----------------------SETUP ENGINE--------------------#
    ligthmap_utilities.setup_engine()

    # -----------------------SETUP NODES--------------------#
    ligthmap_utilities.add_node_setup()
    
    # ----------------------- BAKING --------------------#
    if bake_settings.lightmap:
        ligthmap_utilities.save_metal_value()
        ligthmap_utilities.bake(constants.Bake_Types.lightmap)
        ligthmap_utilities.load_metal_value()
    
    if bake_settings.ao_map:
        ligthmap_utilities.bake(constants.Bake_Types.ao)

    ligthmap_utilities.add_lightmap_flag()
    ligthmap_utilities.cleanup()


    
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
