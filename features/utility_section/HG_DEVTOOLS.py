"""
Operators and functions to be used by the developer and content pack creators
"""

import bpy #type: ignore
from ... features.common.HG_COMMON_FUNC import find_human
from ... features.creation_phase.HG_FINISH_CREATION_PHASE import remove_stretch_bones

#REMOVE
class HG_TESTOP(bpy.types.Operator):
    """Operator for testing bits of code
    """
    bl_idname      = "hg3d.testop"
    bl_label       = "Test"
    bl_description = ""
    bl_options     = {"UNDO"}

    def execute(self,context):
        return {'FINISHED'}


#keep
class HG_MASK_PROP(bpy.types.Operator):
    """
    Adds a custom property to the object indicating what mesh mask should be added to the human for this cloth
    """
    bl_idname      = "hg3d.maskprop"
    bl_label       = "Add"
    bl_description = "Adds a custom prop with the name of the mask"
    bl_options     = {"UNDO"}
 
    def execute(self, context):
        obj = context.object
        mask_name = context.scene.HG3D.dev_mask_name
        for i in range(10):
            try:
                mask = obj['mask_{}'.format(i)]
                continue
            except:
                obj['mask_{}'.format(i)] = 'mask_{}'.format(mask_name)
                break
    
        return {'FINISHED'}

#keep
class HG_DELETE_STRETCH(bpy.types.Operator):
    """
    Deletes stretch bones from this human
    """
    bl_idname      = "hg3d.delstretch"
    bl_label       = "Remove stretch bones"
    bl_description = "Removes all stretch bones"
    bl_options     = {"UNDO"}
 
    def execute(self, context):
        hg_rig = find_human(context.object)
        if not hg_rig:
            self.report({'WARNING'}, 'No human selected')
            return {'FINISHED'}
        
        hg_body = hg_rig.HG.body_obj
        
        remove_list = [driver for driver in hg_body.data.shape_keys.animation_data.drivers]

        for driver in remove_list:
            hg_body.data.shape_keys.animation_data.drivers.remove(driver)

        remove_stretch_bones(hg_rig)

        return {'FINISHED'}
