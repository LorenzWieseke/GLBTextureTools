import bpy

addon_keymaps = []


# keymap
def register():

    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new("object.dp_ot_draw_operator", 'F', 'PRESS', shift=True, ctrl=True)
        
        addon_keymaps.append((km, kmi))
def unregister():

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        addon_keymaps.clear()