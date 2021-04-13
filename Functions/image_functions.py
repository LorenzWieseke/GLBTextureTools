import bpy
import os
from . import node_functions
from . import constants

# def get_all_images_in_material()

def get_all_images_in_ui_list():
    
    images_in_scene = bpy.data.images
    image_name_list = bpy.types.GTT_TEX_UL_List.image_name_list
    images_found = []
    
    if len(image_name_list) > 0:
        images_found = [img for img in images_in_scene for name_list_entry in image_name_list if img.name == name_list_entry]
        
    return images_found


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

    if new_size[0] > image.size[0] or new_size[1] > image.size[1]:
        new_size[0] = image.size[0]
        new_size[1] = image.size[1]

    # set image back to original if size is 0, else scale it
    if new_size[0] == 0:
        image.filepath_raw = image.org_filepath
    else:
        image.scale(new_size[0], new_size[1])
        save_image(image)

        
