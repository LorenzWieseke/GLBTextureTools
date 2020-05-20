from bpy.utils import register_class, unregister_class
from . import bake_utilities

classes = [

]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)