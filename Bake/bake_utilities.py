import bpy
import mathutils
from .. Functions import node_functions
from .. Functions import image_functions
from .. Functions import constants
from .. Functions import visibility_functions
from .. Functions import object_functions


class BakeUtilities():
    C = bpy.context
    D = bpy.data
    O = bpy.ops

    all_materials = None
    image_texture_nodes = None
    bake_settings = None
    bake_image = None
    render_engine = None
    selected_objects = None
    image_size = None
    parent_operator = None
    tex_node_name = None

    def __init__(self,parent_operator,selected_objects, bake_settings):
        self.C = bpy.context
        self.D = bpy.data
        self.parent_operator = parent_operator
        self.render_engine = self.C.scene.render.engine

        self.selected_objects = selected_objects

        if self.selected_objects is not None:
            all_materials = set()
            slots_array = [obj.material_slots for obj in self.selected_objects]
            for slots in slots_array:
                for slot in slots:
                    all_materials.add(slot.material)
                
            self.all_materials = all_materials
            
        self.bake_settings = bake_settings
        self.baked_images = []
        self.image_texture_nodes = set()
        self.image_size = [int(self.C.scene.img_bake_size),
                      int(self.C.scene.img_bake_size)]
        image_name = bake_settings.bake_image_name

        self.bake_image = image_functions.create_image(image_name, self.image_size)

    def setup_engine(self):
        # setup engine
        if self.render_engine == 'BLENDER_EEVEE':
            self.C.scene.render.engine = 'CYCLES'
            
        # setup device type
        self.cycles_device_type = self.C.preferences.addons['cycles'].preferences.compute_device_type
        if self.cycles_device_type == 'OPTIX':
            self.C.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        
        # setup samples
        if self.bake_settings.pbr_nodes:
            self.C.scene.cycles.samples = self.bake_settings.pbr_samples
        if self.bake_settings.lightmap:
            self.C.scene.cycles.samples = self.bake_settings.lightmap_samples
        if self.bake_settings.ao_map:
            self.C.scene.cycles.samples = self.bake_settings.ao_samples

        self.C.scene.render.resolution_percentage = 100

        device = self.C.scene.cycles.device
        if device != 'GPU':
            try:
                device = 'GPU'
            except:
                device = 'CPU'
                print("GPU not Supported, leaving at CPU")

    def set_active_uv_to_lightmap(self):
        bpy.ops.object.set_active_uv(uv_slot=2)



    def unwrap_selected(self):
        if self.bake_settings.unwrap:
            self.O.object.add_uv(uv_name=self.bake_settings.uv_name)

            # apply scale on linked
            sel_objects = self.C.selected_objects
            scene_objects = self.D.objects
            linked_objects = set()

            for sel_obj in sel_objects:
                for scene_obj in scene_objects:
                    if sel_obj.data.original is scene_obj.data and sel_obj is not scene_obj:
                        linked_objects.add(sel_obj)
            
            # self.O.object.select_all(action='DESELECT')
            # for linked_obj in linked_objects:
            #     linked_obj.select_set(True)

            # object_functions.apply_transform_on_linked()

            # self.O.object.select_all(action='DESELECT')
            # for sel_obj in sel_objects:
            #     if sel_obj not in linked_objects:
            #         sel_obj.select_set(True)

            # do not apply transform if linked objects in selection
            if not len(linked_objects)>0:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


            self.O.object.mode_set(mode='EDIT')
            self.O.mesh.reveal()
            self.O.mesh.select_all(action='SELECT')
            self.O.uv.smart_project(island_margin=self.bake_settings.unwrap_margin)
            self.O.object.mode_set(mode='OBJECT')

    def create_bake_material(self,material_name_suffix):
        
        bake_materials = []
        # create new material for every slot on selcted objects
        for material in self.all_materials:

            org_material = material
            
            # is material already baked, continue
            if material_name_suffix in org_material.name:
                continue  

            bake_material_name = org_material.name + material_name_suffix
            
            for i in range(1,10,1):               
                if self.check_if_bake_material_exists(bake_material_name):
                    bake_material_name += str(i)
                else:
                    continue
          
            bake_material = org_material.copy()
            bake_material.name = bake_material_name
            bake_materials.append(bake_material)
  
        visibility_functions.switch_baked_material(True)
        self.all_materials = bake_materials

    # material was baked before
    def check_if_bake_material_exists(self,material_name):
        bake_material = bpy.data.materials.get(material_name)
        if bake_material is not None:
            return True


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
        nodes = material.node_tree.nodes
        
        # add image texture
        if self.bake_settings.lightmap:
            self.tex_node_name = self.bake_settings.texture_node_lightmap

        if self.bake_settings.ao_map:
            self.tex_node_name = self.bake_settings.texture_node_ao
        
        image_texture_node = node_functions.add_node(material, constants.Shader_Node_Types.image_texture, self.tex_node_name)
        image_texture_node.image = self.bake_image
        self.bake_image.colorspace_settings.name = "Linear"
        nodes.active = image_texture_node

        # save texture nodes and pbr nodes for later
        self.image_texture_nodes.add(image_texture_node)

        return image_texture_node

    def save_metal_value(self):
        for material in self.all_materials:
            nodes = material.node_tree.nodes
            pbr_node = node_functions.get_pbr_node(material)
            
            # save metal value
            metallic_value = pbr_node.inputs["Metallic"].default_value
            pbr_node["original_metallic"] = metallic_value
            pbr_node.inputs["Metallic"].default_value = 0

            # save metal image
            if pbr_node.inputs["Metallic"].is_linked:
                # get metal image node, save it in pbr node and remove connection
                metal_image_node = pbr_node.inputs["Metallic"].links[0].from_node
                self.metal_image_node = metal_image_node
                node_functions.remove_link(material,metal_image_node.outputs[0],pbr_node.inputs["Metallic"])

    def load_metal_value(self):
        for material in self.all_materials:
            nodes = material.node_tree.nodes
            pbr_node = node_functions.get_pbr_node(material)   
            pbr_node.inputs["Metallic"].default_value = pbr_node["original_metallic"]

            # reconnect metal image
            if hasattr(self,"metal_image_node"):
                node_functions.make_link(material,self.metal_image_node.outputs[0],pbr_node.inputs["Metallic"])

    def add_uv_node(self,material):

        uv_node = node_functions.add_node(material, constants.Shader_Node_Types.uv, "Second_UV")
        uv_node.uv_map = self.bake_settings.uv_name
        return uv_node

    def position_gltf_setup_nodes(self,material,uv_node,image_texture_node,gltf_settings_node):
        nodes = material.node_tree.nodes
        # uv node
        pbr_node = node_functions.get_pbr_node(material)   
        pos_offset = mathutils.Vector((-900, 400))
        loc = pbr_node.location + pos_offset
        uv_node.location = loc

        # image texture
        loc = loc + mathutils.Vector((300, 0))
        image_texture_node.location = loc

        # ao node
        loc = loc + mathutils.Vector((300, 0))
        gltf_settings_node.location = loc

        nodes.active = image_texture_node

    def add_node_setup(self):    
        for material in self.all_materials:
            # AO
            if self.bake_settings.ao_map:
                uv_node = self.add_uv_node(material)
                image_texture_node = self.add_image_texture_node(material)
                gltf_settings_node = self.add_gltf_settings_node(material)

                # position
                self.position_gltf_setup_nodes(material,uv_node,image_texture_node,gltf_settings_node)

                # linking
                node_functions.make_link(material, uv_node.outputs["UV"],image_texture_node.inputs['Vector'])
                node_functions.make_link(material, image_texture_node.outputs['Color'], gltf_settings_node.inputs['Occlusion'])
            
            # LIGHTMAP
            if self.bake_settings.lightmap:
                image_texture_node = self.add_image_texture_node(material)
                uv_node = self.add_uv_node(material)
                # position
                image_texture_node.location =  mathutils.Vector((-500, 200))
                uv_node.location = mathutils.Vector((-700, 200))

                # linking
                pbr_node = node_functions.get_pbr_node(material)
                # node_functions.make_link(material, image_texture_node.outputs['Color'], pbr_node.inputs['Emission'])
                node_functions.make_link(material, uv_node.outputs["UV"],image_texture_node.inputs['Vector'])        

    def bake(self,bake_type):
        channels_to_bake = bake_type
        self.baked_images = []
        
        # if no denoise, bake only first image
        if not self.bake_settings.denoise:              
            channel = bake_type[0]
            self.bake_and_save_image(self.bake_image,channel)
            return

        for channel in channels_to_bake:
            image_name = self.bake_image.name + "_" + channel 
            image = image_functions.create_image(image_name,self.bake_image.size)
            self.change_image_in_nodes(image)
            baked_channel_image = self.bake_and_save_image(image,channel)
            self.baked_images.append(baked_channel_image)
            
        self.denoise()

    def denoise(self):
        # denoise
        if self.bake_settings.lightmap:           
            denoised_image_path = node_functions.comp_ai_denoise(self.baked_images[0],self.baked_images[1],self.baked_images[2])
            self.bake_image.filepath = denoised_image_path
            self.bake_image.source = "FILE"
            self.change_image_in_nodes(self.bake_image)
            
        # blur
        if self.bake_settings.ao_map and self.bake_settings.denoise:
            blur_image_path = node_functions.blur_bake_image(self.baked_images[0],self.baked_images[1])
            self.bake_image.filepath = blur_image_path
            self.bake_image.source = "FILE"
            self.change_image_in_nodes(self.bake_image)

    def change_image_in_nodes(self,image):
        for image_texture_node in self.image_texture_nodes:
            if image_texture_node.name == self.tex_node_name:
                image_texture_node.image = image

    def bake_and_save_image(self, image, channel):
        if channel == "NRM":
            self.C.scene.cycles.samples = 1
            self.O.object.bake(type="NORMAL", use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)
        
        if channel == "COLOR":
            self.C.scene.cycles.samples = 1
            self.O.object.bake(type="DIFFUSE", pass_filter={'COLOR'}, use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)

        if channel == "AO":
            self.O.object.bake(type="AO", use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)
        
        if channel == "NOISY":
            self.O.object.bake(type="DIFFUSE", pass_filter={'DIRECT', 'INDIRECT'}, use_clear=self.bake_settings.bake_image_clear, margin=self.bake_settings.bake_margin)
        
        image_functions.save_image(image)

        return image

    def add_lightmap_flag(self):
         for obj in self.selected_objects:
             obj.hasLightmap = True

    def cleanup(self):
        # set back engine
        self.C.scene.render.engine = self.render_engine
        self.C.preferences.addons['cycles'].preferences.compute_device_type = self.cycles_device_type

        # cleanup images
        if self.bake_settings.cleanup_textures:
            for img in self.D.images:
                if self.bake_image.name in img.name and ("_COLOR" in img.name or "_NRM" in img.name or "_NOISY" in img.name) :
                    self.D.images.remove(img)

        # show image
        visibility_functions.show_image_in_image_editor(self.bake_image)


