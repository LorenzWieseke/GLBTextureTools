from bpy.utils import register_class, unregister_class
import bpy
from . import object_functions

classes = [
    
]

def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(object_functions.update_one_selection)
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)