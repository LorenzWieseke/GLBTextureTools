import bpy
from . import object_functions
from bpy.app.handlers import persistent


def update_pbr_button(self,context):
    self["lightmap"] = False
    self["ao_map"] = False

def update_lightmap_button(self,context):
    self["pbr_nodes"] = False
    self["ao_map"] = False
    update_active_element_in_bake_list()

def update_ao_button(self,context):
    self["lightmap"] = False
    self["pbr_nodes"] = False
    update_active_element_in_bake_list()
    
    
# ----------------------- UPDATE BAKE IMAGE NAME / ENUM--------------------#    
    
last_selection = []

@persistent
def update_on_selection(scene): 
    C = bpy.context
    global last_selection
    if C.object is None:
        return

    if C.selected_objects != last_selection:
        last_selection = C.selected_objects
        update_active_element_in_bake_list()

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

    if bake_image_name is not "" and bake_image_name is not "New Name":
        bake_settings.bake_image_name = bake_image_name
        bake_settings.lightmap_bakes = bake_image_name
    

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
        