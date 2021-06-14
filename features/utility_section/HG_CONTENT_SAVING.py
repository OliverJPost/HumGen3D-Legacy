import re
import json
from pathlib import Path
import platform
import subprocess
import bpy #type: ignore
import os
from ... features.common.HG_COMMON_FUNC import (
    ShowMessageBox,
    apply_shapekeys,
    find_human,
    get_prefs)
from ... core.HG_SHAPEKEY_CALCULATOR import (
    build_distance_dict,
    deform_obj_from_difference)
from ... features.creation_phase.HG_LENGTH import apply_armature
from .   HG_UTILITY_FUNC import show_message

class Content_Saving_Operator:
    def overwrite_warning(self):
        """Show a warning popup if the file already exists
        """
        layout = self.layout
        col = layout.column(align = True)
        col.label(text = f'"{self.name}" already exists in:')
        col.label(text = self.folder)
        col.separator()
        col.label(text = 'Overwrite?')

    def save_thumb(self, folder, current_name, save_name):
        """Save the thumbnail with this content

        Args:
            folder (Path): folder where to save it
            current_name (str): current name of the image
            save_name (str): name to save the image as
        """
        
        img = bpy.data.images[current_name]
        if current_name != 'Render Result':    
            try:
                img.filepath_raw = str(Path(f'{folder}/{save_name}.jpg'))
                img.file_format  = 'JPEG'
                img.save()
            except RuntimeError as e:
                show_message(self, "Thumbnail image doesn't have any image data")
                print(e)
        else:
            try:
                img.save_render(str(Path(f'{self.folder}/{self.name}.jpg')))
            except RuntimeError:
                show_message(self, 
                    "[Cancelled] Saving render as thumbnail, but render is empty")

    def save_objects_optimized(self, context, objs, folder, filename, 
                               clear_sk = True, clear_materials = True,
                               clear_vg = True, clear_ps = True,
                               run_in_background = True):
        """Saves the passed objects as a new blend file, opening the file in the
        background to make it as small as possible

        Args:
            objs              (list)          : List of objects to save
            folder            (Path)          : Folder to save the file in
            filename          (str)           : Name to save the file as
            clear_sk          (bool, optional): Remove all shapekeys from objs. 
                                                Defaults to True.
            clear_materials   (bool, optional): Remove all materials from objs. 
                                                Defaults to True.
            clear_vg          (bool, optional): Remove all vertex groups from 
                                                objs. Defaults to True.
            clear_ps          (bool, optional): Remove all particle systems from
                                                objs. Defaults to True.
            run_in_background (bool, optional): Open the new subprocess in the 
                                                background. Defaults to True.
        """
        for obj in objs:
            if clear_materials:
                obj.data.materials.clear()
            if clear_vg:
                obj.vertex_groups.clear()  
            if clear_sk:
                self._remove_shapekeys(obj)
            if clear_ps:
                self._remove_particle_systems(context, obj)

        new_scene = bpy.data.scenes.new(name='test_scene')
        new_col   = bpy.data.collections.new(name='HG')
        new_scene.collection.children.link(new_col)
        for obj in objs:
            new_col.objects.link(obj)    

        if not os.path.exists(folder):
            os.makedirs(folder)  

        blend_filepath = os.path.join(folder, f'{filename}.blend')
        bpy.data.libraries.write(blend_filepath, {new_scene})
        
        #CHECK if still works
        python_file = Path(__file__).parent.absolute() + str(Path('/scripts/hg_purge.py'))
        if run_in_background:
            subprocess.Popen([bpy.app.binary_path,
                              blend_filepath,
                              "--background",
                              "--python",
                              python_file])
        else:
            subprocess.Popen([bpy.app.binary_path,
                              blend_filepath,
                              "--python",
                              python_file])
            
        bpy.data.scenes.remove(new_scene)
        for obj in objs:
            bpy.data.objects.remove(obj)

    def _remove_particle_systems(self, context, obj):
        """Remove particle systems from the passed object

        Args:
            obj (Object): obj to remove particle systems from
        """
        context.view_layer.objects.active= obj
        for i, ps in enumerate(obj.particle_systems):   
            obj.particle_systems.active_index = i
            bpy.ops.object.particle_system_remove()

    def _remove_shapekeys(self, obj):
        """Remove shapekeys from the passed object

        Args:
            obj (Object): obj to remove shapekeys from
        """        
        for sk in [sk for sk in obj.data.shape_keys.key_blocks if sk.name != 'Basis']:
            obj.shape_key_remove(sk)
        if obj.data.shape_keys:
            obj.shape_key_remove(obj.data.shape_keys.key_blocks['Basis'])
        
    def remove_number_suffix(self, name) -> str:
        """Remove the number suffix from the passed name 
        (i.e. Box.004 becomes Box)

        Args:
            name (str): name to remove suffix from

        Returns:
            str: name without suffix
        """
        re_suffix = re.search(r'.\d\d\d', name)
        if not re_suffix or not name.endswith(re_suffix.group(0)):
            return name
        else:
            return name.replace(re_suffix.group(0), '')
        
