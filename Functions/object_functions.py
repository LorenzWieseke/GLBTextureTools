import bpy
from .. Functions import node_functions


last_selection = []

def update_one_selection(scene): 
    C = bpy.context
    global last_selection
    if C.object is None:
        return
    if C.object.get('hasLightmap') is None:
        return

    if C.selected_objects != last_selection:
        last_selection = C.selected_objects
        update_bake_image_name()
        update_bake_list()

def update_bake_list():
    C = bpy.context
    bake_settings = C.scene.bake_settings
    # bake_image_name = bake_settings.bake_image_name
    # lightmap_bakes = bake_settings.lightmap_bakes
    # if bake_image_name in lightmap_bakes.enum_items:
    try:
        bake_settings.lightmap_bakes = bake_settings.bake_image_name
    except:
        pass
       

def update_bake_image_name():
    C = bpy.context

    active_mat = C.object.active_material

    if active_mat is None:
        return

    bake_settings = C.scene.bake_settings
    nodes = active_mat.node_tree.nodes

    image_name = "New Name"
    if bake_settings.lightmap:
        if nodes.get(bake_settings.texture_node_lightmap):
            image_name = nodes.get(bake_settings.texture_node_lightmap).image.name
    if bake_settings.ao_map:
        if nodes.get(bake_settings.texture_node_ao):
            image_name = nodes.get(bake_settings.texture_node_ao).image.name

    bake_settings.bake_image_name = image_name

def apply_transform_on_linked():    
    bpy.ops.object.select_linked(type='OBDATA')
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.make_links_data(type='OBDATA')

def select_object(self, obj):
    C = bpy.context
    O = bpy.ops
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
            object_materials = [slot.material for slot in obj.material_slots]
            if mat in object_materials:
                select_object(self, obj)

# todo - save objects in array, unlink objects, apply scale and link them back
def apply_scale_on_multiuser():
    O = bpy.ops
    O.object.transform_apply(location=False, rotation=False, scale=True)