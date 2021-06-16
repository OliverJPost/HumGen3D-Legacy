"""
Operators and functions used for adding the base human and for reverting to creation phase
"""

import json
import bpy #type: ignore
import os
from pathlib import Path
from sys import platform

from .   HG_NAMEGEN import get_name
from ... features.common.HG_COMMON_FUNC import (
    ShowMessageBox,
    add_to_collection,
    find_human,
    get_prefs
)
from ... core.HG_PCOLL import refresh_pcoll
from .   HG_MATERIAL import male_specific_shader

class HG_START_CREATION(bpy.types.Operator):
    """Imports human, setting the correct custom properties. 
    
    Operator type:
        Object importer
        Prop setter
        Material
    
    Prereq:
        Starting human selected in humans preview collection
    """
    bl_idname = "hg3d.startcreation"
    bl_label = "Generate New Human"
    bl_description = "Generate a new human"
    bl_options = {"UNDO"}

    @classmethod
    def poll (cls, context):
        return context.scene.HG3D.pcoll_humans != 'none'

    def execute(self,context):
        sett = context.scene.HG3D
        sett.ui_phase = 'body'

        hg_rig, _ = self.create_human(context)
        hg_rig.select_set(True)
        context.view_layer.objects.active = hg_rig

        name = self._get_random_name(sett.gender, hg_rig)

        self.report({'INFO'}, "You've created: {}".format(name))
        
        return {'FINISHED'}

    def _get_random_name(self, gender, hg_rig) -> str:
        """Gets a random name for HG_NAMEGEN

        Args:
            gender (str): gender of this human
            hg_rig (Object): armature object of this human

        Returns:
            str: capitalized given name
        """
        #get a list of names that are already taken in this scene
        taken_names = []
        for obj in bpy.data.objects:
            if not obj.HG.ishuman:
                continue
            taken_names.append(obj.name[4:])
        
        #generate name
        name = get_name(gender)

        #get new name if it's already taken
        i=0
        while i<10 and name in taken_names:
            name = get_name(gender)
            i+=1
        
        hg_rig.name = 'HG_' + name

        return name
 

    def create_human(self, context) -> tuple [bpy.types.Object, bpy.types.Object]:
        """Creates a new human based on the selected gender and starting human

        Returns:
            tuple [bpy.types.Object, bpy.types.Object]: 
                hg_rig : Armature of newly created human, used for storing props
                hg_body: Body object of newly created human
        """
        sett = context.scene.HG3D
        pref = get_prefs()

        gender, hg_rig, hg_body, hg_eyes = self._import_human(context, sett, pref)
        self._set_HG_object_props(sett, hg_rig, hg_body)

        self._load_external_shapekeys(context, pref, hg_body)

        context.view_layer.objects.active = hg_rig
        self._set_gender_shapekeys(hg_body, gender)
        
        context.view_layer.objects.active = hg_body
        self.delete_gender_hair(hg_body, gender)
        
        context.view_layer.objects.active = hg_rig

        if platform == 'darwin': #skip beautyspots on MacOS to prevent OpenGL issue
            nodes = hg_body.data.materials[0].node_tree.nodes
            links = hg_body.data.materials[0].node_tree.links
            links.new(nodes['Mix_reroute_1'].outputs[0],
                      nodes['Mix_reroute_2'].inputs[1]
                      )

        #set correct gender specific node group
        if gender == 'male':
            male_specific_shader(hg_body)
            
        mat   = hg_body.data.materials[0]
        nodes = mat.node_tree.nodes
        mat.node_tree.nodes.remove(nodes['Delete_node']) #TODO wtf is this
        
        json_path = pref.filepath + sett.pcoll_humans.replace('jpg', 'json')
        with open(json_path) as json_file:
            preset_data = json.load(json_file)

        context.view_layer.objects.active = hg_rig
        self._configure_human_from_preset(context, sett, gender,
                                                   hg_body, hg_eyes, preset_data)

        #collapse modifiers
        for mod in hg_body.modifiers:
            mod.show_expanded = False

        return hg_rig, hg_body

    def _import_human(self, context, sett, pref) -> tuple[str,
                                                          bpy.types.Object,
                                                          bpy.types.Object,
                                                          bpy.types.Object]:
        """Import human from HG_HUMAN.blend and add it to scene
        Also adds some identifiers to the objects to find them later

        Args:
            sett (PropertyGroup)   : HumGen props
            pref (AddonPreferences): HumGen preferences

        Returns:
            tuple[str, bpy.types.Object*3]: 
                gender  (str)   : gender of the imported human
                hg_rig  (Object): imported armature of human
                hg_body (Object): imported body of human
                hg_eyes (Object): imported eyes of human
        """
        #import from HG_Human file
        blendfile = str(pref.filepath) + str(Path('/models/HG_HUMAN.blend'))
        with bpy.data.libraries.load(blendfile, link = False) as (data_from ,data_to):
            data_to.objects = ['HG_Rig',
                               'HG_Body',
                               'HG_Eyes',
                               'HG_TeethUpper',
                               'HG_TeethLower']

        gender = sett.gender
        
        #link to scene
        hg_rig  = data_to.objects[0]
        hg_body = data_to.objects[1]
        hg_eyes = data_to.objects[2]
        scene   = context.scene
        for obj in data_to.objects: 
            scene.collection.objects.link(obj)
            add_to_collection(context, obj)
      
        hg_rig.location = context.scene.cursor.location 
             
        #set custom properties for identifying
        hg_body['hg_body'] = 1
        hg_eyes['hg_eyes'] = 1
        hg_teeth = [obj for obj in data_to.objects
                    if 'Teeth' in obj.name]
        for tooth in hg_teeth:
            tooth['hg_teeth'] = 1
            
        return gender, hg_rig, hg_body, hg_eyes

    def _set_HG_object_props(self, sett, hg_rig, hg_body):
        """Sets the custom properties to the HG Object propertygroup

        Args:
            sett (PropertyGRoup): HumGen SCENE props
            hg_rig (Object): humgen armature
            hg_body (Object): humgen body
        """
        #custom properties
        HG = hg_rig.HG
        
        HG.ishuman  = True
        HG.gender   = sett.gender
        HG.phase    = 'body'
        HG.body_obj = hg_body
        HG.length   = hg_rig.dimensions[2]

    def _load_external_shapekeys(self, context, pref, hg_body):
        """Imports external shapekeys from the models/shapekeys folder

        Args:
            pref (AddonPreferences): HumGen preferences
            hg_body (Object): Humgen body object
        """
        context.view_layer.objects.active = hg_body
        walker = os.walk(str(pref.filepath) + str(Path('/models/shapekeys')))

        for root, _, filenames in walker:
            for fn in filenames:
                if pref.debug_mode:
                    print(f'EXT SKS: Found {fn} in {root}')
                if not os.path.splitext(fn)[1] == '.blend':
                    continue

                imported_body = self._import_external_sk_human(context, pref,
                                                               root, fn)
                self._transfer_shapekeys(context, hg_body, imported_body)
                
                imported_body.select_set(False)
                bpy.data.objects.remove(imported_body)
        
        hg_body.show_only_shape_key = False

    def _import_external_sk_human(self, context, pref,
                                  root, fn) -> bpy.types.Object:
        """Imports the Humgen body from the passed file in order to import the
        shapekeys on that human

        Args:
            pref (AddonPReferences): HumGen preferences
            root (dir): Root directory the file is in
            fn (str): Filename

        Returns:
            Object: Imported body object
        """
        blendfile = root + str(Path(f'/{fn}'))
        with bpy.data.libraries.load(blendfile, link = False) as (data_from ,data_to):
            data_to.objects = data_from.objects
        if pref.debug_mode:
            print('EXT SK imported:', data_to.objects)
        imported_body = [obj for obj in data_to.objects
                         if obj.name.lower() == 'hg_shapekey'][0] 
        
        context.scene.collection.objects.link(imported_body)
        
        return imported_body

    def _transfer_shapekeys(self, context, hg_body, imported_body):
        """Transfer all non-Basis shapekeys from the passed object to hg_body

        Args:
            hg_body (Object): HumGen body object
            imported_body (Object): imported body object that contains shapekeys
        """
        for obj in context.selected_objects:
            obj.select_set(False)
        hg_body.select_set(True)
        imported_body.select_set(True)
        for idx, sk in enumerate(imported_body.data.shape_keys.key_blocks):
            if sk.name in ['Basis', 'Male']:
                continue
            imported_body.active_shape_key_index = idx
            bpy.ops.object.shape_key_transfer()

    def _set_gender_shapekeys(self, hg_body, gender):
        """Renames shapekeys, removing Male_ and Female_ prefixes according to
        the passed gender

        Args:
            hg_body (Object): HumGen body object
            gender (str): gender of this human
        """
        
        for sk in [sk for sk in hg_body.data.shape_keys.key_blocks]:
            if sk.name.lower().startswith(gender):
                if sk.name != 'Male':
                    GD = gender.capitalize()
                    sk.name = sk.name.replace(f'{GD}_',
                                              ''
                                              )
            
            opposite_gender = 'male' if gender == 'female' else 'female'    
            
            if sk.name.lower().startswith(opposite_gender) and sk.name != 'Male':
                hg_body.shape_key_remove(sk)

    def delete_gender_hair(self, hg_body, gender):
        """Deletes the hair of the opposite gender

        Args:
            hg_body (Object): hg body object
            gender (str): gender of this human
        """
        ps_delete_dict = {
            'female': ('Eyebrows_Male', 'Eyelashes_Male'),
            'male': ('Eyebrows_Female', 'Eyelashes_Female')
        }
        #TODO make into common func
        for ps_name in ps_delete_dict[gender]:
            ps_idx = next(i for i, ps in enumerate(hg_body.particle_systems)
                          if ps.name == ps_name
                     )
            hg_body.particle_systems.active_index = ps_idx
            
            bpy.ops.object.particle_system_remove()  

    def _configure_human_from_preset(self, context, sett, gender,
                                              hg_body, hg_eyes, preset_data):
        """Configures this human according to the preset human that was selected
        by the user. Configuring from imported json 

        Args:
            context ([type]): [description]
            sett (PropertyGroup): HumGen props
            gender (str): gender of human
            hg_body (Object): humgen body object
            hg_eyes (Object): eyes of this human
            preset_data (dict): dictionary of preset data, imported from json
        """
        if preset_data['experimental']:
            bpy.ops.hg3d.experimental()
        
        sett.human_length = preset_data['body_proportions']['length']*100
        sett.chest_size = preset_data['body_proportions']['chest']  

        sks = hg_body.data.shape_keys.key_blocks
        missed_shapekeys = 0
        for sk_name, sk_value in preset_data['shapekeys'].items():
            try:
                sks[sk_name].value = sk_value
            except KeyError:
                missed_shapekeys += 1

        self._load_preset_texture_set(context, sett, gender, preset_data)

        nodes = hg_body.data.materials[0].node_tree.nodes
        for node_name, input_dict in preset_data['material']['node_inputs'].items():
            self._set_preset_node_values(nodes, node_name, input_dict)

        eye_nodes = hg_eyes.data.materials[1].node_tree.nodes
        for node_name, value in preset_data['material']['eyes'].items():
            eye_nodes[node_name].inputs[2].default_value = value

        if 'eyebrows' in preset_data:  
            self._set_preset_eyebrows(hg_body, preset_data)

    def _load_preset_texture_set(self, context, sett, gender, preset_data):
        """Makes the texture set of the starting human preset_data the active
        item in the pcoll_textures, causing it to load

        Args:
            sett (PropertyGroup): HumGen props
            gender (str): gender of this human
            preset_data (dict): dict of preset_data from json
        """
        refresh_pcoll(None, context, 'textures')
        
        texture_name         = preset_data['material']['diffuse']
        texture_library      = preset_data['material']['texture_library']
        sett.texture_library = preset_data['material']['texture_library']
        
        sett.pcoll_textures  = str(Path(
            f'/textures/{gender}/{texture_library}/{texture_name}'
            ) #update function handles the actual texture loading
        )

    def _set_preset_node_values(self, nodes, node_name, input_dict):
        """For each input (key) in the input dict, sets the input.default_value 
        to the value named in the dict

        Args:
            nodes (ShaderNode list): nodes of this material
            node_name (str): name of node to set values for
            input_dict (dict): 
                key (str): name of the input on the passed node
                value (AnyType): value to set as default_value for this input
        """
        node = nodes[node_name]
        for input_name, value in input_dict.items():
            node.inputs[input_name].default_value = value

    def _set_preset_eyebrows(self, hg_body, preset_data):
        """Sets the eyebrow named in preset_data as the only visible eyebrow
        system

        Args:
            hg_body (Object): humgen body obj
            preset_data (dict): preset data dict
        """
        eyebrows = [mod for mod in hg_body.modifiers
                    if mod.type == 'PARTICLE_SYSTEM'
                    and mod.particle_system.name.startswith('Eyebrows')
                    ]
        for mod in eyebrows:
            mod.show_viewport = mod.show_render = False

        preset_eyebrows = next(
            (mod for mod in eyebrows 
                if mod.particle_system.name == preset_data['eyebrows']),
            None
            )
        if not preset_eyebrows:
            ShowMessageBox(message = ('Could not find eyebrows named ' 
                                      + preset_data['eyebrows']))
        else:
            preset_eyebrows.show_viewport = preset_eyebrows.show_render = True

    def hair_children_to_1(self, hg_body):
        #INACTIVE
        for mod in hg_body.modifiers:
            if mod.type == 'PARTICLE_SYSTEM':
                ps_sett = mod.particle_system.settings
                if ps_sett.child_nbr > 1:
                    ps_sett.child_nbr = 1



    