class HG_OT_OPEN_FOLDER(bpy.types.Operator):
    """Open the folder that belongs to this section

    API: False

    Operator type:
        Open subprocess
    
    Prereq:
        subpath passed
    """
    bl_idname      = "hg3d.openfolder"
    bl_label       = "Open folder"
    bl_description = "Opens the folder that belongs to this type of content"

    subpath: bpy.props.StringProperty()

    def execute(self,context):        
        pref = get_prefs()
        path = pref.filepath + str(Path(self.subpath))

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

        return {'FINISHED'}

class HG_OT_SAVE_SHAPEKEY(bpy.types.Operator, Content_Saving_Operator):
    """Save these shapekeys to a separate file. They will be loaded on any 
    newly created human from now on

    Operator type:
        Content saving
        
    Prereq:
        Items in shapekeys_col
        
    Args:
        name (str): internal, does not need to be passed

    """
    bl_idname = "hg3d.saveshapekey"
    bl_label = "Save shapekeys"
    bl_description = "Save shapekeys"

    name: bpy.props.StringProperty()

    def invoke(self, context, event):
        pref            = get_prefs()
        self.sett       = context.scene.HG3D
        self.collection = context.scene.shapekeys_col

        has_selected = next((True for item in self.collection if item.enabled), False)
        if not has_selected:
            show_message(self, 'No shapekeys selected')
            return {'CANCELLED'}

        if not self.sett.shapekey_col_name:
            show_message(self, 'No name given for collection file')
            return {'CANCELLED'}

        self.folder = pref.filepath + str(Path('/models/shapekeys/'))
        self.name = self.sett.shapekey_col_name
        if os.path.isfile(str(Path(f'{self.folder}/{self.name}.blend'))):
            return context.window_manager.invoke_props_dialog(self)

        return self.execute(context)

    def draw(self, context):
        self.overwrite_warning()

    def execute(self,context):        
        hg_rig = find_human(context.object)

        data = [item.sk_name for item in self.collection if item.enabled]
   
        sk_obj      = hg_rig.HG.body_obj.copy()
        sk_obj.data = sk_obj.data.copy()
        sk_obj.name = 'hg_shapekey'
        context.collection.objects.link(sk_obj)
        
        sks_to_remove = [sk for sk in sk_obj.data.shape_keys.key_blocks 
                         if sk.name not in data 
                         and sk.name != 'Basis']
        for sk in sks_to_remove:
            sk_obj.shape_key_remove(sk)
    
        with open((os.path.join(self.folder, f'{self.name}.json')), 'w') as f:
            json.dump(data, f, indent = 4)
        
        self.save_objects_optimized(
            context,
            sk_obj,
            self.folder,
            self.name,
            clear_sk=False
        )

        msg = f'Saved {len(data)} shapekeys to {self.folder}'
        
        self.report({'INFO'}, msg)
        ShowMessageBox(message = msg)
        
        return {'FINISHED'}

