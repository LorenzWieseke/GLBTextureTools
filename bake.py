import bpy
from .functions import *
from .constants import *
import mathutils
import os

def Bake_Texture(selected_objects,bake_settings):
    # -----------------------SETUP VARS--------------------#
    C = bpy.context
    D = bpy.data
    O = bpy.ops

    uv_name = "Lightmap"

    all_materials = set ()
    slots_array = [obj.material_slots for obj in selected_objects]
    for slots in slots_array:
        for slot in slots:
            all_materials.add(slot.material)

    # -----------------------SETUP UV'S--------------------#
    if bake_settings.unwrap:
        O.object.add_uv(uv_name=uv_name)
        O.object.transform_apply(location=False, rotation=False, scale=True)
        O.object.mode_set(mode = 'EDIT')
        O.mesh.select_all(action = 'SELECT')
        O.uv.smart_project(island_margin=0.08)
        O.object.mode_set(mode = 'OBJECT')

    # -----------------------SETUP ENGINE--------------------#
    if C.scene.render.engine == 'BLENDER_EEVEE':
        C.scene.render.engine = 'CYCLES'
        if bake_settings.ao_map:
            C.scene.cycles.samples = bake_settings.ao_samples
        if bake_settings.lightmap:
            C.scene.cycles.samples = bake_settings.lightmap_samples
        device = C.scene.cycles.device
        if device != 'GPU':
            try:
                device = 'GPU'
            except:
                device = 'CPU'
                print("GPU not Supported, leaving at CPU")
    
    # -----------------------SETUP IMAGE--------------------#
    image_size = [int(C.scene.img_bake_size),int(C.scene.img_bake_size)]
    image_name = bake_settings.bake_image_name
        
    bake_image = create_image(image_name,image_size)

    
    # -----------------------SETUP NODES--------------------#
    for material in all_materials:

        nodes = material.node_tree.nodes
        
        # add image texture
        image_texture_node = add_node(material,Shader_Node_Types.image_texture,"AO Bake")
        image_texture_node.image = bake_image


        # -----------------------AO SETUP--------------------#
        # create group data
        gltf_settings = bpy.data.node_groups.get('glTF Settings')
        if gltf_settings is None:
            bpy.data.node_groups.new('glTF Settings', 'ShaderNodeTree')
        
        # add group to node tree
        ao_group = nodes.get('glTF Settings')
        if ao_group is None:
            ao_group = nodes.new('ShaderNodeGroup')
            ao_group.name = 'glTF Settings'
            ao_group.node_tree = bpy.data.node_groups['glTF Settings']

        # create group inputs
        if ao_group.inputs.get('Occlusion') is None:
            ao_group.inputs.new('NodeSocketFloat','Occlusion')
            
        # create uv node
        uv_node = add_node(material,Shader_Node_Types.uv,"Second_UV")     
        uv_node.uv_map = uv_name


        make_link(material,uv_node.outputs["UV"],image_texture_node.inputs['Vector'])
        make_link(material,image_texture_node.outputs['Color'],ao_group.inputs['Occlusion'])

        # ----------------------- SETUP AO NODE --------------------#
        ao_node = add_node(material,Shader_Node_Types.ao,"AO")
        if bake_settings.ao_map:
            emission_setup(material,ao_node.outputs[1])


        # ----------------------- POSITION NODES --------------------#
        # uv node
        pbr_node = find_node_by_type(nodes,Node_Types.pbr_node)[0]   
        posOffset = mathutils.Vector((-900, 400))
        loc = pbr_node.location + posOffset
        uv_node.location = loc

        # image texture
        loc = loc + mathutils.Vector((300, 0))
        image_texture_node.location = loc

        # ao node
        loc = loc + mathutils.Vector((300, 0))
        ao_group.location = loc

        nodes.active = image_texture_node

    # ----------------------- BAKING --------------------#
    # bake once for all selcted objects
    if (bake_settings.ao_map):
        O.object.bake(type="EMIT", use_clear=bake_settings.bake_image_clear,margin=2)
    elif (bake_settings.lightmap):
        O.object.bake(type="DIFFUSE", pass_filter= {'COLOR', 'DIRECT', 'INDIRECT','AO'}, use_clear=bake_settings.bake_image_clear,margin=2)
        save_image(bake_image)
        org_name = bake_image.name
        org_filepath = bake_image.filepath

        bake_image.name = org_name + "_NRM"   
        O.object.bake(type="NORMAL", use_clear=bake_settings.bake_image_clear,margin=2) 
        save_image(bake_image)    

        bake_image.name = org_name + "_COLOR"   
        O.object.bake(type="DIFFUSE", pass_filter= {'COLOR'}, use_clear=bake_settings.bake_image_clear,margin=2)    
        save_image(bake_image)

        bake_image.name = org_name
        bake_image.filepath = org_filepath

        nrm_image_name = org_name + "_NRM"
        nrm_image = create_image(nrm_image_name,bake_image.size)

        file_format = os.path.splitext(bake_image.filepath)[1]
        nrm_image.filepath = os.path.dirname(org_filepath) + "\\" + org_name + "_NRM" + file_format
        nrm_image.source = "FILE"

        color_image_name = org_name + "_COLOR"
        color_image = create_image(color_image_name,bake_image.size)
        color_image.filepath = os.path.dirname(org_filepath) + "\\" + org_name + "_COLOR" + file_format
        color_image.source = "FILE"


        denoised_image_path = comp_ai_denoise(bake_image,nrm_image,color_image)

        bake_image.filepath = denoised_image_path

        # clear images
        # D.images.remove(nrm_image)
        # D.images.remove(color_image)





    # ----------------------- CLEANUP --------------------#
    C.scene.render.engine = 'BLENDER_EEVEE'
    # cleanup images
    # for img in D.images:
    #     if image_name in img.name and "_" in img.name:
    #         D.images.remove(img)

    # cleanup nodes
    for material in all_materials:
        nodes = material.node_tree.nodes
        pbr_node = find_node_by_type(nodes,Node_Types.pbr_node)[0]   
        remove_node(material,"Emission Bake")
        remove_node(material,"AO")
        reconnect_PBR(material, pbr_node)
    return


