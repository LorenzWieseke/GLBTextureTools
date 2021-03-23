import bpy
def get_all_visible_materials():
    objects=[ob for ob in bpy.context.view_layer.objects if ob.visible_get()]
    slot_array = [object.material_slots for object in objects]
    vis_mat = set()
    for slots in slot_array:
        for slot in slots:
            vis_mat.add(slot.material)

    # to remove None values in list 
    vis_mat = list(filter(None, vis_mat)) 
    return vis_mat

def clean_empty_materials(self):
    for obj in bpy.data.objects:
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                print("Removed Empty Materials from " + obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.material_slot_remove()