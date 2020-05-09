import bpy
from . import functions
from .functions import BakeUtilities

from .constants import *
import mathutils
import os

def Bake_Texture(selected_objects,bake_settings):
    # ----------------------- CREATE INSTANCE --------------------#
    ligthmap_utilities = BakeUtilities(selected_objects,bake_settings)  

    # -----------------------SETUP UV'S--------------------#
    ligthmap_utilities.unwrap_selected()

    # -----------------------SETUP ENGINE--------------------#
    ligthmap_utilities.setup_engine()
    
    # -----------------------SETUP NODES--------------------#
    ligthmap_utilities.add_gltf_setup()

    # ----------------------- BAKING --------------------#
    ligthmap_utilities.save_metal_value()
    ligthmap_utilities.bake()
    ligthmap_utilities.load_metal_value()
    ligthmap_utilities.cleanup()


    
    return


def Bake_On_Plane(material,bake_settings):

    # -----------------------SETUP VARS--------------------#
    C = bpy.context
    D = bpy.data
    O = bpy.ops

    nodes = material.node_tree.nodes
    pbr_node = functions.find_node_by_type(nodes,Node_Types.pbr_node)[0]        
    pbr_inputs = functions.get_pbr_inputs(pbr_node)

    image_size = [int(C.scene.img_bake_size),int(C.scene.img_bake_size)]

    # -----------------------SETUP ENGINE--------------------#
    if C.scene.render.engine == 'BLENDER_EEVEE':
        C.scene.render.engine = 'CYCLES'
        C.scene.cycles.samples = bake_settings.pbr_samples
        device = C.scene.cycles.device
        if device != 'GPU':
            try:
                device = 'GPU'
            except:
                device = 'CPU'
                print("GPU not Supported, leaving at CPU")

    # -----------------------SETUP BAKE PLANE--------------------#

    bake_plane = D.objects.get(material.name + "_Bake")

    if bake_plane is not None:
        print(bake_plane.name + " was found, remove bake plane !")
        return

    O.mesh.primitive_plane_add(size=2, location=(2, 0, 0))
    bake_plane = C.object
    bake_plane.name = material.name + "_Bake"
    bake_plane.data.materials.append(material)


    # mute texture mapping
    if bake_settings.mute_texture_nodes:
        functions.mute_all_texture_mappings(material, True)

    # for each input create an image
    for pbr_input in pbr_inputs.values():

        # -----------------------TESTING--------------------#
        # skip if input has no connection
        if not pbr_input.is_linked:
            continue

        # skip if input has only texture node attached
        texture_node = pbr_input.links[0].from_node
        if texture_node.type == Node_Types.image_texture:
            texture_node.image.org_image_name = texture_node.image.name
            continue

        # -----------------------IMAGE CLEANUP--------------------#
        
        image_name = material.name + "_" + pbr_input.name + "_" + str(image_size[0]) + "x" + str(image_size[1])
        
        # find image
        bake_image = D.images.get(image_name)

        # remove image
        if bake_image is not None:
            D.images.remove(bake_image)

        bake_image = D.images.new(image_name, width=image_size[0], height=image_size[1])
        bake_image.name = image_name
        
        image_texture_node = functions.add_node(material,Shader_Node_Types.image_texture,"Image Texture Bake")

        image_texture_node.image = bake_image
        nodes.active = image_texture_node

        # -----------------------COPY ORG IMAGE--------------------#
        # copy file settings form original image texture
        org_img_node = functions.find_node_by_type_recusivly(material,pbr_input.links[0].from_node,Node_Types.image_texture)
        if org_img_node:
            org_image = org_img_node.image
            bake_image.file_format = 'PNG' if ".png" in org_image.name else "JPEG"     
            bake_image.colorspace_settings.name = org_image.colorspace_settings.name
        # -----------------------PROCEDURAL TEXTURE--------------------#
        # else:
            # uv_node = add_node(material,Shader_Node_Types.uv,"PROC_UV")
            # make_link(material,uv_node.outputs["UV"],image_texture_node.inputs["Vector"]) 




        
    # -----------------------BAKING--------------------#
    
        if pbr_input is pbr_inputs["normal_input"]:
            functions.link_pbr_to_output(material, pbr_node)
            O.object.bake(type="NORMAL", use_clear=True)
        else:
            # if pbr_input is not pbr_inputs.get("base_color_input"):
            #     add_gamma_node(material, pbr_input)
            functions.emission_setup(material, pbr_input.links[0].from_socket)
            O.object.bake(type="EMIT", use_clear=True)
            # if pbr_input is not pbr_inputs.get("base_color_input"):
            #     remove_gamma_node(material, pbr_input)


    # -----------------------CLEANUP--------------------#

    # switch back to eevee
    C.scene.render.engine = 'BLENDER_EEVEE'

    # unmute texture mappings
    functions.mute_all_texture_mappings(material, False)

    # delete plane
    O.object.delete()

    # cleanup nodes
    functions.remove_node(material,"Emission Bake")
    functions.remove_node(material,"Image Texture Bake")
    functions.reconnect_PBR(material, pbr_node)
    return
