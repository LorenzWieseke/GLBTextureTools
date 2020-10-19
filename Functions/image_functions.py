import bpy
import os
from . import node_functions
from . import constants

# def get_all_images_in_material()

def get_all_images_in_selected_objects(selected_objects):
    all_materials = set()
    images = []

    slots_array = [obj.material_slots for obj in selected_objects]
    for slots in slots_array:
        for slot in slots:
            all_materials.add(slot.material)
    
    for mat in all_materials:
            nodes = mat.node_tree.nodes
            tex_nodes = node_functions.get_node_by_type(nodes,constants.Node_Types.image_texture)
            [images.append(node.image) for node in tex_nodes]
    
    return images


def save_image(image):

    filePath = bpy.data.filepath
    path = os.path.dirname(filePath)


    if not os.path.exists(path + "/textures"):
        os.mkdir(path + "/textures")

    if not os.path.exists(path + "/textures/GLBTexTool"):
        os.mkdir(path + "/textures/GLBTexTool")

    if not os.path.exists(path + "/textures/GLBTexTool/" + str(image.size[0])):
        os.mkdir(path + "/textures/GLBTexTool/" + str(image.size[0]))

    # file format
    image.file_format = bpy.context.scene.img_file_format

    # change path
    savepath = path + "\\textures\\GLBTexTool\\" + str(image.size[0]) + "\\" + image.name + "." + image.file_format

    image.filepath_raw = savepath
    image.save()

def create_image(image_name, image_size):
    D = bpy.data
    # find image
    image = D.images.get(image_name)

    if image:
        old_size = list(image.size)
        new_size = list(image_size)

        if old_size != new_size:
            D.images.remove(image)
            image = None

    # image = D.images.get(image_name)

    if image is None:
        image = D.images.new(
            image_name, width=image_size[0], height=image_size[1])
        image.name = image_name

    return image

def get_file_size(filepath):
    size = "Unpack Files"
    try:
        path = bpy.path.abspath(filepath)
        size = os.path.getsize(path)
        size /= 1024
    except:
        return ("Unpack")
        # print("error getting file path for " + filepath)

    return (size)

def scale_image(image, new_size):
    if (image.org_filepath != ''):
        image.filepath = image.org_filepath

    image.org_filepath = image.filepath

    # set image back to original if size is 0, else scale it
    if new_size[0] == 0:
        image.filepath_raw = image.org_filepath
    else:
        image.scale(new_size[0], new_size[1])
        save_image(image)

        
