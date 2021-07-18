import bpy
from bpy import context
from . import node_functions
from . import material_functions
from . import constants
import mathutils


def update_selected_image(self, context):
    sel_texture = bpy.data.images[self.texture_index]
    show_image_in_image_editor(sel_texture)


def show_image_in_image_editor(image):
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = image
            
            
def switch_baked_material(show_bake_material,affect):
    
    current_bake_type = bpy.context.scene.bake_settings.get_current_bake_type()
    material_name_suffix = constants.Material_Suffix.bake_type_mat_suffix[current_bake_type]
    
    # on what object to work
    if affect == 'active':
        objects = [bpy.context.active_object]
    elif affect == 'selected':
        objects = bpy.context.selected_editable_objects
    elif affect == 'visible':
        objects = [ob for ob in bpy.context.view_layer.objects if ob.visible_get()]
    elif affect == 'scene':
        objects = bpy.context.scene.objects
     
    
    all_mats = bpy.data.materials
    baked_mats = [mat for mat in all_mats if material_name_suffix in mat.name]
    

    for obj in objects:   

        if current_bake_type != "pbr":
            baked_ao_flag = getattr(obj,"ao_map_name") != '' or getattr(obj,"lightmap_name") != '' 
            if not baked_ao_flag:
                continue
        
        for slot in obj.material_slots:
            if show_bake_material:
                    for baked_mat in baked_mats:                      
                        if baked_mat.name == slot.material.name + material_name_suffix + obj.bake_version:
                            slot.material = baked_mat

            else:
                if (material_name_suffix in slot.material.name):
                    bake_material = slot.material 
                    index = bake_material.name.find(material_name_suffix)
                    org_mat = all_mats.get(bake_material.name[0:index]) 
                    if org_mat is not None:
                        slot.material = org_mat
 
def preview_bake_texture(self,context):
    context = bpy.context
    bake_settings = context.scene.bake_settings
    preview_bake_texture = context.scene.texture_settings.preview_bake_texture
    vis_mats = material_functions.get_all_visible_materials()
    for mat in vis_mats:
        if not mat.node_tree:
            continue

        nodes = mat.node_tree.nodes
        bake_texture_node = None
        if bake_settings.lightmap_bake:
            bake_texture_node = nodes.get(bake_settings.texture_node_lightmap)

        elif bake_settings.ao_bake:
            bake_texture_node = nodes.get(bake_settings.texture_node_ao)


        if bake_texture_node is not None:
            if preview_bake_texture:
                node_functions.emission_setup(mat, bake_texture_node.outputs["Color"])
            else:
                pbr_node = node_functions.get_nodes_by_type(nodes, constants.Node_Types.pbr_node)
                if len(pbr_node) == 0:
                    return
                
                pbr_node = pbr_node[0]
                node_functions.remove_node(mat, "Emission Bake")
                node_functions.reconnect_PBR(mat, pbr_node)


def preview_lightmap(self, context):
        preview_lightmap = context.scene.texture_settings.preview_lightmap
        vis_mats = material_functions.get_all_visible_materials()
        for material in vis_mats:
            if not material.node_tree:
                continue
            
            nodes = material.node_tree.nodes

            lightmap_node = nodes.get("Lightmap")
            if lightmap_node is None:
                continue
            
            pbr_node = node_functions.get_pbr_node(material)
            if pbr_node is None:
                print("\n " + material.name + " has no PBR Node \n")
                continue
            base_color_input = node_functions.get_pbr_inputs(pbr_node)["base_color_input"]
            emission_input = node_functions.get_pbr_inputs(pbr_node)["emission_input"]

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
    
    vis_mats = material_functions.get_all_visible_materials()
    for material in vis_mats:
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



