import bpy
from .. Functions import node_functions


last_selection = []

def update_one_selection(scene): 
    C = bpy.context
    global last_selection
    if bpy.context.selected_objects != last_selection:
        last_selection = C.selected_objects
        update_bake_image_name()
       

def update_bake_image_name():
    C = bpy.context

    active_mat = C.object.active_material
    bake_settings = C.scene.bake_settings
    nodes = active_mat.node_tree.nodes

    image_name = "New Name"
    if bake_settings.lightmap:
        if nodes.get(bake_settings.texture_node_lightmap):
            image_name = nodes.get(bake_settings.texture_node_lightmap).image.name
    if bake_settings.ao_map:
        if nodes.get(bake_settings.texture_node_ao):
            image_name = nodes.get(bake_settings.texture_node_ao).image.name

    #cleanup
    if image_name == "New Name":
        del C.object["bake_texture_name"]

    bake_settings.bake_image_name = image_name

bpy.app.handlers.depsgraph_update_post.clear()
bpy.app.handlers.depsgraph_update_post.append(update_one_selection)

def select_object(self, obj):
    C = bpy.context
    try:
        O.object.select_all(action='DESELECT')
        C.view_layer.objects.active = obj
        obj.select_set(True)
    except:
        self.report({'INFO'}, "Object not in View Layer")

def select_obj_by_mat(self, mat):
    D = bpy.data
    for obj in D.objects:
        if obj.type == "MESH":
            object_materials = [
                slot.material for slot in obj.material_slots]
            if mat in object_materials:
                select_object(self, obj)

# todo - save objects in array, unlink objects, apply scale and link them back
def apply_scale_on_multiuser():
    O = bpy.ops
    O.object.transform_apply(location=False, rotation=False, scale=True)