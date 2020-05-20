import bpy
from . import node_functions
from . import constants

def show_selected_image_in_image_editor(self,context):
    sel_texture = bpy.data.images[self.texture_index]
    show_image_in_image_editor(sel_texture)
    
def show_image_in_image_editor(image):
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = image

def preview_bake_material():
    C = bpy.context
    
    active_obj = C.active_object
    active_mat = C.active_object.active_material

    all_mats = bpy.data.materials
    mat_bake = all_mats.get(active_mat.name + "_Bake") 
    
    # for obj in bpy.data.objects:
    for slot in active_obj.material_slots:
        if mat_bake is not None and slot.material is active_mat:
            slot.material = mat_bake

def preview_bake_texture(self, context):
    all_materials = bpy.data.materials
    bake_settings = context.scene.bake_settings
    toggle_lightmap_texture = context.scene.texture_settings.toggle_lightmap_texture
    for mat in all_materials:
        nodes = mat.node_tree.nodes

        if bake_settings.lightmap:
            bake_texture_node = nodes.get(bake_settings.texture_node_lightmap)

        if bake_settings.ao_map:
            bake_texture_node = nodes.get(bake_settings.texture_node_ao)
       
        if bake_texture_node is not None:
            if toggle_lightmap_texture:
                node_functions.emission_setup(mat, bake_texture_node.outputs["Color"])
            else:
                pbr_node = node_functions.find_node_by_type(nodes, constants.Node_Types.pbr_node)[0]
                node_functions.remove_node(mat, "Emission Bake")
                node_functions.reconnect_PBR(mat, pbr_node)