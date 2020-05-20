from bpy.utils import register_class, unregister_class
from . import properties

classes = [
    # properties.GTT_Bake_Settings,
    # properties.GTT_Cleanup_Settings,
    # properties.GTT_Texture_Settings,
    # properties.GTT_UV_Settings
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)