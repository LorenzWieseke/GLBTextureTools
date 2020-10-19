import bpy

addon_keymaps = []


# keymap
def register():

    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new("scene.open_textures_folder", 'O', 'PRESS', shift=True, ctrl=True)
        kmi = km.keymap_items.new("scene.gltf_quick_export", 'E', 'PRESS', shift=True, ctrl=True)
        kmi = km.keymap_items.new("scene.open_web_preview", 'P', 'PRESS', shift=True, ctrl=True)
        
        addon_keymaps.append((km, kmi))
def unregister():

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        addon_keymaps.clear()