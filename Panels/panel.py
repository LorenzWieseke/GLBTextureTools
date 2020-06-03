import bpy
import os
from . import panel_ui_list
from .. Update import addon_updater_ops

              
class GTT_ResolutionPanel(bpy.types.Panel):
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
 

class GTT_BakeTexturePanel(bpy.types.Panel):
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
        row.prop(bake_settings, 'open_bake_settings_menu', text="Bake Settings", icon = 'TRIA_DOWN' if bake_settings.open_bake_settings_menu else 'TRIA_RIGHT' )
        
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
            

            row = box.row()
            row.prop(scene.bake_settings, 'bake_image_name',  text="")

            if bake_settings.pbr_nodes:
                row = box.row()
                # col = row.collumn()
                row.prop(scene.bake_settings, 'mute_texture_nodes', text="Mute Texture Mapping")
                row.prop(scene.bake_settings, 'bake_image_clear', text="Clear Bake Image")

            if bake_settings.lightmap or bake_settings.ao_map:
                row = box.row()
                row.prop(scene.bake_settings, 'lightmap_bakes',text="") 
                row.operator("object.select_lightmap_objects",text="",icon="RESTRICT_SELECT_OFF")

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
        row.prop(scene.bake_settings, 'open_object_bake_list_menu', text="Lightmapped Objects", icon = 'TRIA_DOWN' if bake_settings.open_object_bake_list_menu else 'TRIA_RIGHT' )
        
        # BAKE LIST
        if bake_settings.open_object_bake_list_menu:
            layout.template_list("GTT_BAKE_IMAGE_UL_List", "", data, "objects", scene.bake_settings, "bake_object_index")       


        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator("object.node_to_texture_operator",text="Bake Textures")
        row.operator("scene.open_textures_folder",icon='FILEBROWSER')
        
        # VISIBILITY
        layout.label(text="Visiblity")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.switch_org_mat_operator",icon = 'NODE_MATERIAL', text="PBR Material")
        row.operator("object.switch_bake_mat_operator",icon = 'MATERIAL', text="PBR Baked Material")
        col.separator()
        row = col.row(align=True)
        row.prop(scene.texture_settings,"toggle_lightmap_texture", text="Show Material" if scene.texture_settings.toggle_lightmap_texture else "Show Baked Texture", icon="SHADING_RENDERED" if scene.texture_settings.toggle_lightmap_texture else "NODE_MATERIAL")
    

def headline(layout,*valueList):
    box = layout.box()
    row = box.row()
    
    split = row.split()
    for pair in valueList:
        split = split.split(factor=pair[0])
        split.label(text=pair[1])
        
class GTT_TextureSelectionPanel(bpy.types.Panel):
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

        texture_settings = bpy.context.scene.texture_settings

        # UI LIST
        headline(layout,(0.6,"IMAGE NAME"),(0.5,"SIZE"),(1,"KB"))
        layout.template_list("GTT_TEX_UL_List", "", data, "images", scene.texture_settings, "texture_index")
        
        row = layout.row()
        row.prop(texture_settings, 'open_texture_settings_menu', text="Texture Settings", icon = 'TRIA_DOWN' if texture_settings.open_texture_settings_menu else 'TRIA_RIGHT' )
        
        if texture_settings.open_texture_settings_menu:

            box = layout.box()                
              
            box.prop(scene.texture_settings, 'show_all_textures', text="Show all Textures")
            box.prop(scene.texture_settings, 'operate_on_all_textures', text="Operate on all Textures")    
                      
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
  
class GTT_CleanupPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_cleanup_panel"
    bl_label = "Cleanup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'GLB Texture Tools'
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("image.clean_textures",text="Clean Textures",icon = 'OUTLINER_OB_IMAGE')
        row.operator("material.clean_materials",text="Clean Materials",icon = 'NODE_MATERIAL')

        row = layout.row()
        row.operator("material.remove_lightmap",text="Clean Lightmap",icon = 'MOD_UVPROJECT')
        row.operator("material.remove_ao_map",text="Clean AO Map",icon = 'TRASH')



class GTT_UVPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_UV_panel"
    bl_label = "UV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GLB Texture Tools"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    def draw(self, context):
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


class GTT_HelpPanel(bpy.types.Panel):
    bl_idname = "GLBTEXTOOLS_PT_help_panel"
    bl_label = "Help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GLB Texture Tools"
    bl_order = 5

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        addon_updater_ops.check_for_update_background()

        if addon_updater_ops.updater.update_ready == True:
            layout.label(text="New version is out", icon="INFO")

		# call built-in function with draw code/checks
        addon_updater_ops.update_notice_box_ui(self, context)
        
        layout.prop(scene,"help_tex_tools",text="Help",icon = 'HELP')


        
        

        
