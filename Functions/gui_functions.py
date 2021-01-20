import bpy
from . import object_functions


def update_pbr_button(self,context):
    self["lightmap"] = False
    self["ao_map"] = False

def update_lightmap_button(self,context):
    self["pbr_nodes"] = False
    self["ao_map"] = False
    object_functions.update_bake_image_name()

def update_ao_button(self,context):
    self["lightmap"] = False
    self["pbr_nodes"] = False
    object_functions.update_bake_image_name()
    
    
# ----------------------- UPDATE BAKE IMAGE NAME / ENUM--------------------#    
    
last_selection = []

def update_one_selection(scene): 
    C = bpy.context
    global last_selection
    if C.object is None:
        return

    if C.selected_objects != last_selection:
        last_selection = C.selected_objects
        update_active_element_in_bake_list()
        # update_bake_image_name()

def update_bake_list(bake_settings, context):
    
    bake_textures_set = set()

    for obj in bpy.data.objects:
        if bake_settings.lightmap:
            if obj.get("lightmap_name"):
                bake_textures_set.add((obj.lightmap_name, obj.lightmap_name, "Baked Texture Name"))
        if bake_settings.ao_map:
            if obj.get("ao_map_name"):
                bake_textures_set.add((obj.ao_map_name, obj.ao_map_name, "Baked Texture Name"))

    if len(bake_textures_set) == 0:
        bake_textures_set.add((" "," ","No Lightmap baked yet"))


    return list(bake_textures_set)


def update_active_element_in_bake_list():
    C = bpy.context
    active_object = C.active_object
    bake_settings = C.scene.bake_settings
    bake_image_name = ""
    
    if bake_settings.lightmap:
        bake_image_name = active_object.get("lightmap_name")
    if bake_settings.ao_map:
        bake_image_name = active_object.get("ao_map_name")
    if bake_image_name is None:
        bake_image_name = "New Name"
    
    bake_settings.bake_image_name = bake_image_name
    bake_settings.lightmap_bakes = bake_image_name
    

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
        
        
 # TODO check this out later        

# last_selection = []

# def update_one_selection(scene): 
#     C = bpy.context
#     global last_selection
#     if C.selected_objects != last_selection and C.object.type == "MESH":
#         last_selection = C.selected_objects
#         update_bake_image_name()
#         update_bake_list()

# def update_bake_list():
#     C = bpy.context
#     bake_settings = C.scene.bake_settings
#     bake_image_name = bake_settings.bake_image_name
#     lightmap_bakes = bake_settings.lightmap_bakes
#     # if bake_image_name in lightmap_bakes.enum_items:
#     try:
#         bake_settings.lightmap_bakes = bake_settings.bake_image_name
#     except:
#         pass
       

# def update_bake_image_name():
#     C = bpy.context

#     active_mat = C.object.active_material

#     if active_mat is None:
#         return

#     bake_settings = C.scene.bake_settings
#     nodes = active_mat.node_tree.nodes

#     image_name = "New Name"
#     if bake_settings.lightmap:
#         if nodes.get(bake_settings.texture_node_lightmap):
#             image_name = nodes.get(bake_settings.texture_node_lightmap).image.name
#     if bake_settings.ao_map:
#         if nodes.get(bake_settings.texture_node_ao):
#             image_name = nodes.get(bake_settings.texture_node_ao).image.name

#     bake_settings.bake_image_name = image_name