def Bake_On_Plane(material,bake_settings):

    # -----------------------SETUP VARS--------------------#
    C = bpy.context
    D = bpy.data
    O = bpy.ops

    nodes = material.node_tree.nodes
    pbr_node = find_node_by_type(nodes,Node_Types.pbr_node)[0]        
    pbr_inputs = get_pbr_inputs(pbr_node)

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
        mute_all_texture_mappings(material, True)

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
        
        image_texture_node = add_node(material,Shader_Node_Types.image_texture,"Image Texture Bake")

        image_texture_node.image = bake_image
        nodes.active = image_texture_node

        # -----------------------COPY ORG IMAGE--------------------#
        # copy file settings form original image texture
        org_img_node = find_node_by_type_recusivly(material,pbr_input.links[0].from_node,Node_Types.image_texture)
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
            link_pbr_to_output(material, pbr_node)
            O.object.bake(type="NORMAL", use_clear=True)
        else:
            # if pbr_input is not pbr_inputs.get("base_color_input"):
            #     add_gamma_node(material, pbr_input)
            emission_setup(material, pbr_input.links[0].from_socket)
            O.object.bake(type="EMIT", use_clear=True)
            # if pbr_input is not pbr_inputs.get("base_color_input"):
            #     remove_gamma_node(material, pbr_input)


    # -----------------------CLEANUP--------------------#

    # switch back to eevee
    C.scene.render.engine = 'BLENDER_EEVEE'

    # unmute texture mappings
    mute_all_texture_mappings(material, False)

    # delete plane
    O.object.delete()

    # cleanup nodes
    remove_node(material,"Emission Bake")
    remove_node(material,"Image Texture Bake")
    reconnect_PBR(material, pbr_node)


    return
