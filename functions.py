import bpy.ops as O
import bpy
import os
from .constants import *
import mathutils

class BakeUtilities():
    C = bpy.context
    D = bpy.data
    O = bpy.ops

    all_materials = None
    image_texture_nodes = set()
    bake_settings = None
    bake_image = None
    render_engine = None

    def __init__(self, selected_objects, bake_settings):
        self.C = bpy.context
        self.D = bpy.data
        self.render_engine = self.C.scene.render.engine

        all_materials = set()
        slots_array = [obj.material_slots for obj in selected_objects]
        for slots in slots_array:
            for slot in slots:
                all_materials.add(slot.material)

        self.all_materials = all_materials
        self.bake_settings = bake_settings

        image_size = [int(self.C.scene.img_bake_size),
                      int(self.C.scene.img_bake_size)]
        image_name = bake_settings.bake_image_name

        self.bake_image = create_image(image_name, image_size)

    def setup_engine(self):
        if self.render_engine == 'BLENDER_EEVEE':
            self.C.scene.render.engine = 'CYCLES'
        
        # setup samples
        if self.bake_settings.lightmap:
            self.C.scene.cycles.samples = self.bake_settings.lightmap_samples
        if self.bake_settings.ao_map:
            self.C.scene.cycles.samples = self.bake_settings.ao_samples

        device = self.C.scene.cycles.device
        if device != 'GPU':
            try:
                device = 'GPU'
            except:
                device = 'CPU'
                print("GPU not Supported, leaving at CPU")

    def unwrap_selected(self):
        if self.bake_settings.unwrap:
            self.O.object.add_uv(uv_name=self.bake_settings.uv_name)
            self.O.object.transform_apply(location=False, rotation=False, scale=True)
            self.O.object.mode_set(mode='EDIT')
            self.O.mesh.select_all(action='SELECT')
            self.O.uv.smart_project(island_margin=self.bake_settings.unwrap_margin)
            self.O.object.mode_set(mode='OBJECT')

    def add_gltf_settings_node(self, material):
        nodes = material.node_tree.nodes
         # create group data
        gltf_settings = bpy.data.node_groups.get('glTF Settings')
        if gltf_settings is None:
            bpy.data.node_groups.new('glTF Settings', 'ShaderNodeTree')
        
        # add group to node tree
        gltf_settings_node = nodes.get('glTF Settings')
        if gltf_settings_node is None:
            gltf_settings_node = nodes.new('ShaderNodeGroup')
            gltf_settings_node.name = 'glTF Settings'
            gltf_settings_node.node_tree = bpy.data.node_groups['glTF Settings']

        # create group inputs
        if gltf_settings_node.inputs.get('Occlusion') is None:
            gltf_settings_node.inputs.new('NodeSocketFloat','Occlusion')

        return gltf_settings_node

    def add_image_texture_node(self, material):
        # add image texture
        image_texture_node = add_node(material, Shader_Node_Types.image_texture, "Texture Bake")
        image_texture_node.image = self.bake_image

        # save texture nodes and pbr nodes for later
        self.image_texture_nodes.add(image_texture_node)

        return image_texture_node

    def save_metal_value(self):
        for material in self.all_materials:
            nodes = material.node_tree.nodes
            pbr_node = find_node_by_type(nodes, Node_Types.pbr_node)[0]
            
            # save metal value
            metallic_value = pbr_node.inputs["Metallic"].default_value
            pbr_node["original_metallic"] = metallic_value
            pbr_node.inputs["Metallic"].default_value = 0

    def load_metal_value(self):
        for material in self.all_materials:
            nodes = material.node_tree.nodes
            pbr_node = find_node_by_type(nodes,Node_Types.pbr_node)[0]   
            pbr_node.inputs["Metallic"].default_value = pbr_node["original_metallic"]

    def add_uv_node(self,material):

        uv_node = add_node(material, Shader_Node_Types.uv, "Second_UV")
        uv_node.uv_map = self.bake_settings.uv_name
        return uv_node

    def position_gltf_setup_nodes(self,material,uv_node,image_texture_node,gltf_settings_node):
        nodes = material.node_tree.nodes
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
        gltf_settings_node.location = loc

        nodes.active = image_texture_node

    def add_gltf_setup(self):
        for material in self.all_materials:
            uv_node = self.add_uv_node(material)
            image_texture_node = self.add_image_texture_node(material)
            gltf_settings_node = self.add_gltf_settings_node(material)

            # position
            self.position_gltf_setup_nodes(material,uv_node,image_texture_node,gltf_settings_node)

            # linking
            make_link(material, uv_node.outputs["UV"],image_texture_node.inputs['Vector'])
            make_link(material, image_texture_node.outputs['Color'], gltf_settings_node.inputs['Occlusion'])

    def bake(self,bake_type):
        channels_to_bake = bake_type
        baked_images = []

        if not self.bake_settings.denoise:              
            channel = bake_type[0]
            self.bake_and_save_image(self.bake_image,channel)
            return

        for channel in channels_to_bake:
            image_name = self.bake_image.name + "_" + channel 
            image = create_image(image_name,self.bake_image.size)
            bake_image = self.bake_and_save_image(image,channel)
            baked_images.append(bake_image)

        if len(baked_images) == 3:
            denoised_image_path = comp_ai_denoise(baked_images[0],baked_images[1],baked_images[2],)
            self.bake_image.filepath = denoised_image_path
            self.bake_image.source = "FILE"
            self.change_image_in_nodes(self.bake_image)

    def change_image_in_nodes(self,image):
        for image_texture_node in self.image_texture_nodes:
            image_texture_node.image = image

    def bake_and_save_image(self, image, channel):
        self.change_image_in_nodes(image)

        if channel == "NOISY":
            O.object.bake(type="DIFFUSE", pass_filter={'COLOR', 'DIRECT', 'INDIRECT'}, use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)
        
        if channel == "AO":
            O.object.bake(type="AO", use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)
        
        if channel == "NRM":
            self.C.scene.cycles.samples = 1
            O.object.bake(type="NORMAL", use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)
        if channel == "COLOR":
            self.C.scene.cycles.samples = 1
            O.object.bake(type="DIFFUSE", pass_filter={'COLOR'}, use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)

        save_image(image)

        return image

    def cleanup(self):
        self.C.scene.render.engine = self.render_engine

        # cleanup images
        if self.bake_settings.cleanup_textures:
            for img in self.D.images:
                if self.bake_image.name in img.name and ("_COLOR" in img.name or "_NRM" in img.name or "_NOISY" in img.name) :
                    self.D.images.remove(img)

        # show image
        show_image_in_image_editor(self.bake_image)

