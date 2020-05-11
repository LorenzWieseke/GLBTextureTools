class Node_Types: 
    image_texture = 'TEX_IMAGE'
    pbr_node = 'BSDF_PRINCIPLED'
    mapping = 'MAPPING'
    normal_map = 'NORMAL_MAP'
    bump_map = 'BUMP'

class Shader_Node_Types:
    emission = "ShaderNodeEmission"
    image_texture = "ShaderNodeTexImage"
    mapping = "ShaderNodeMapping"
    normal = "ShaderNodeNormalMap"
    ao = "ShaderNodeAmbientOcclusion"
    uv = "ShaderNodeUVMap"
    comp_image_node = 'CompositorNodeImage'

class Bake_Types:
    pbr = ["EMISSION"]
    lightmap = ["NOISY", "NRM", "COLOR"]
    ao = ["AO","NRM","COLOR"]
