"""
Operators and functions relating to the posing of the human
"""

import bpy #type: ignore
from pathlib import Path
from ... features.common.HG_COMMON_FUNC import add_to_collection, find_human, get_prefs

class HG_RIGIFY(bpy.types.Operator):
    """Changes the rig to make it compatible with Rigify, then generates the rig
    
    Operator type:
        Pose
        Rigify
    
    Prereq:
        Active object is part of HumGen human
        Human still has normal rig
    """
    bl_idname      = "hg3d.rigify"
    bl_label       = "Generate Rigify Rig"
    bl_description = "Generates a Rigify rig for this human"
    bl_options     = {"REGISTER", "UNDO"}

    def execute(self,context):
        hg_rig  = find_human(context.active_object)
        context.view_layer.objects.active = hg_rig
        hg_body = hg_rig.HG.body_obj
            
        bpy.ops.object.mode_set(mode='POSE')
        for posebone in hg_rig.pose.bones:
            posebone.bone.select = True
        
        bpy.ops.pose.transforms_clear()
        bpy.ops.object.mode_set(mode='OBJECT')

        try:
            bpy.ops.pose.rigify_generate()
        except Exception as e:
            print('Rigify Error:', e)
            self.report({'WARNING'}, 'Something went wrong, please check if Rigify is enabled')
            return {'FINISHED'}
               
        rigify_rig = self._find_created_rigify_rig(context)
        self._rename_vertex_groups(hg_body)
        add_to_collection(context, rigify_rig)
        rigify_rig.name = hg_rig.name + '_RIGIFY'

        self._iterate_children(hg_rig, rigify_rig)
        self._set_HG_props(hg_rig, rigify_rig)

        armature_mod = next(mod for mod in hg_body.modifiers 
                            if mod.type == 'ARMATURE')
        armature_mod.object = rigify_rig

        bpy.data.objects.remove(hg_rig)
        return {'FINISHED'}

    def _rename_vertex_groups(self, obj):
        """Renames vertex groups to match the rigify naming convention"""
        for vg in obj.vertex_groups:
            prefix_list = ('mask', 'pin', 'def-', 'hair', 'fh', 'sim', 'lip')
            if not vg.name.lower().startswith(prefix_list):
                vg.name = 'DEF-' + vg.name    

    def _set_HG_props(self, hg_rig, rigify_rig):
        """Sets the HG props on the new rig to be the same as the old rig

        Args:
            hg_rig (Object): standard HumGen armature
            rigify_rig (Object): Rigify HumGen armature
        """
        new_HG = rigify_rig.HG
        old_HG = hg_rig.HG
        
        new_HG.ishuman  = True
        new_HG.phase    = old_HG.phase
        new_HG.gender   = old_HG.gender
        new_HG.body_obj = old_HG.body_obj
        new_HG.backup   = old_HG.backup
        new_HG.length   = old_HG.length

    def _iterate_children(self, hg_rig, rigify_rig):
        """Iterates over the children of the rig (clothes, eyes etc.) and 
        sets their vertex groups, drivers and armature

        Args:
            hg_rig (Object): old HumGen armature
            rigify_rig (Object): new Rigify humgen armature
        """
        for child in hg_rig.children:
            child.parent = rigify_rig
            child_armature = [mod for mod in child.modifiers if mod.type == 'ARMATURE']
            if child_armature:
                child_armature[0].object = rigify_rig
                self._rename_vertex_groups(child)
                self._correct_drivers(child, rigify_rig)

    def _find_created_rigify_rig(self, context) -> bpy.types.Object:
        """Finds the newly created Rigify rig
        Returns:
            bpy.types.Object: new Rigify rig
        """
        unused_rigify_rigs = [obj for obj 
            in bpy.data.objects 
            if obj.type == 'ARMATURE' 
                and 'rig_id' in obj.data 
                and not obj.children 
                and not 'hg_rigify' in obj.data]  

        for rig in unused_rigify_rigs:
            if rig in context.selected_objects:
                rigify_rig = rig
                rigify_rig.data['hg_rigify'] = 1

        return rigify_rig
    
    def _correct_drivers(self, obj, rigify_rig):
        """Correct the drivers to fit the new bone names

        Args:
            obj (Object): HumGen body object?
            rigify_rig (Object): new Rigify rig
        """
        if not obj.data.shape_keys or not obj.data.shape_keys.animation_data:
            return
        
        for driver in obj.data.shape_keys.animation_data.drivers:            
            var = driver.driver.variables[0]
            target = var.targets[0]
            target.id = rigify_rig    
            target.bone_target = 'DEF-' + target.bone_target        

