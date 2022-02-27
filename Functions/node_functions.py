import bpy.ops as O
import bpy
import os
from .. Functions import constants
import mathutils


# -----------------------COMPOSITING--------------------#
def blur_bake_image(noisy_image,color_image):
    
    # switch on nodes and get reference
    if not bpy.context.scene.use_nodes:
        bpy.context.scene.use_nodes = True

    tree = bpy.context.scene.node_tree
    
    # add cam if not in scene  
    cam = bpy.context.scene.camera
    if not cam:
        bpy.ops.object.camera_add()
    
    # bake image
    image_node = tree.nodes.new(type='CompositorNodeImage')
    image_node.image = noisy_image
    image_node.location = 0, 0
    
    # color image
    color_image_node = tree.nodes.new(type='CompositorNodeImage')
    color_image_node.image = color_image
    color_image_node.location = 0, 300

    # create blur node
    blur_node = tree.nodes.new(type='CompositorNodeBilateralblur')
    blur_node.location = 300, 0

    # create output node
    comp_node = tree.nodes.new('CompositorNodeComposite')
    comp_node.location = 600, 0

    # link nodes
    links = tree.links
    links.new(image_node.outputs[0], blur_node.inputs[0])
    links.new(color_image_node.outputs[0], blur_node.inputs[1])
    links.new(blur_node.outputs[0], comp_node.inputs[0])

    # set output resolution to image res
    bpy.context.scene.render.resolution_x = noisy_image.size[0]
    bpy.context.scene.render.resolution_y = noisy_image.size[1]

    
    # set output path
    scene = bpy.context.scene
    outputImagePath = constants.Path_List.get_textures_dir()

    # set image format and quality
    scene.render.image_settings.file_format = bpy.context.scene.img_file_format
    scene.render.image_settings.quality = 100
     
    scene.render.filepath = os.path.join(outputImagePath,noisy_image.name + "_Denoise_AO")
    bpy.ops.render.render(write_still=True)

    if bpy.context.scene.img_file_format == 'JPEG':
        file_extention = '.jpg'
    elif bpy.context.scene.img_file_format == 'PNG':
        file_extention = '.png'
    elif bpy.context.scene.img_file_format == 'HDR':
        file_extention = '.hdr'
    
    # cleanup
    comp_nodes = [image_node,color_image_node,blur_node,comp_node]
    for node in comp_nodes:
        tree.nodes.remove(node)

    return scene.render.filepath + file_extention

def comp_ai_denoise(noisy_image, nrm_image, color_image):

    # switch on nodes and get reference
    if not bpy.context.scene.use_nodes:
        bpy.context.scene.use_nodes = True

    tree = bpy.context.scene.node_tree

    # add cam if not in scene
    cam = bpy.context.scene.camera
    if not cam:
        bpy.ops.object.camera_add()

    # bake image
    image_node = tree.nodes.new(type='CompositorNodeImage')
    image_node.image = noisy_image
    image_node.location = 0, 0

    # nrm image
    nrm_image_node = tree.nodes.new(type='CompositorNodeImage')
    nrm_image_node.image = nrm_image
    nrm_image_node.location = 0, 300

    # color image
    color_image_node = tree.nodes.new(type='CompositorNodeImage')
    color_image_node.image = color_image
    color_image_node.location = 0, 600

    # create denoise node
    denoise_node = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node.location = 300, 0

    # create output node
    comp_node = tree.nodes.new('CompositorNodeComposite')
    comp_node.location = 600, 0

    # link nodes
    links = tree.links
    links.new(image_node.outputs[0], denoise_node.inputs[0])
    links.new(nrm_image_node.outputs[0], denoise_node.inputs[1])
    links.new(color_image_node.outputs[0], denoise_node.inputs[2])
    links.new(denoise_node.outputs[0], comp_node.inputs[0])

    # set output resolution to image res
    bpy.context.scene.render.resolution_x = noisy_image.size[0]
    bpy.context.scene.render.resolution_y = noisy_image.size[1]

    # set output path
    scene = bpy.context.scene
    outputImagePath = constants.Path_List.get_textures_dir()

    # set image format and quality
    scene.render.image_settings.file_format = bpy.context.scene.img_file_format
    scene.render.image_settings.quality = 100
     
    scene.render.filepath = os.path.join(outputImagePath,noisy_image.name + "_Denoise_LM")
    print("Starting Denoise")
    bpy.ops.render.render(write_still=True)

    if bpy.context.scene.img_file_format == 'JPEG':
        file_extention = '.jpg'
    elif bpy.context.scene.img_file_format == 'PNG':
        file_extention = '.png'
    elif bpy.context.scene.img_file_format == 'HDR':
        file_extention = '.hdr'
    
    # cleanup
    comp_nodes = [image_node, nrm_image_node,color_image_node, denoise_node, comp_node]
    for node in comp_nodes:
        tree.nodes.remove(node)

    return scene.render.filepath + file_extention


