import bpy
from .. Functions import node_functions

def apply_transform_on_linked():    
    bpy.ops.object.select_linked(type='OBDATA')
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.make_links_data(type='OBDATA')

def select_object(self, obj):
    C = bpy.context
    O = bpy.ops
    try:
        O.object.select_all(action='DESELECT')
        C.view_layer.objects.active = obj
        obj.select_set(True)
    except:
        self.report({'INFO'}, "Object not in View Layer")

def select_obj_by_mat(mat,self=None):
    D = bpy.data
    result = []
    for obj in D.objects:
        if obj.type == "MESH":
            object_materials = [slot.material for slot in obj.material_slots]
            if mat in object_materials:
                result.append(obj)
                if (self):
                    select_object(self, obj)

    return result

# TODO - save objects in array, unlink objects, apply scale and link them back
def apply_scale_on_multiuser():
    O = bpy.ops
    O.object.transform_apply(location=False, rotation=False, scale=True)