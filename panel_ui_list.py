import bpy
from . import functions

class TEX_UL_List(bpy.types.UIList):
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
                filesize = functions.get_file_size(filepath)
                split.label(text=str(filesize).split('.')[0])
            else:
                split.label(text="file not saved")

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        object_list = objects.items()
        img_names = [obj[0] for obj in object_list]

        # Default return values.
        flt_flags = []
        flt_neworder = []
        images = []
        try:
            active_mat = context.active_object.active_material
            if active_mat is not None:
                nodes = active_mat.node_tree.nodes
                tex_nodes = functions.find_node_by_type(nodes,Node_Types.image_texture)
                images = [node.image.name for node in tex_nodes]
            else:
                images = [image.name for image in bpy.data.images if image.name not in ('Viewer Node','Render Result')]
        except:
            pass
    
        flt_flags = [self.bitflag_filter_item if name in images else 0 for name in img_names]

        return flt_flags, flt_neworder

class BAKE_IMAGE_UL_List(bpy.types.UIList):
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
            

