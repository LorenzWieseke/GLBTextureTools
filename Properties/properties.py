import bpy
from bpy.props import *
from .. Functions import gui_functions
from .. Functions import visibility_functions

bpy.types.Scene.img_bake_size = EnumProperty(
    name='Size',
    description='Set Resolution for Baking',
    default='1024',
    items=[
         ('128', '128', 'Set image size to 128'),
        ('256', '256', 'Set image size to 256'),
        ('512', '512', 'Set image size to 512'),
        ('1024', '1024', 'Set image size to 1024'),
        ('2048', '2048', 'Set image size to 2048'),
        ('4096', '4096', 'Set image size to 4096'),
        ('0', 'Original', 'Set image back to original File'),
    ])

bpy.types.Scene.img_file_format = EnumProperty(
    name='File Format',
    description='Set file format for output image',
    default='PNG',
    items=[
         ('JPEG', 'JPEG', 'Set image format to jpg'),
        ('PNG', 'PNG', 'Set image format to jpg'),
    ])

class GTT_UV_Settings(bpy.types.PropertyGroup):
    uv_slot: IntProperty(default=1)
    uv_name: StringProperty(default="AO")

bpy.utils.register_class(GTT_UV_Settings)
bpy.types.Scene.uv_settings = PointerProperty(type=GTT_UV_Settings)

class GTT_Cleanup_Settings(bpy.types.PropertyGroup):
    clean_texture: BoolProperty(default=True)
    clean_material: BoolProperty(default=True)
    clean_bake: BoolProperty(default=False)
    clean_node_tree: BoolProperty(default=False)

bpy.utils.register_class(GTT_Cleanup_Settings)
bpy.types.Scene.cleanup_settings = PointerProperty(type=GTT_Cleanup_Settings)

class GTT_Bake_Settings(bpy.types.PropertyGroup):  
    open_bake_settings_menu: BoolProperty(default = False)    
    open_object_bake_list_menu: BoolProperty(default = False)    
    pbr_nodes: BoolProperty(default = True,update=gui_functions.update_pbr_button)
    pbr_samples: IntProperty(name = "Samples for PBR bake", default = 1)
    
    ao_map: BoolProperty(default = False,update=gui_functions.update_ao_button)
    ao_samples: IntProperty(name = "Samples for AO bake", default = 2)

    lightmap: BoolProperty(default = False,update=gui_functions.update_lightmap_button)
    lightmap_samples: IntProperty(name = "Samples for Lightmap bake", default = 10)

    lightmap_bakes: EnumProperty(name='Baked Textures',description='List of all the Baked Textures',items=gui_functions.update_bakes_list)
   
    bake_image_name: StringProperty(default="Lightmap")
    bake_image_clear: BoolProperty(default= True)
    mute_texture_nodes: BoolProperty(default = True)
    bake_margin:IntProperty(default=2)
    unwrap_margin:FloatProperty(default=0.08)
    unwrap: BoolProperty(default= True)
    denoise: BoolProperty(default=True)
    show_texture_after_bake: BoolProperty(default=True)
    bake_object_index:IntProperty(name = "Index for baked Objects", default = 0)

    uv_name="Lightmap"
    texture_node_lightmap="Lightmap"
    texture_node_ao="AO"
    cleanup_textures=False


bpy.utils.register_class(GTT_Bake_Settings)
bpy.types.Scene.bake_settings = PointerProperty(type=GTT_Bake_Settings)

class GTT_Texture_Settings(bpy.types.PropertyGroup):
    open_texture_settings_menu:BoolProperty(default=False)
    open_sel_mat_menu:BoolProperty(default=False)
    show_all_textures:BoolProperty(default=False)
    operate_on_all_textures:BoolProperty(default=False)

    toggle_lightmap_texture:BoolProperty(default=False,update=visibility_functions.preview_bake_texture)
    texture_index:IntProperty(name = "Index for Texture List", default = 0, update=visibility_functions.show_selected_image_in_image_editor)

bpy.utils.register_class(GTT_Texture_Settings)
bpy.types.Scene.texture_settings = PointerProperty(type=GTT_Texture_Settings)

# HELP PANEL PROPERTIES
def run_help_operator(self,context):
    bpy.ops.scene.help('INVOKE_DEFAULT')

bpy.types.Scene.help_tex_tools = BoolProperty(default=False,update=run_help_operator)

# IMAGE PROPERTIES
bpy.types.Image.org_filepath = StringProperty()
bpy.types.Image.org_image_name = StringProperty()

# OBJECT PROPERTIES
bpy.types.Object.has_lightmap = BoolProperty()
bpy.types.Object.bake_texture_name = StringProperty()
