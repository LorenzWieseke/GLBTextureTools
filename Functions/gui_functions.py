import bpy
from . import object_functions

def update_pbr_button(self,context):
    self["lightmap"] = False
    self["ao_map"] = False

def update_lightmap_button(self,context):
    self["pbr_nodes"] = False
    self["ao_map"] = False
    object_functions.update_bake_image_name()
    # self["bake_image_name"] = "Lightmap"

def update_ao_button(self,context):
    self["lightmap"] = False
    self["pbr_nodes"] = False
    object_functions.update_bake_image_name()
    # self["bake_image_name"] = "AO"

def update_bakes_list(bake_settings, context):
    bake_textures_set = set()

    # bake_textures_set = bake_settings.lightmap_list
    for obj in bpy.data.objects:
        if obj.ligthmap_name:
            bake_textures_set.add((obj.ligthmap_name, obj.ligthmap_name, "Baked Texture Name"))

    return list(bake_textures_set)