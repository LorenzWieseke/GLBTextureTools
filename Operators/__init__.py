from bpy.utils import register_class, unregister_class
from . import operators

classes = [
    operators.GTT_AddUVOperator,
    operators.GTT_CleanBakesOperator,
    operators.GTT_CleanMaterialsOperator,
    operators.GTT_CleanTexturesOperator,
    operators.GTT_GetMaterialByTextureOperator,
    operators.GTT_NodeToTextureOperator,
    operators.GTT_OpenTexturesFolderOperator,
    operators.GTT_RemoveAOOperator,
    operators.GTT_RemoveLightmapOperator,
    operators.GTT_RemoveUVOperator,
    operators.GTT_ScaleImageOperator,
    operators.GTT_SelectLightmapObjectsOperator,
    operators.GTT_SetActiveUVOperator,
    operators.GTT_SwitchBakeMaterialOperator,
    operators.GTT_SwitchOrgMaterialOperator
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)