class PbrBakeUtilities(BakeUtilities):
    active_material = None
    parent_operator = None

    def __init__(self,parent_operator, material, bake_settings):
        super().__init__(parent_operator,None,bake_settings)
        self.active_material = material
        self.active_object = bpy.context.active_object
        self.active_material.use_fake_user = True
        self.parent_operator = parent_operator

    def ready_for_bake(self):
        # check if not baked material
        if "_Bake" in self.active_material.name:
            return
        
        print("\n Checking " + self.active_material.name + "\n")
        # check if renderer not set to optix
        if self.C.preferences.addons["cycles"].preferences.compute_device_type == "OPTIX":
            self.C.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
            self.parent_operator.report({'INFO'}, 'Changing Compute device to CUDA cause Baking in Optix not Supported')
        
        # check if pbr node exists
        check_ok = node_functions.check_pbr(self.parent_operator,self.active_material) and node_functions.check_is_org_material(self.parent_operator,self.active_material)
        if not check_ok :
            self.parent_operator.report({'INFO'}, "Material " + self.active_material.name + " has errors !")
            return False
        return True
                     
    def preview_bake_material(self):
        bpy.context.view_layer.objects.active = self.active_object
        self.active_object.select_set(True)
        visibility_functions.switch_baked_material("_Bake")

    def cleanup_nodes(self):
        bake_material = self.active_material
        node_functions.remove_unused_nodes(bake_material)

    def add_bake_plane(self):
        material = self.active_material
        bake_plane = self.D.objects.get(material.name + "_Bake")

        if bake_plane is not None:
            self.parent_operator.report({'INFO'}, 'Delete Bake Plane')
            return

        self.O.mesh.primitive_plane_add(size=2, location=(2, 0, 0))
        bake_plane = self.C.object
        bake_plane.name = material.name + "_Bake"
        bake_plane.data.materials.append(material)


    def bake_pbr(self):
        material = self.active_material
        nodes = material.node_tree.nodes
        pbr_node = node_functions.get_pbr_node(material)        
        pbr_inputs = node_functions.get_pbr_inputs(pbr_node)
        image_texture_node = None

        # mute texture mapping
        if self.bake_settings.mute_texture_nodes:
            node_functions.mute_all_texture_mappings(material, True)

        for pbr_input in pbr_inputs.values():

            # -----------------------TESTING--------------------#
            # skip if input has no connection
            if not pbr_input.is_linked:
                continue

            # skip if input has only texture node attached
            texture_node = pbr_input.links[0].from_node
            if texture_node.type == constants.Node_Types.image_texture:
                texture_node.image.org_image_name = texture_node.image.name
                continue

            # -----------------------IMAGE --------------------#
            
            image_name = material.name + "_" + pbr_input.name
            
            # find image
            bake_image = self.D.images.get(image_name)

            # remove image
            if bake_image is not None:
                self.D.images.remove(bake_image)

            bake_image = self.D.images.new(image_name, width=self.image_size[0], height=self.image_size[1])
            bake_image.name = image_name
            
            image_texture_node = node_functions.add_node(material,constants.Shader_Node_Types.image_texture,"PBR Bake")

            image_texture_node.image = bake_image
            nodes.active = image_texture_node

            # -----------------------SET COLOR SPACE--------------------#
            if pbr_input is not pbr_inputs["base_color_input"]:
                bake_image.colorspace_settings.name = "Non-Color"

            # -----------------------BAKING--------------------#    
            if pbr_input is pbr_inputs["normal_input"]:
                node_functions.link_pbr_to_output(material, pbr_node)
                self.O.object.bake(type="NORMAL", use_clear=True)
            else:
                node_functions.emission_setup(material, pbr_input.links[0].from_socket)
                self.O.object.bake(type="EMIT", use_clear=True)

        # unmute texture mappings
        node_functions.mute_all_texture_mappings(material, False)

        # delete plane
        self.O.object.delete()
        
        # cleanup nodes
        node_functions.remove_node(material,"Emission Bake")
        node_functions.remove_node(material,"PBR Bake")
        node_functions.reconnect_PBR(material, pbr_node)

    def create_pbr_bake_material(self,material_name_suffix):

        # -----------------------CREATE MATERIAL--------------------#
        org_material = self.active_material
        bake_material_name = org_material.name + material_name_suffix
        bake_material = bpy.data.materials.get(bake_material_name)

        if bake_material is not None:
            bpy.data.materials.remove(bake_material)

        # and create new from org. material
        bake_material = org_material.copy()
        bake_material.name = bake_material_name
        self.bake_material = bake_material

    def create_nodes_after_pbr_bake(self):
        # -----------------------SETUP VARS--------------------#
        org_material = self.active_material
        bake_material = self.bake_material
        nodes = bake_material.node_tree.nodes
        pbr_node = node_functions.get_pbr_node(bake_material)        
        pbr_inputs = node_functions.get_pbr_inputs(pbr_node)

        for pbr_input in pbr_inputs.values():

            if not pbr_input.is_linked:
                continue

            # -----------------------REPLACE IMAGE TEXTURES--------------------#
            first_node_after_input = pbr_input.links[0].from_node
            tex_node = node_functions.get_node_by_type_recusivly(bake_material,first_node_after_input,constants.Node_Types.image_texture,True)

            bake_image_name = org_material.name + "_" + pbr_input.name
            bake_image = self.D.images.get(bake_image_name)

            # if no texture node found (baking procedural textures) add new one
            if tex_node is None:
                tex_node = node_functions.add_node(bake_material,constants.Shader_Node_Types.image_texture,bake_image_name)

            # keep org image if nothing changed
            if bake_image is None:
                org_image = self.D.images.get(tex_node.image.org_image_name)
                tex_node.image = org_image
            else:
                image_functions.save_image(bake_image)
                tex_node.image = bake_image
            
            # -----------------------LINKING--------------------#
            if pbr_input is pbr_inputs["normal_input"]:
                normal_node = first_node_after_input
                normal_node.inputs["Strength"].default_value = 1
                
                        
                if normal_node.type == constants.Node_Types.bump_map:
                    bump_node = normal_node
                    normal_node = node_functions.add_node(bake_material,constants.Shader_Node_Types.normal,"Normal from Bump")
                    normal_node.location = bump_node.location
                    nodes.remove(bump_node)
    
                node_functions.make_link(bake_material, tex_node.outputs[0], normal_node.inputs["Color"])
                node_functions.make_link(bake_material, normal_node.outputs["Normal"], pbr_input)
            else:
                node_functions.make_link(bake_material,tex_node.outputs[0], pbr_input)

            # -----------------------SET COLOR SPACE--------------------#
            if pbr_input is not pbr_inputs["base_color_input"]:
                tex_node.image.colorspace_settings.name = "Non-Color"

        return bake_material