class HG_OT_SAVEPRESET(bpy.types.Operator, Content_Saving_Operator):
    """Save the current creation phase human as a starting human

    Operator type:
        Content Saving
        
    Prereq:
        Active object is part of a humgen human
        That humgen human is still in creation phase
        All external dependencies (custom shapekeys, textures) are saved separately
    
    Args:
        name (str): internal, does not need to be passed
    """
    bl_idname      = "hg3d.savepreset"
    bl_label       = "Save as starting human"
    bl_description = "Save as starting human"

    name: bpy.props.StringProperty()

    def invoke(self, context, event):
        pref        = get_prefs()
        self.sett   = context.scene.HG3D
        self.hg_rig = find_human(context.object)

        self.thumb = self.sett.preset_thumbnail_enum
        if not self.thumb and not self.sett.dont_export_thumb:
            show_message(self, 'No thumbnail selected')
            return {'CANCELLED'}
        if not self.sett.preset_name:
            show_message(self, 'No name given for starting human')
            return {'CANCELLED'}

        self.folder = pref.filepath + str(Path(f'/models/{self.hg_rig.HG.gender}/'))
        self.name = self.sett.preset_name
        if os.path.isfile(str(Path(f'{self.folder}/{self.name}.json'))):
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)
    
    def draw(self, context):
        self.overwrite_warning()

    def execute(self,context):        
        hg_rig = self.hg_rig
        folder = self.folder

        hg_body = hg_rig.HG.body_obj
        hg_eyes = [obj for obj in hg_rig.children if 'hg_eyes' in obj]
        
        if not self.sett.dont_export_thumb:
            self.save_thumb(self.folder, self.thumb, self.name)

        preset_data = {}
        preset_data['gender'] = hg_rig.HG.gender
        preset_data['experimental'] = True if hg_rig.HG.experimental else False
        
        eyebrows = [mod for mod in hg_body.modifiers 
                    if mod.type == 'PARTICLE_SYSTEM' 
                    and mod.particle_system.name.startswith('Eyebrows')
                    ]
        preset_data['eyebrows'] = next(
            (mod.particle_system.name for mod in eyebrows 
                if (mod.show_viewport or mod.show_render)
                ),
            f'Eyebrows_{hg_rig.HG.gender.capitalize()}'
            )
        
        #TODO is it even necessary to return the dict back?
        preset_data = self.add_body_proportions(preset_data, hg_rig) 
        preset_data = self.add_shapekeys(preset_data, hg_body)
        preset_data = self.add_material_data(preset_data, hg_body, hg_eyes)
        
        with open(str(Path(f'{folder}/{self.name}.json')), 'w') as f:
            json.dump(preset_data, f, indent = 4)
        
        self.report({'INFO'}, f'Saved starting human {self.name} to {folder}')
        ShowMessageBox(message = f'Saved starting human {self.name} to {folder}')        
        return {'FINISHED'}
    
    def add_body_proportions(self, preset_data, hg_rig) -> dict:
        """Add body proportions to the preset_data dict

        Args:
            preset_data (dict): preset human settings dict
            hg_rig (Object): Armature

        Returns:
            dict: preset_data
        """
        bp_dict = {}
        bp_dict['length'] = hg_rig.dimensions[2]
        
        size = hg_rig.pose.bones['breast.L'].scale[0]
        bp_dict['chest'] = 3*size -2.5
  
        preset_data['body_proportions'] = bp_dict

        return preset_data

    def add_shapekeys(self, preset_data, hg_body) -> dict:
        """Add shapekey data to the preset_data dict

        Args:
            preset_data (dict): preset human settings dict
            hg_rig (Object): Armature

        Returns:
            dict: preset_data
        """        
        sks = hg_body.data.shape_keys.key_blocks
        sk_dict = {sk.name:sk.value for sk in sks 
                   if sk.value != 0 
                   and not sk.name.startswith(('expr',
                                               'cor',
                                               'Basis'))
                   }
        preset_data['shapekeys'] = sk_dict
        
        return preset_data

    def add_material_data(self, preset_data, hg_body, hg_eyes) -> dict:
        """Add material info to the preset_data dict

        Args:
            preset_data (dict): preset human settings dict
            hg_body (Object): HumGen body object
            hg_eyes (Object): HumGen eyes object

        Returns:
            dict: preset_data
        """
        mat_dict = {}
        mat = hg_body.data.materials[0]
        nodes = mat.node_tree.nodes
        
        mat_dict['texture_library'] = (mat['texture_library'] 
                                       if getattr(mat, "texture_library", None) 
                                       else 'Default 4K') 
        
        img_name = nodes['Color'].image.name
        if img_name[-1].isdigit(): #check if ends with duplicate numbers
            img_name = img_name[:-4]
        
        mat_dict['diffuse'] = img_name
        nodegroup_dict = {}
        for node in [node for node in nodes if node.bl_idname == 'ShaderNodeGroup']:
            input_dict = {}
            for input in [inp for inp in node.inputs if not inp.links]:
                inp_value = (
                    tuple(input.default_value) 
                    if str(type(input.default_value)) == "<class 'bpy_prop_array'>" 
                    else input.default_value
                    )
                input_dict[input.name] = inp_value
                
            nodegroup_dict[node.name] = input_dict
        nodename_dict = {
            'Bump': 'Strength',
            'Normal Map': 'Strength',
            'Darken_hsv': 'Value',
            'Lighten_hsv': 'Value'
        }
        
        for nodename, input_name in nodename_dict.items():
            nodegroup_dict[nodename] = {input_name: nodes[nodename].inputs[input_name].default_value,}
        
        mat_dict['node_inputs'] = nodegroup_dict

        eye_mat = hg_eyes[0].data.materials[1]
        eye_nodes = eye_mat.node_tree.nodes
        mat_dict['eyes'] = {
            'HG_Eye_Color': tuple(eye_nodes['HG_Eye_Color'].inputs[2].default_value),
            'HG_Scelera_Color': tuple(eye_nodes['HG_Scelera_Color'].inputs[2].default_value)
        }

        preset_data['material'] = mat_dict

        return preset_data

