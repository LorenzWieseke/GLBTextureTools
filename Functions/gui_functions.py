import bpy
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

def update_bake_list(bake_settings,context):
    
    bake_textures_set = set()

    for obj in bpy.data.objects:
        if bake_settings.lightmap:
            if obj.get("lightmap_name"):
                bake_textures_set.add((obj.lightmap_name, obj.lightmap_name, "Baked Texture Name"))
        if bake_settings.ao_map:
            if obj.get("ao_map_name"):
                bake_textures_set.add((obj.ao_map_name, obj.ao_map_name, "Baked Texture Name"))

    if len(bake_textures_set) == 0:
        bake_textures_set.add(("-- Baking Groups --","-- Baking Groups --","No Lightmap baked yet"))

    return list(bake_textures_set)


def update_active_element_in_bake_list():
    C = bpy.context
    active_object = C.active_object
    bake_settings = C.scene.bake_settings
    new_bake_image_name = ""
    
    if bake_settings.lightmap:
        new_bake_image_name = active_object.get("lightmap_name")
        if new_bake_image_name is None:
            new_bake_image_name = "Lightmap " + active_object.name
    if bake_settings.ao_map:
        new_bake_image_name = active_object.get("ao_map_name")
        if new_bake_image_name is None:
            new_bake_image_name = "AO " + active_object.name
            
    enum_items = bake_settings.get_baked_lightmaps()
    keys = [key[0] for key in enum_items]
    if new_bake_image_name in keys:
        bake_settings.bake_image_name = new_bake_image_name
        bake_settings.baking_groups = new_bake_image_name
    else:
        if active_object.type == "MESH":
            bake_settings.bake_image_name = new_bake_image_name
            bake_settings.baking_groups = "-- Baking Groups --"
   

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
        
@persistent
def init_values(self,context):
    bpy.context.scene.world.light_settings.distance = 1