import bpy
import os
from . import functions
from .panel_ui_list import *
from .constants import *

from bpy.props import EnumProperty,BoolProperty,PointerProperty, IntProperty,StringProperty, CollectionProperty, FloatProperty

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

class UV_Settings(bpy.types.PropertyGroup):
    uv_slot: IntProperty(default=1)
    uv_name: StringProperty(default="AO")

bpy.utils.register_class(UV_Settings)
bpy.types.Scene.uv_settings = PointerProperty(type=UV_Settings)

class Cleanup_Settings(bpy.types.PropertyGroup):
    clean_texture: BoolProperty(default=True)
    clean_material: BoolProperty(default=True)
    clean_bake: BoolProperty(default=False)
    clean_node_tree: BoolProperty(default=False)

bpy.utils.register_class(Cleanup_Settings)
bpy.types.Scene.cleanup_settings = PointerProperty(type=Cleanup_Settings)

def update_pbr_button(self,context):
    self["lightmap"] = False
    self["ao_map"] = False

def update_lightmap_button(self,context):
    self["pbr_nodes"] = False
    self["ao_map"] = False

def update_ao_button(self,context):
    self["lightmap"] = False
    self["pbr_nodes"] = False

class Bake_Settings(bpy.types.PropertyGroup):  
    open_bake_settings_menu: BoolProperty(default = False)    
    open_object_bake_list_menu: BoolProperty(default = False)    
    pbr_nodes: BoolProperty(default = True,update=update_pbr_button)
    pbr_samples: IntProperty(name = "Samples for PBR bake", default = 1)
    
    ao_map: BoolProperty(default = False,update=update_ao_button)
    ao_samples: IntProperty(name = "Samples for AO bake", default = 2)

    lightmap: BoolProperty(default = False,update=update_lightmap_button)
    lightmap_samples: IntProperty(name = "Samples for Lightmap bake", default = 10)
    lightmap_list = []
    lightmap_bakes: EnumProperty(name='Baked Textures',description='List of all the Baked Textures',items=functions.update_bakes_list)
   
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
    cleanup_textures=False


bpy.utils.register_class(Bake_Settings)
bpy.types.Scene.bake_settings = PointerProperty(type=Bake_Settings)

class Texture_Settings(bpy.types.PropertyGroup):
    open_sel_mat_menu:BoolProperty(default=False)
    toggle_bake_texture:BoolProperty(default=False,update=functions.preview_bake_texture)
    texture_index:IntProperty(name = "Index for Texture List", default = 0, update=functions.set_image_in_image_editor)

bpy.utils.register_class(Texture_Settings)
bpy.types.Scene.texture_settings = PointerProperty(type=Texture_Settings)

# HELP PANEL PROPERTIES
def run_help_operator(self,context):
    bpy.ops.scene.help('INVOKE_DEFAULT')

bpy.types.Scene.help_tex_tools = BoolProperty(default=False,update=run_help_operator)

# IMAGE PROPERTIES
bpy.types.Image.org_filepath = StringProperty()
bpy.types.Image.org_image_name = StringProperty()

# MATERIAL PROPERTIES
bpy.types.Material.has_lightmap = BoolProperty()

# OBJECT PROPERTIES
bpy.types.Object.bake_texture_name = StringProperty()
              
class ResolutionPanel(bpy.types.Panel):
    bl_idname = "RESOLTUION_PT_scale_image_panel"
    bl_label = "Output Resolution"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'GLB Texture Tools'
    # bl_parent_id = "TEXTURETOOLS_PT_parent_panel"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box = layout.box()
        column = box.column()
        column.prop(scene, "img_bake_size")

        column.prop(scene,"img_file_format")
 

class BakeTexturePanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_node_to_texture_panel"
    bl_label = "Baking"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'GLB Texture Tools'
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        bake_settings = bpy.context.scene.bake_settings
    
        row = layout.row()
        row.prop(scene.bake_settings, 'open_bake_settings_menu', text="Bake Settings", icon = 'TRIA_DOWN' if bake_settings.open_bake_settings_menu else 'TRIA_RIGHT' )
        
        if bake_settings.open_bake_settings_menu:

            box = layout.box()                

            col = box.column(align = True)
            row = col.row(align = True)                       
            row.prop(scene.bake_settings, 'pbr_nodes', text="PBR",toggle = True)
            row.prop(scene.bake_settings, 'pbr_samples', text="Samples",toggle = True)    
                      
            row = col.row(align = True)     
            row.prop(scene.bake_settings, 'ao_map',  text="AO",toggle = True)
            row.prop(scene.bake_settings, 'ao_samples',  text="Samples")

            row = col.row(align = True)     
            row.prop(scene.bake_settings, 'lightmap',  text="Lightmap",toggle = True)
            row.prop(scene.bake_settings, 'lightmap_samples',  text="Samples")
            
            if bake_settings.pbr_nodes:
                col.prop(scene.bake_settings, 'mute_texture_nodes', text="Mute Texture Mapping")
                col.prop(scene.bake_settings, 'bake_image_clear', text="Clear Bake Image")


            box.prop(scene.bake_settings, 'bake_image_name',  text="Image Name")

            if bake_settings.lightmap:
                box.prop(scene.world.node_tree.nodes["Background"].inputs[1],'default_value',text="World Influence")

            if bake_settings.ao_map:
                box.prop(scene.world.light_settings,"distance",text="AO Distance")
                
            box.prop(scene.bake_settings, 'unwrap_margin', text="UV Margin")
            box.prop(scene.bake_settings, 'bake_margin', text="Bake Margin")
            
            split = box.split()
            col = split.column(align=True)
            col.prop(scene.bake_settings, 'unwrap', text="Unwrap")
            col.prop(scene.bake_settings, 'bake_image_clear', text="Clear Bake Image")

            col = split.column(align=True)
            col.prop(scene.bake_settings, 'denoise', text="Denoise")
            col.prop(scene.bake_settings, 'show_texture_after_bake', text="Show Texture after Bake")
            
        row = layout.row()
        row.prop(scene.bake_settings, 'open_object_bake_list_menu', text="Object Bake List", icon = 'TRIA_DOWN' if bake_settings.open_object_bake_list_menu else 'TRIA_RIGHT' )
        
        if bake_settings.open_object_bake_list_menu:
            box = layout.box()        
            row = box.row()
            row.prop(scene.bake_settings, 'lightmap_bakes',text="") 
            row.operator("object.select_lightmap_objects",text="",icon="RESTRICT_SELECT_OFF")
            layout.template_list("BAKE_IMAGE_UL_List", "", data, "objects", scene.bake_settings, "bake_object_index")       


        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator("object.node_to_texture_operator",text="Bake Textures")
        row.operator("scene.open_textures_folder",icon='FILEBROWSER')

        layout.label(text="Visiblity")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.switch_org_mat_operator",icon = 'NODE_MATERIAL', text="PBR Material")
        row.operator("object.switch_bake_mat_operator",icon = 'MATERIAL', text="PBR Baked Material")
        col.separator()
        row = col.row(align=True)
        row.prop(scene.texture_settings,"toggle_bake_texture", text="Show Material" if scene.texture_settings.toggle_bake_texture else "Show Baked Texture", icon="SHADING_RENDERED" if scene.texture_settings.toggle_bake_texture else "NODE_MATERIAL")


def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
        
class TextureSelectionPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_tex_selection_panel"
    bl_label = "Texture"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'GLB Texture Tools'
    # bl_parent_id = "TEXTURETOOLS_PT_parent_panel"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data

        headline(layout,(0.6,"IMAGE NAME"),(0.5,"SIZE"),(1,"KB"))
        layout.template_list("TEX_UL_List", "", data, "images", scene.texture_settings, "texture_index")
        
        layout.operator("file.unpack_all",text="Unpack")

        # Select Material by Texture
        row = layout.row()
        row.prop(scene.texture_settings,"open_sel_mat_menu",text="Select Material by Texture", icon = 'TRIA_DOWN' if scene.texture_settings.open_sel_mat_menu else 'TRIA_RIGHT' )
        if scene.texture_settings.open_sel_mat_menu:
            box = layout.box()
            col = box.column(align = True)
            col.operator("scene.select_mat_by_tex",text="Select Material",icon='RESTRICT_SELECT_OFF')
            col = box.column(align = True)
            if len(scene.materials_found) > 0:
                col.label(text="Texture found in Material :")
                for mat in scene.materials_found:
                    col.label(text=mat)
            else:
                col.label(text="Texture not used")


        # Scale and Clean
        layout.operator("image.scale_image",text="Scale Image",icon= 'FULLSCREEN_EXIT')
  
class CleanupPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_cleanup_panel"
    bl_label = "Cleanup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'GLB Texture Tools'
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = bpy.data
        
        row = layout.row()
        row.operator("image.clean_textures",text="Clean Textures",icon = 'ORPHAN_DATA')
        row.operator("material.clean_materials",text="Clean Materials",icon = 'ORPHAN_DATA')


class UVPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_UV_panel"
    bl_label = "UV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GLB Texture Tools"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        uv_settings = context.scene.uv_settings
        box = layout.box()

        row = box.row()      
        row.prop(uv_settings,"uv_name", text="UV Name")
        row.prop(uv_settings,"uv_slot", text="UV Slot")
        row = box.row()  
        row.operator("object.add_uv",text="Add UV",icon = 'ADD').uv_name = uv_settings.uv_name
        row.operator("object.remove_uv",text="Remove UV",icon = 'REMOVE').uv_slot = uv_settings.uv_slot
        row.operator("object.set_active_uv",text="Set Active",icon = 'RESTRICT_SELECT_OFF').uv_slot = uv_settings.uv_slot


class HelpPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_help_panel"
    bl_label = "Help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GLB Texture Tools"
    bl_order = 5

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.prop(scene,"help_tex_tools",text="Help",icon = 'HELP')


        
        

        
