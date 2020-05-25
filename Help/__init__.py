from bpy.utils import register_class, unregister_class
from . import help_overlay

classes = [
    help_overlay.GTT_Help_Operator
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)