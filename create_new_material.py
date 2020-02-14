from .functions import *
from .constants import *
import bpy
import mathutils
import os


def create_bake_material(org_material):

     # -----------------------CREATE MATERIAL--------------------#
    bake_material_name = org_material.name + "_Bake"
    bake_material = bpy.data.materials.get(bake_material_name)

    if bake_material is not None:
        bpy.data.materials.remove(bake_material)

    # and create new from org. material
    bake_material = org_material.copy()
    bake_material.name = bake_material_name

    # -----------------------SETUP VARS--------------------#
    C = bpy.context
    D = bpy.data

    image_size = [int(C.scene.img_bake_size),int(C.scene.img_bake_size)]

    nodes = bake_material.node_tree.nodes
    pbr_node = find_node_by_type(nodes,Node_Types.pbr_node)[0]        
    pbr_inputs = get_pbr_inputs(pbr_node)

    for pbr_input in pbr_inputs.values():

        if not pbr_input.is_linked:
            continue

        # -----------------------REPLACE IMAGE TEXTURES--------------------#
        first_node_after_input = pbr_input.links[0].from_node
        tex_node = find_node_by_type_recusivly(bake_material,first_node_after_input,Node_Types.image_texture,True)

        bake_image_name = org_material.name + "_" + pbr_input.name + "_" + str(image_size[0]) + "x" + str(image_size[1])
        bake_image = D.images.get(bake_image_name)

        # if no texture node found (baking procedural textures) add new one
        if tex_node is None:
            tex_node = add_node(bake_material,Shader_Node_Types.image_texture,bake_image_name)

        # keep org image if nothing changed
        if bake_image is None:
            org_image = D.images.get(tex_node.image.org_image_name)
            tex_node.image = org_image
        else:
            save_image(bake_image)
            tex_node.image = bake_image
        
         # -----------------------LINKING--------------------#
        if pbr_input is pbr_inputs["normal_input"]:
            normal_node = first_node_after_input
            normal_node.inputs["Strength"].default_value = 1
            
                    
            if normal_node.type == Node_Types.bump_map:
                bump_node = normal_node
                normal_node = add_node(bake_material,Shader_Node_Types.normal,"Normal from Bump")
                normal_node.location = bump_node.location
                nodes.remove(bump_node)
 
            make_link(bake_material, tex_node.outputs[0], normal_node.inputs["Color"])
            make_link(bake_material, normal_node.outputs["Normal"], pbr_input)
        else:
            make_link(bake_material,tex_node.outputs[0], pbr_input)

         # -----------------------SET COLOR SPACE--------------------#
        if pbr_input is not pbr_inputs["base_color_input"]:
            tex_node.image.colorspace_settings.name = "Non-Color"

    return bake_material
