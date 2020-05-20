from bpy.utils import register_class, unregister_class
from . import panel,panel_ui_list

classes = [
    panel_ui_list.GTT_BAKE_IMAGE_UL_List,
    panel_ui_list.GTT_TEX_UL_List,
    panel.GTT_ResolutionPanel,
    panel.GTT_TextureSelectionPanel,
    panel.GTT_BakeTexturePanel,
    panel.GTT_CleanupPanel,
    panel.GTT_HelpPanel,
    panel.GTT_UVPanel
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)