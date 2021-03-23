import bpy
from . import functions
from .. Functions import material_functions


def Diff(li1, li2):
    return (list(set(li1) - set(li2)))


def compareImages(images):
    firstImg = images[0]
    firstImgPixels = firstImg.pixels

    for img in images[1:]:
        currentImgPixels = img.pixels
        diff = Diff(firstImgPixels, currentImgPixels)
        if len(diff) == 0:
            print(firstImg.name + " and " + img.name + " map !")

    return compareImages(images[1:])


class CleanDupliTexturesOperator(bpy.types.Operator):
    """By checking the incoming links in the PBR Shader, new Textures are generated that will include all the node transformations."""
    bl_idname = "object.clean_dupli_textures"
    bl_label = "Delete Texture Duplicates"

    def execute(self, context):

        # images = bpy.data.images
        # compareImages(images)
        material_functions.clean_empty_materials(self)

        return {'FINISHED'}