def update_bakes_list(bake_settings, context):
    bake_textures_set = set()

    for obj in bpy.data.objects:
        if obj.bake_texture_name:
            bake_textures_set.add(
                (obj.bake_texture_name, obj.bake_texture_name, "Baked Texture Name"))
    # print(list(bake_textures_set))
    return list(bake_textures_set)

# COMPOSITING
def comp_ai_denoise(noisy_image, nrm_image, color_image):

    # switch on nodes and get reference
    if not bpy.context.scene.use_nodes:
        bpy.context.scene.use_nodes = True

    tree = bpy.context.scene.node_tree

    # clear default nodes
    # for node in tree.nodes:
    #     tree.nodes.remove(node)

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

    filePath = bpy.data.filepath
    path = os.path.dirname(filePath)

    bpy.data.scenes["Scene"].render.filepath = path + \
        "\\textures\\GLBTexTool\\" + noisy_image.name + "_Denoise"
    bpy.ops.render.render(write_still=True)
    denoised_image_path = bpy.data.scenes["Scene"].render.filepath + "." + \
        bpy.data.scenes["Scene"].render.image_settings.file_format.lower()

    # cleanup
    comp_nodes = [image_node,nrm_image_node,color_image_node,denoise_node,comp_node]
    for node in comp_nodes:
        tree.nodes.remove(node)

    return denoised_image_path

def select_object(self, obj):
    C = bpy.context
    try:
        O.object.select_all(action='DESELECT')
        C.view_layer.objects.active = obj
        obj.select_set(True)
    except:
        self.report({'INFO'}, "Object not in View Layer")


def select_obj_by_mat(self, mat):
    D = bpy.data
    for obj in D.objects:
        if obj.type == "MESH":
            object_materials = [
                slot.material for slot in obj.material_slots]
            if mat in object_materials:
                select_object(self, obj)


