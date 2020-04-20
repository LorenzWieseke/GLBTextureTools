import bpy
import os
from . import functions
from .constants import *

from bpy.props import EnumProperty,BoolProperty,PointerProperty, IntProperty,StringProperty

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

class Bake_Settings(bpy.types.PropertyGroup):  
    open_bake_settings_menu: BoolProperty(default = False)    
    mute_texture_nodes: BoolProperty(default = True)
    pbr_nodes: BoolProperty(default = True)
    pbr_samples: IntProperty(name = "Samples for PBR bake", default = 1)
    ao_map: BoolProperty(default = False)
    ao_map_name: StringProperty(default="AO")
    ao_samples: IntProperty(name = "Samples for AO bake", default = 2)
    ao_use_clear: BoolProperty(default= True)

bpy.utils.register_class(Bake_Settings)

def run_help_operator(self,context):
    bpy.ops.scene.help('INVOKE_DEFAULT')


# HELP PANEL PROPERTIES
bpy.types.Scene.help_tex_tools = BoolProperty(default=False,update=run_help_operator)

# TEXTURE PANEL PROPERTIES
bpy.types.Scene.open_sel_mat_menu = BoolProperty(default=False)
bpy.types.Scene.need_unpack = BoolProperty(default=False)
bpy.types.Scene.toggle_ao = BoolProperty(default=False,update=functions.apply_ao_toggle)
bpy.types.Scene.bake_settings = PointerProperty(type=Bake_Settings)
bpy.types.Scene.texture_index = IntProperty(name = "Index for Texture List", default = 0, update=functions.set_image_in_image_editor)

# UV PROPERTIES
bpy.types.Scene.uv_settings = PointerProperty(type=UV_Settings)

# IMAGE PROPERTIES
bpy.types.Image.org_filepath = StringProperty()
bpy.types.Image.org_image_name = StringProperty()



def clearConsole():
    print("console cleared")
    os.system('cls')

clearConsole()
              
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
 

class NodeToTexturePanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_node_to_texture_panel"
    bl_label = "Baking"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'GLB Texture Tools'
    # bl_parent_id = "TEXTURETOOLS_PT_parent_panel"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
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

            box.prop(scene.bake_settings, 'ao_map_name',  text="Image Name",toggle = True)
            box.prop(scene.bake_settings, 'mute_texture_nodes', text="Mute Texture Mapping")
            box.prop(scene.bake_settings, 'ao_use_clear', text="Clear Bake Image")
            
        layout.operator("object.node_to_texture_operator",text="Bake Textures")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.switch_org_mat_op",icon = 'NODE_MATERIAL')
        row.operator("object.switch_bake_mat_op",icon = 'MATERIAL' )
        row = col.row(align=True)
        row.prop(scene,"toggle_ao", text="Show Material" if scene.toggle_ao else "Show AO", icon="SHADING_RENDERED" if scene.toggle_ao else "NODE_MATERIAL")


class TEX_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()

            split = row.split(factor=0.6)
            split.label(text=str(item.users) + " " +item.name)
            
            split = split.split(factor=0.5)
            split.label(text=str(item.size[0]))

            split = split.split(factor=1)
            
            filepath = item.filepath
            if filepath != '':
                filesize = functions.get_file_size(filepath)
                split.label(text=str(filesize).split('.')[0])
            else:
                split.label(text="file not saved")

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        object_list = objects.items()
        img_names = [obj[0] for obj in object_list]

        # Default return values.
        flt_flags = []
        flt_neworder = []
        images = []
        try:
            active_mat = context.active_object.active_material
            if active_mat is not None:
                nodes = active_mat.node_tree.nodes
                tex_nodes = functions.find_node_by_type(nodes,Node_Types.image_texture)
                images = [node.image.name for node in tex_nodes]
            else:
                images = [image.name for image in bpy.data.images if image.name not in ('Viewer Node','Render Result')]
        except:
            pass
    
        flt_flags = [self.bitflag_filter_item if name in images else 0 for name in img_names]

        return flt_flags, flt_neworder

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
        layout.template_list("TEX_UL_List", "", data, "images", scene, "texture_index")
        
        layout.operator("file.unpack_all",text="Unpack")

        # Select Material by Texture
        row = layout.row()
        row.prop(scene,"open_sel_mat_menu",text="Select Material by Texture", icon = 'TRIA_DOWN' if scene.open_sel_mat_menu else 'TRIA_RIGHT' )
        if scene.open_sel_mat_menu:
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
        row = layout.row()
        row.operator("image.clean_textures",text="Clean Textures",icon = 'ORPHAN_DATA')
        row.operator("material.clean_materials",text="Clean Materials",icon = 'ORPHAN_DATA')

class UVPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_UV_panel"
    bl_label = "UV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GLB Texture Tools"
    bl_order = 3

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
    bl_order = 4

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.prop(scene,"help_tex_tools",text="Help",icon = 'HELP')


        
        

        
