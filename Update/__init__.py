from bpy.utils import register_class, unregister_class
import bpy
from . import addon_updater_ops
from . import updater_preferences

classes = [
    updater_preferences.GTT_Preferences
]

def register(bl_info):
    addon_updater_ops.register(bl_info)
    for cls in classes:
        register_class(cls)
        addon_updater_ops.make_annotations(cls)
        
def unregister():
    addon_updater_ops.unregister()
    for cls in classes:
        unregister_class(cls)