class HG_OT_SAVEHAIR(bpy.types.Operator, Content_Saving_Operator):
    bl_idname      = "hg3d.savehair"
    bl_label       = "Save as starting human"
    bl_description = "Save as starting human"

    name: bpy.props.StringProperty()


    def invoke(self, context, event):
        pref = get_prefs()
        self.sett = context.scene.HG3D
        self.hg_rig = find_human(context.object)

        self.thumb = self.sett.preset_thumbnail_enum
        if not self.thumb and not self.sett.dont_export_thumb:
            show_message(self, 'No thumbnail selected')
            return {'CANCELLED'}
        if not (self.sett.savehair_male or self.sett.savehair_female):
            show_message(self, 'Select at least one gender')
            return {'CANCELLED'}
        if not self.sett.hairstyle_name:
            show_message(self, 'No name given for hairstyle')
            return {'CANCELLED'}

        self.folder = pref.filepath + str(Path(f'/hair/{self.sett.save_hairtype}/'))
        self.name = self.sett.hairstyle_name
        if os.path.isfile(str(Path(f'{self.folder}/{self.name}.blend'))):
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        self.overwrite_warning()
        
    def execute(self,context):        
        sett = self.sett
        pref = get_prefs()

        hg_rig  = self.hg_rig
        hg_body = hg_rig.HG.body_obj
        col     = context.scene.savehair_col

        hair_obj      = hg_body.copy()
        hair_obj.data = hair_obj.data.copy()
        hair_obj.name = 'HG_Body'
        context.collection.objects.link(hair_obj)

        context.view_layer.objects.active = hair_obj
        hair_obj.select_set(True)
        self._remove_other_systems(hair_obj, [item.ps_name for item in col if item.enabled])

        keep_vgs = self._find_vgs_used_by_hair(hair_obj)
        for vg in [vg for vg in hair_obj.vertex_groups if vg.name not in keep_vgs]:
                hair_obj.vertex_groups.remove(vg)

        genders = [
            gd for gd, enabled 
            in {
                'male': sett.savehair_male,
                'female': sett.savehair_female }.items() 
            if enabled
            ]
        for gender in genders:
            hair_type = sett.save_hairtype
            if hair_type == 'face_hair' and gender == 'female':
                continue

            #TODO this is horrible
            folder = (pref.filepath 
                      + str(Path('hair/{}/{}Custom/'.format(
                                                            hair_type,
                                                            f'{gender}/' 
                                                                if hair_type == 'head' 
                                                            else '')))  
                                                            )
            if not os.path.exists(folder):
                os.makedirs(folder)     
            if not self.sett.dont_export_thumb:
                self.save_thumb(folder, self.thumb, self.name)  
            
            self._make_hair_json(context, hair_obj, folder, self.name)
            
        self.save_objects_optimized(
            context,
            hair_obj,
            self.folder,
            self.name,
            clear_ps=False,
            clear_vg=False
        )
        
        context.view_layer.objects.active= hg_rig
        msg = f'Saved {self.name} to {self.folder}'
        self.report({'INFO'}, msg)
        ShowMessageBox(message = msg)
        return {'FINISHED'}

    def _find_vgs_used_by_hair(self, hair_obj) -> list:
        all_vgs = [vg.name for vg in hair_obj.vertex_groups]
        keep_vgs = []
        for ps in [ps for ps in hair_obj.particle_systems]:
            vg_types = [
                ps.vertex_group_clump,
                ps.vertex_group_density,
                ps.vertex_group_field,
                ps.vertex_group_kink,
                ps.vertex_group_length,
                ps.vertex_group_rotation,
                ps.vertex_group_roughness_1,
                ps.vertex_group_roughness_2,
                ps.vertex_group_roughness_end,
                ps.vertex_group_size,
                ps.vertex_group_tangent,
                ps.vertex_group_twist,
                ps.vertex_group_velocity
                ]
            for used_vg in vg_types:
                if used_vg in all_vgs:
                    keep_vgs.append(used_vg)
        
        return keep_vgs


    def _remove_other_systems(self, obj, keep_list):
        remove_list = [ps.name for ps in obj.particle_systems if ps.name not in keep_list]
           
        for ps_name in remove_list:    
            ps_idx = [i for i, ps in enumerate(obj.particle_systems) if ps.name == ps_name]
            obj.particle_systems.active_index = ps_idx[0]
            bpy.ops.object.particle_system_remove()

    def _make_hair_json(self, context, hair_obj, folder, style_name):
        ps_dict = {}
        for mod in hair_obj.modifiers:
            if mod.type == 'PARTICLE_SYSTEM':
                ps          = mod.particle_system
                ps_length   = ps.settings.child_length
                ps_children = ps.settings.child_nbr
                ps_steps    = ps.settings.display_step
                ps_dict[ps.name] = {"length": ps_length,
                                    "children_amount": ps_children,
                                    "path_steps": ps_steps}

        json_data = {"blend_file": f'{style_name}.blend', "hair_systems": ps_dict}

        full_path = os.path.join(folder, f'{style_name}.json')
        
        with open(full_path, 'w') as f:
            json.dump(json_data, f, indent = 4)

