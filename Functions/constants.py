class Node_Types: 
    image_texture = 'TEX_IMAGE'
    pbr_node = 'BSDF_PRINCIPLED'
    mapping = 'MAPPING'
    normal_map = 'NORMAL_MAP'
    bump_map = 'BUMP'
    material_output = 'OUTPUT_MATERIAL'

class Shader_Node_Types:
    emission = "ShaderNodeEmission"
    image_texture = "ShaderNodeTexImage"
    mapping = "ShaderNodeMapping"
    normal = "ShaderNodeNormalMap"
    ao = "ShaderNodeAmbientOcclusion"
    uv = "ShaderNodeUVMap"
    comp_image_node = 'CompositorNodeImage'
    mix ="ShaderNodeMixRGB"


class Bake_Passes:
    pbr = ["EMISSION"]
    lightmap = ["NOISY", "NRM", "COLOR"]
    ao = ["AO","COLOR"]
    
class Material_Suffix:
    bake_type_mat_suffix = {
        "pbr" : "_Bake",
        "ao" : "_AO"
    }