def load_pose(self, context):
    """Gets called by pcoll_pose to add selected pose to human
    """
    sett = context.scene.HG3D
    pref = get_prefs()
    
    if sett.load_exception:
        return
    hg_rig = find_human(context.active_object)
    hg_pose = _import_pose(context)
    
    _match_rotation_mode(hg_rig, hg_pose, context)
    _match_roll(hg_rig, hg_pose, context)
    
    _copy_pose(context, hg_pose)

    hg_rig.hide_set(False)
    hg_rig.hide_viewport = False

    context.view_layer.objects.active = hg_rig

    hg_pose.select_set(False)
    hg_rig.select_set(True)

    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.paste()

    bpy.ops.object.mode_set(mode='OBJECT')
    
    if not pref.debug_mode:
        bpy.data.objects.remove(hg_pose)

def _import_pose(context) -> bpy.types.Object:
    """Import selected pose object

    Returns:
        bpy.types.Object: Armature containing this pose
    """
    pref = get_prefs()

    blendfile = str(pref.filepath) + context.scene.HG3D.pcoll_poses
    with bpy.data.libraries.load(blendfile, link = False) as (data_from ,data_to):
        data_to.objects = ['HG_Pose']

    hg_pose = data_to.objects[0]
    if not hg_pose:
        print('could not load pose:', context.scene.HG3D.pcoll_poses)
    
    scene = context.scene
    scene.collection.objects.link(hg_pose)
    
    return hg_pose

def _match_roll(hg_rig, hg_pose, context):
    """Some weird issue caused changed to the rig to change the roll values on
    bones. This caused imported poses that still use the original armature to
    not copy properly to the human

    Args:
        hg_rig (Object): HumGen human armature
        hg_pose (Object): imported armature set to a certain pose
    """
    context.view_layer.objects.active = hg_pose
    hg_rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in hg_rig.data.edit_bones:
        b_name = bone.name if bone.name != 'neck' else 'spine.004'
        if b_name in hg_pose.data.edit_bones:
            bone.roll = hg_pose.data.edit_bones[b_name].roll
    bpy.ops.object.mode_set(mode='OBJECT')

def _match_rotation_mode(hg_rig, hg_pose, context):
    context.view_layer.objects.active = hg_pose
    hg_rig.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    for bone in hg_rig.pose.bones:
        b_name = bone.name if bone.name != 'neck' else 'spine.004'
        if b_name in hg_pose.pose.bones:
            print(f'changing {b_name}')
            bone.rotation_mode = hg_pose.pose.bones[b_name].rotation_mode = 'QUATERNION'
    bpy.ops.object.mode_set(mode='OBJECT')
    
def _copy_pose(context, pose):
    """Copies pose from one human to the other

    Args:
        pose (Object): armature to copy from
    """
    for obj in context.selected_objects:
        obj.select_set(False)

    pose.select_set(True)
    context.view_layer.objects.active = pose
    
    bpy.ops.object.mode_set(mode='POSE')
    
    for posebone in pose.pose.bones:
        posebone.bone.select = True
    
    bpy.ops.pose.copy()
    bpy.ops.object.mode_set(mode='OBJECT')