#FIXME male to female not working, other way?
#FIXME texture saving
#FIXME origin to model origin? Correction?
#FIXME shoes corrective shapekeys
class HG_OT_SAVEOUTFIT(bpy.types.Operator, Content_Saving_Operator):
    bl_idname      = "hg3d.saveoutfit"
    bl_label       = "Save as outfit"
    bl_description = "Save as outfit"
    bl_options     = {"UNDO"}

    name: bpy.props.StringProperty()
    alert: bpy.props.StringProperty()

    def execute(self,context):        
        sett = self.sett
        col  = self.col
        objs = [bpy.data.objects[item.obj_name] for item in col]
                  
        genders = []
        if sett.saveoutfit_female:
            genders.append('female')
        if sett.saveoutfit_male:
            genders.append('male')

        for gender in genders:
            gender_folder = self.folder + str(Path(f'/{gender}/Custom'))
            if not self.sett.dont_export_thumb:
                self.save_thumb(gender_folder, self.thumb, self.name)
        
        body_copy = self.hg_rig.HG.body_obj.copy()
        body_copy.data = body_copy.data.copy()
        context.collection.objects.link(body_copy)
        apply_shapekeys(body_copy)
        apply_armature(self.hg_rig, body_copy)
        
        self.save_material_textures(objs)
        obj_distance_dict = {}
        for obj in objs:
            distance_dict = build_distance_dict(body_copy, obj, apply = False) 
            obj_distance_dict[obj.name] = distance_dict
        
 
        for gender in genders:
            export_list = []
            backup_human = next((obj for obj in self.hg_rig.HG.backup.children 
                                 if 'hg_body' in obj))
            if gender == 'male':
                backup_human = backup_human.copy()
                backup_human.data = backup_human.data.copy()
                context.collection.objects.link(backup_human)
                sks = backup_human.data.shape_keys.key_blocks
                for sk in sks:
                    sk.value = 0
                sks['Male'].mute = False
                sks['Male'].value = 1
                apply_shapekeys(backup_human)
            backup_human.hide_viewport = False
            
            for obj in objs:           
                obj_copy = obj.copy()
                obj_copy.data = obj_copy.data.copy()
                if 'cloth' in obj_copy:
                    del obj_copy['cloth']
                context.collection.objects.link(obj_copy)
                distance_dict = obj_distance_dict[obj.name]
                
                deform_obj_from_difference(
                    '',
                    distance_dict,
                    backup_human,
                    obj_copy,
                    as_shapekey=False
                )
                export_list.append(obj_copy)
            
            if gender == 'male':
                bpy.data.objects.remove(backup_human)    
                
            gender_folder = self.folder + str(Path(f'/{gender}/Custom'))
            self.save_objects_optimized(
                context,
                export_list,
                gender_folder,
                self.name,
                clear_sk=False,
                clear_materials=False,
                clear_vg=False,
                run_in_background= not sett.open_exported_outfits
            )
        bpy.data.objects.remove(body_copy)

        show_message(self, 'Succesfully exported outfits')
        return {'FINISHED'}

    def draw(self, context):
        self.overwrite_warning()

    def invoke(self, context, event):
        self.pref   = get_prefs()
        self.sett   = context.scene.HG3D
        self.hg_rig = find_human(self.sett.saveoutfit_human)
        self.col    = context.scene.saveoutfit_col

        self.thumb = self.sett.preset_thumbnail_enum
        if not self.thumb and not self.sett.dont_export_thumb:
            show_message(self, 'No thumbnail selected')
            return {'CANCELLED'}    
        if not self.hg_rig:
            show_message(self, 'No human selected as reference')
            return {'CANCELLED'}
        if not (self.sett.savehair_male or self.sett.savehair_female):
            show_message(self, 'Select at least one gender')
            return {'CANCELLED'}
        if not self.sett.saveoutfit_name:
            show_message(self, 'No name given for outfit')
            return {'CANCELLED'}
        if len(self.col) == 0:
            show_message(self, 'No objects in list')
            return {'CANCELLED'}
        
        obj_list_without_suffix = [self.remove_number_suffix(item.obj_name) for item in self.col]
        if len(obj_list_without_suffix) != len(set(obj_list_without_suffix)):
            show_message(self, 'There are objects in the list which have the same names if suffix like .001 is removed')
            return {'CANCELLED'}            

        self.folder = os.path.join(self.pref.filepath, self.sett.saveoutfit_categ)
        self.name = self.sett.saveoutfit_name
        
        if os.path.isfile(str(Path(f'{self.folder}/{self.hg_rig.HG.gender}/Custom/{self.name}.blend'))):
            self.alert = 'overwrite'
            return context.window_manager.invoke_props_dialog(self)
        
        return self.execute(context)

    #CHECK naming adds .004 to file names, creating duplicates
    def save_material_textures(self, objs):
        saved_images = {}

        for obj in objs:
            for mat in obj.data.materials:
                nodes= mat.node_tree.nodes
                for img_node in [n for n in nodes if n.bl_idname == 'ShaderNodeTexImage']:
                    return self._process_image(saved_images, img_node)

    def _process_image(self, saved_images, img_node):
        img = img_node.image
        colorspace = img.colorspace_settings.name 
        if not img:
            return
        img_path, saved_images = self._save_img(img, saved_images)
        if img_path:
            new_img = bpy.data.images.load(img_path)
            img_node.image = new_img
            new_img.colorspace_settings.name = colorspace
    
    def _save_img(self, img, saved_images) -> tuple[str, list]:
        img_name = self.remove_number_suffix(img.name)
        print('img_name', img_name)
        if img_name in saved_images:
            return saved_images[img_name], saved_images
        
        path = self.pref.filepath + str(Path(f'{self.sett.saveoutfit_categ}/textures/'))
        if not os.path.exists(path):
            os.makedirs(path)  

        full_path = os.path.join(path, img_name)
        img.filepath_raw = full_path
        try:
            img.save()
            saved_images[img_name] = full_path
        except RuntimeError as e:
            print(f'failed to save {img.name} with error {e}')
            return None, saved_images
            
        return full_path, saved_images