# -----------------------CHECKING --------------------#


def check_pbr(self, material):
    check_ok = True
    
    if material is None:
        return False
    
    if material.node_tree is None:
        return False
    
    if material.node_tree.nodes is None:
        return False
   
    # get pbr shader
    nodes = material.node_tree.nodes
    pbr_node_type = constants.Node_Types.pbr_node
    pbr_nodes = get_nodes_by_type(nodes, pbr_node_type)

    # check only one pbr node
    if len(pbr_nodes) == 0:
        self.report({'INFO'}, 'No PBR Shader Found')
        check_ok = False

    if len(pbr_nodes) > 1:
        self.report(
            {'INFO'}, 'More than one PBR Node found ! Clean before Baking.')
        check_ok = False

    return check_ok


def check_is_org_material(self, material):
    check_ok = True
    if "_Bake" in material.name:
        self.report({'INFO'}, 'Change back to org. Material')
        check_ok = False

    return check_ok


# -----------------------NODES --------------------#


def get_pbr_inputs(pbr_node):

    base_color_input = pbr_node.inputs["Base Color"]
    metallic_input = pbr_node.inputs["Metallic"]
    specular_input = pbr_node.inputs["Specular"]
    roughness_input = pbr_node.inputs["Roughness"]
    normal_input = pbr_node.inputs["Normal"]
    emission_input = pbr_node.inputs["Emission"]
    alpha_input = pbr_node.inputs["Alpha"]

    pbr_inputs = {"base_color_input": base_color_input, "metallic_input": metallic_input,
                  "specular_input": specular_input, "roughness_input": roughness_input, 
                  "normal_input": normal_input, "emission_input": emission_input,"alpha_input":alpha_input}
    return pbr_inputs


def get_nodes_by_type(nodes, node_type):
    nodes_found = [n for n in nodes if n.type == node_type]
    return nodes_found


def get_node_by_type_recusivly(material, note_to_start, node_type, del_nodes_inbetween=False):
    nodes = material.node_tree.nodes
    if note_to_start.type == node_type:
        return note_to_start

    for input in note_to_start.inputs:
        for link in input.links:
            current_node = link.from_node
            if (del_nodes_inbetween and note_to_start.type != constants.Node_Types.normal_map and note_to_start.type != constants.Node_Types.bump_map):
                nodes.remove(note_to_start)
            return get_node_by_type_recusivly(material, current_node, node_type, del_nodes_inbetween)


def get_node_by_name_recusivly(node, idname):
    if node.bl_idname == idname:
        return node

    for input in node.inputs:
        for link in input.links:
            current_node = link.from_node
            return get_node_by_name_recusivly(current_node, idname)


def get_pbr_node(material):
    nodes = material.node_tree.nodes
    pbr_node = get_nodes_by_type(nodes, constants.Node_Types.pbr_node)
    if len(pbr_node) > 0:
        return pbr_node[0]


def make_link(material, socket1, socket2):
    links = material.node_tree.links
    links.new(socket1, socket2)


def remove_link(material, socket1, socket2):

    node_tree = material.node_tree
    links = node_tree.links

    for l in socket1.links:
        if l.to_socket == socket2:
            links.remove(l)


def add_in_gamme_node(material, pbrInput):
    nodeToPrincipledOutput = pbrInput.links[0].from_socket

    gammaNode = material.node_tree.nodes.new("ShaderNodeGamma")
    gammaNode.inputs[1].default_value = 2.2
    gammaNode.name = "Gamma Bake"

    # link in gamma
    make_link(material, nodeToPrincipledOutput, gammaNode.inputs["Color"])
    make_link(material, gammaNode.outputs["Color"], pbrInput)


