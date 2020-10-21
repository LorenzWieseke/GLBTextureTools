import bpy
from . import node_functions
from . import object_functions
from . import constants
import mathutils


def show_selected_image_in_image_editor(self, context):
    sel_texture = bpy.data.images[self.texture_index]
    show_image_in_image_editor(sel_texture)


def show_image_in_image_editor(image):
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = image


def preview_bake_material():
    C = bpy.context

    active_obj = C.active_object
    active_mat = C.active_object.active_material

    all_mats = bpy.data.materials
    mat_bake = all_mats.get(active_mat.name + "_Bake")

    # for obj in bpy.data.objects:
    for slot in active_obj.material_slots:
        if mat_bake is not None and slot.material is active_mat:
            slot.material = mat_bake


def preview_bake_texture(self, context):
    all_materials = bpy.data.materials
    bake_settings = context.scene.bake_settings
    preview_bake_texture = context.scene.texture_settings.preview_bake_texture
    for mat in all_materials:
        if not mat.node_tree:
            continue

        nodes = mat.node_tree.nodes
        bake_texture_node = None
        if bake_settings.lightmap:
            bake_texture_node = nodes.get(bake_settings.texture_node_lightmap)

        elif bake_settings.ao_map:
            bake_texture_node = nodes.get(bake_settings.texture_node_ao)


        if bake_texture_node is not None:
            if preview_bake_texture:
                node_functions.emission_setup(
                    mat, bake_texture_node.outputs["Color"])
            else:
                pbr_node = node_functions.get_node_by_type(
                    nodes, constants.Node_Types.pbr_node)[0]
                node_functions.remove_node(mat, "Emission Bake")
                node_functions.reconnect_PBR(mat, pbr_node)


def preview_lightmap(self, context):
        preview_lightmap = context.scene.texture_settings.preview_lightmap
        all_materials = bpy.data.materials
        for material in all_materials:
            if not material.node_tree:
                continue
                   
            nodes = material.node_tree.nodes

            pbr_node = node_functions.get_pbr_node(material)
            base_color_input = node_functions.get_pbr_inputs(pbr_node)["base_color_input"]
            emission_input = node_functions.get_pbr_inputs(pbr_node)["emission_input"]

            lightmap_node = nodes.get("Lightmap")
            if lightmap_node is None:
                continue
            lightmap_output = lightmap_node.outputs["Color"]
            
            if preview_lightmap:

                # add mix node
                mix_node_name = "Mulitply Lightmap"
                mix_node = node_functions.add_node(material,constants.Shader_Node_Types.mix, mix_node_name)
                mix_node.blend_type = 'MULTIPLY'
                mix_node.inputs[0].default_value = 1 # set factor to 1
                pos_offset = mathutils.Vector((-200, 200))
                mix_node.location = pbr_node.location + pos_offset

                mix_node_input1 = mix_node.inputs["Color1"]
                mix_node_input2 = mix_node.inputs["Color2"]
                mix_node_output = mix_node.outputs["Color"]

                # image texture in base color
                if base_color_input.is_linked:
                    node_before_base_color = base_color_input.links[0].from_node
                    if not node_before_base_color.name == mix_node_name:
                        node_functions.make_link(material, node_before_base_color.outputs["Color"], mix_node_input1)
                        node_functions.make_link(material, lightmap_output, mix_node_input2)
                        node_functions.make_link(material, mix_node_output, base_color_input)
                else :
                    mix_node_input1.default_value = base_color_input.default_value 
                    node_functions.make_link(material, lightmap_output, mix_node_input2)
                    node_functions.make_link(material, mix_node_output, base_color_input)

                node_functions.remove_link(material,lightmap_output,emission_input)
            
            if not preview_lightmap:
                
                # remove mix and reconnect base color

                mix_node = nodes.get("Mulitply Lightmap")

                if mix_node is not None:
                    color_input_connections = len(mix_node.inputs["Color1"].links)

                    if (color_input_connections == 0):
                        node_functions.remove_node(material,mix_node.name)
                    else:
                        node_functions.remove_reconnect_node(material,mix_node.name)
                
                node_functions.link_pbr_to_output(material,pbr_node)
                        
                



def lightmap_to_emission(self, context, connect):
    
    all_materials = bpy.data.materials
    for material in all_materials:
        if not material.node_tree:
            continue

        nodes = material.node_tree.nodes

        pbr_node = node_functions.get_pbr_node(material)
        lightmap_node = nodes.get("Lightmap")

        if lightmap_node is None:
            continue

        emission_input = node_functions.get_pbr_inputs(pbr_node)["emission_input"]
        lightmap_output = lightmap_node.outputs["Color"]

        if connect:
            node_functions.make_link(material, lightmap_output, emission_input)
        else:
            node_functions.remove_link(material,lightmap_output,emission_input)