def set_image_in_image_editor(self,context):
    sel_texture = bpy.data.images[self.texture_index]
    show_image_in_image_editor(sel_texture)
    

def show_image_in_image_editor(image):
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = image


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
    filename, file_extention = os.path.splitext(image.name)
    file_extention = image.file_format.lower()
    if file_extention == "jpeg":
        file_extention = "jpg"
    if file_extention == "targa":
        file_extention = "tga"

    # change path
    savepath = path + "\\textures\\GLBTexTool\\" + \
        str(image.size[0]) + "\\" + image.name
    image.filepath_raw = savepath + "." + file_extention
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


def check_only_one_pbr(self, material):
    check_ok = True
    # get pbr shader
    nodes = material.node_tree.nodes
    pbr_node_type = Node_Types.pbr_node
    pbr_nodes = find_node_by_type(nodes, pbr_node_type)

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


def clean_empty_materials(self):
    for obj in bpy.data.objects:
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                print("Removed Empty Materials from " + obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.material_slot_remove()


def get_pbr_inputs(pbr_node):

    base_color_input = pbr_node.inputs["Base Color"]
    metallic_input = pbr_node.inputs["Metallic"]
    specular_input = pbr_node.inputs["Specular"]
    roughness_input = pbr_node.inputs["Roughness"]
    normal_input = pbr_node.inputs["Normal"]

    pbr_inputs = {"base_color_input": base_color_input, "metallic_input": metallic_input,
                  "specular_input": specular_input, "roughness_input": roughness_input, "normal_input": normal_input}
    return pbr_inputs


def find_node_by_type(nodes, node_type):
    nodes_found = [n for n in nodes if n.type == node_type]
    return nodes_found


def find_node_by_type_recusivly(material, note_to_start, node_type, del_nodes_inbetween=False):
    nodes = material.node_tree.nodes
    if note_to_start.type == node_type:
        return note_to_start

    for input in note_to_start.inputs:
        for link in input.links:
            current_node = link.from_node
            if (del_nodes_inbetween and note_to_start.type != Node_Types.normal_map and note_to_start.type != Node_Types.bump_map):
                nodes.remove(note_to_start)
            return find_node_by_type_recusivly(material, current_node, node_type, del_nodes_inbetween)


def find_node_by_name_recusivly(node, idname):
    if node.bl_idname == idname:
        return node

    for input in node.inputs:
        for link in input.links:
            current_node = link.from_node
            return find_node_by_name_recusivly(current_node, idname)


def make_link(material, socket1, socket2):
    links = material.node_tree.links
    links.new(socket1, socket2)


def remove_link(material, socket1, socket2):

    node_tree = material.node_tree
    links = node_tree.links

    for l in socket1.links:
        if l.to_socket == socket2:
            links.remove(l)


def add_gamma_node(material, pbrInput):
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


def preview_bake_texture(self, context):
    all_materials = bpy.data.materials
    toggle_bake_texture = context.scene.texture_settings.toggle_bake_texture
    for mat in all_materials:
        nodes = mat.node_tree.nodes
        ao_node = nodes.get("Texture Bake")
        if ao_node is not None:
            if toggle_bake_texture:
                emission_setup(mat, ao_node.outputs["Color"])
            else:
                pbr_node = find_node_by_type(nodes, Node_Types.pbr_node)[0]
                remove_node(mat, "Emission Bake")
                reconnect_PBR(mat, pbr_node)


def emission_setup(material, node_output):
    nodes = material.node_tree.nodes
    emission_node = add_node(
        material, Shader_Node_Types.emission, "Emission Bake")

    # link emission to whatever goes into current pbrInput
    emission_input = emission_node.inputs[0]
    make_link(material, node_output, emission_input)

    # link emission to materialOutput
    surface_input = nodes.get("Material Output").inputs[0]
    emission_output = emission_node.outputs[0]
    make_link(material, emission_output, surface_input)


def link_pbr_to_output(material, pbr_node):
    nodes = material.node_tree.nodes
    surface_input = nodes.get("Material Output").inputs[0]
    make_link(material, pbr_node.outputs[0], surface_input)


def reconnect_PBR(material, pbrNode):
    nodes = material.node_tree.nodes
    pbr_output = pbrNode.outputs[0]
    surface_input = nodes.get("Material Output").inputs[0]
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
