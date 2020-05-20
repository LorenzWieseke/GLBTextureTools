import bpy
from .. Functions import node_functions
from .. Functions import image_functions
from .. Functions import constants

class GTT_TEX_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()

            split = row.split(factor=0.6)
            split.label(text=str(item.users) + " " +item.name)
            
            split = split.split(factor=0.5)
            split.label(text=str(item.size[0]))

            split = split.split(factor=1)
            
            filepath = item.filepath
            if filepath != '':
                filesize = image_functions.get_file_size(filepath)
                split.label(text=str(filesize).split('.')[0])
            else:
                split.label(text="file not saved")

    def filter_items(self, context, data, propname):
        texture_settings = context.scene.texture_settings
        selected_objects = context.selected_objects

        all_materials = set()
        all_image_names = [image.name for image in data.images]

        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)
 
        # Default return values.
        flt_flags = []
        flt_neworder = []
        images = []

        if texture_settings.show_all_textures:
            images = [image.name for image in data.images if image.name not in ('Viewer Node','Render Result')]
        else:
            for mat in all_materials:
                nodes = mat.node_tree.nodes
                tex_nodes = node_functions.find_node_by_type(nodes,constants.Node_Types.image_texture)
                [images.append(node.image.name) for node in tex_nodes]

        flt_flags = [self.bitflag_filter_item if name in images else 0 for name in all_image_names]

        return flt_flags, flt_neworder

class GTT_BAKE_IMAGE_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text=item.name)
            
    def filter_items(self, context, data, propname):
        bake_settings = context.scene.bake_settings
        objects = data.objects

        # Default return values.
        flt_flags = []
        flt_neworder = []

        flt_flags = [self.bitflag_filter_item if obj.bake_texture_name == bake_settings.lightmap_bakes else 0 for obj in objects]

        return flt_flags, flt_neworder
            

