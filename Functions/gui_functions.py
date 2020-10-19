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

def update_bakes_list(bake_settings, context):
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

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])