def remove_gamma_node(material, pbrInput):
    nodes = material.node_tree.nodes
    gammaNode = nodes.get("Gamma Bake")
    nodeToPrincipledOutput = gammaNode.inputs[0].links[0].from_socket

    make_link(material, nodeToPrincipledOutput, pbrInput)
    material.node_tree.nodes.remove(gammaNode)


def emission_setup(material, node_output):
    nodes = material.node_tree.nodes
    emission_node = add_node(
        material, constants.Shader_Node_Types.emission, "Emission Bake")

    # link emission to whatever goes into current pbrInput
    emission_input = emission_node.inputs[0]
    make_link(material, node_output, emission_input)

    # link emission to materialOutput
    surface_input = get_nodes_by_type(nodes,constants.Node_Types.material_output)[0].inputs[0]
    emission_output = emission_node.outputs[0]
    make_link(material, emission_output, surface_input)


def link_pbr_to_output(material, pbr_node):
    nodes = material.node_tree.nodes
    surface_input = get_nodes_by_type(nodes,constants.Node_Types.material_output)[0].inputs[0]
    make_link(material, pbr_node.outputs[0], surface_input)

def reconnect_PBR(material, pbrNode):
    nodes = material.node_tree.nodes
    pbr_output = pbrNode.outputs[0]
    surface_input = get_nodes_by_type(
        nodes, constants.Node_Types.material_output)[0].inputs[0]
    make_link(material, pbr_output, surface_input)


def mute_all_texture_mappings(material, do_mute):
    nodes = material.node_tree.nodes
    for node in nodes:
        if node.bl_idname == "ShaderNodeMapping":
            node.mute = do_mute


def add_node(material, shader_node_type, node_name):
    nodes = material.node_tree.nodes
    new_node = nodes.get(node_name)
    if new_node is None:
        new_node = nodes.new(shader_node_type)
        new_node.name = node_name
        new_node.label = node_name
    return new_node


def remove_node(material, node_name):
    nodes = material.node_tree.nodes
    node = nodes.get(node_name)
    if node is not None:
        nodes.remove(node)

def remove_reconnect_node(material, node_name):
    nodes = material.node_tree.nodes
    node = nodes.get(node_name)
    input_node = node.inputs["Color1"].links[0].from_node
    output_node = node.outputs["Color"].links[0].to_node

    if node is not None:
        make_link(material,input_node.outputs["Color"],output_node.inputs["Base Color"])
        nodes.remove(node)

def remove_unused_nodes(material):
    nodes = material.node_tree.nodes
    all_nodes = set(nodes)
    connected_nodes = set()
    material_output = nodes.get("Material Output")

    get_all_connected_nodes(material_output, connected_nodes)

    unconnected_nodes = all_nodes - connected_nodes

    for node in unconnected_nodes:
        nodes.remove(node)


def remove_double_linking(material,texture_node):
    color_output = texture_node.outputs["Color"]
    links_count = len(color_output.links)
    org_vector_input = texture_node.inputs["Vector"]
    position_y = texture_node.location.y

    if links_count > 1:
        for link in color_output.links:
            
            new_texture_node = add_node(material,constants.Shader_Node_Types.image_texture,texture_node.name + "_Copy" + str(link))
            new_texture_node.image = texture_node.image
            new_texture_node.location = texture_node.location
            position_y -= 250 
            new_texture_node.location.y = position_y

            # relink tex node output
            make_link(material,new_texture_node.outputs["Color"],link.to_socket)
            
            # remap texture mapping
            if len(org_vector_input.links) != 0:
                new_vector_input = new_texture_node.inputs["Vector"]
                tex_transform_socket = org_vector_input.links[0].from_socket
                make_link(material,tex_transform_socket,new_vector_input)
            


def get_all_connected_nodes(node, connected_nodes):

    connected_nodes.add(node)

    for input in node.inputs:
        for link in input.links:
            current_node = link.from_node
            get_all_connected_nodes(current_node, connected_nodes)
