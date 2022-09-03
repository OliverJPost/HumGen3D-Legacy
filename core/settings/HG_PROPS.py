
import bpy  # type: ignore
from bpy.props import (  # type: ignore
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from ...features.common.HG_COMMON_FUNC import make_path_absolute
from ...features.creation_phase.HG_BODY import scale_bones
from ...features.creation_phase.HG_HAIR import load_hair, update_hair_shader_type
from ...features.creation_phase.HG_LENGTH import update_length
from ...features.creation_phase.HG_MATERIAL import (
    load_textures,
    toggle_sss,
    toggle_underwear,
)
from ...features.finalize_phase.HG_CLOTHING import load_pattern
from ...features.finalize_phase.HG_CLOTHING_LOAD import load_outfit
from ...features.finalize_phase.HG_EXPRESSION import load_expression
from ...features.finalize_phase.HG_POSE import load_pose
from ...user_interface import HG_BATCH_UILIST
from .HG_PROP_FUNCTIONS import (
    add_image_to_thumb_enum,
    find_folders,
    get_resolutions,
    poll_mtc_armature,
    thumbnail_saving_prop_update,
)


class HG_LEGACY_SETTINGS(bpy.types.PropertyGroup):   
    ######### back end #########
    load_exception: BoolProperty(
        name="load_exception",
        default=False)
    subscribed: BoolProperty(
        name="subscribed",
        default=False)
    update_exception: BoolProperty(default = False)

    ######### ui back end ###############
    ui_phase : EnumProperty(
        name="phase",
        items = [
                ("body",            "body",           "", 0),
                ("face",            "face",           "", 1),
                ("skin",            "skin",           "", 2),
                ("hair",            "hair",           "", 3),
                ("length",          "length",         "", 4),
                ("creation_phase",  "Creation Phase", "", 5),
                ("clothing",        "clothing",       "", 6),
                ("footwear",        "footwear",       "", 7),
                ("pose",            "pose",           "", 8),
                ("expression",      "expression",     "", 9),
                ("simulation",      "simulation",     "", 10),
                ("compression",     "compression",    "", 11),
                ("closed",          "closed",         "", 12),
                ("hair2",           "Hair Length",    "", 13),
                ("eyes",            "Eyes",           "", 14),
            ],
        default = "body",
        )   


    ########### ui toggles #################
    #body
    indiv_scale_ui: BoolProperty(name="Individual Scaling", default=False)
    
    #hair
    hair_length_ui : BoolProperty(name="Hair Length", default=False)
    face_hair_ui   : BoolProperty(name="Facial Hair",
                                  description="Click to unfold facial hair ui",
                                  default=False)
    hair_mat_ui    : BoolProperty(name="Hair Material", default=False)
    hair_cards_ui  : BoolProperty(name="Hair Cards", default=False)

    #skin
    makeup_ui      : BoolProperty(default=False)
    beard_shadow_ui: BoolProperty(default=False)
    main_skin_ui   : BoolProperty(default=True)
    light_dark_ui  : BoolProperty(default=False)
    freckles_ui    : BoolProperty(default=False)
    age_ui         : BoolProperty(default=False)
    beautyspots_ui : BoolProperty(default=False)
    eyes_section   : BoolProperty(default=False)
    texture_ui     : BoolProperty(default=True)

    #pose
    pose_choice : EnumProperty(
        name = "posing",
        items = [
                ("library", "Library", "", 0),
                ("rigify",  "Rigify",  "", 1),
            ],
        default = "library",
        )   

    #expression
    expression_slider_ui: BoolProperty(
        name="Expression sliders",
        description="Click to unfold panel",
        default=True)
    expression_type : EnumProperty(
        name="Expression",
        items = [
                ("1click", "1-Click",  "", 0),
                ("frig",   "Face Rig", "", 1),
            ],
        default = "1click",
        )   


    #material mode
    material_ui : BoolProperty(name = "",         default=False)
    pattern_bool: BoolProperty(name = "Bottom",   default=False)
    decal_bool  : BoolProperty(name = "Footwear", default=False)

    #face
    ui_nose   : BoolProperty(name = "Nose",        default=False)
    ui_cheeks : BoolProperty(name = "Cheeks",      default=False)
    ui_eyes   : BoolProperty(name = "Eyes",        default=False)
    ui_l_skull: BoolProperty(name = "Lower Skull", default=False)
    ui_u_skull: BoolProperty(name = "Upper Skull", default=False)
    ui_chin   : BoolProperty(name = "Chin",        default=False)
    ui_ears   : BoolProperty(name = "Ears",        default=False)
    ui_mouth  : BoolProperty(name = "Mouth",       default=False)
    ui_jaw    : BoolProperty(name = "Jaw",         default=False)
    ui_other  : BoolProperty(name = "Other",       default=False)
    ui_custom : BoolProperty(name = "Custom",      default=False)
    ui_presets: BoolProperty(name = "Presets",     default=False)


    thumb_ui: BoolProperty(default=False)

    ############# creation ##############

    human_length: FloatProperty(
        default = 183,
        soft_min = 150,
        soft_max = 200,
        min = 120,
        max = 250,
        update = update_length
        )

    head_size: FloatProperty(
        default = .5,
        soft_min = 0,
        soft_max = 1,
        update = lambda a,b: scale_bones(a,b,"head")
        )
    neck_size: FloatProperty(
        default = .5,
        soft_min = 0,
        soft_max = 1,
        update = lambda a,b: scale_bones(a,b,"neck")
        )
    
    chest_size: FloatProperty(
        default = .5,
        soft_min = 0,
        soft_max = 1,
        update = lambda a,b: scale_bones(a,b,"chest")
        )
    shoulder_size: FloatProperty(
        default = .5,
        soft_min = 0,
        soft_max = 1,
        update = lambda a,b: scale_bones(a,b,"shoulder")
        )
    breast_size: FloatProperty(
        default = .5,
        soft_min = 0,
        soft_max = 1,
        update = lambda a,b: scale_bones(a,b,"breast")
        )
    hips_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a,b: scale_bones(a, b, "hips")
    )
    
    upper_arm_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a,b: scale_bones(a, b, "upper_arm")
    )
    forearm_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a,b: scale_bones(a, b, "forearm")
    )
    hand_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a, b: scale_bones(a, b, "hand")
    )

    thigh_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a, b: scale_bones(a, b, "thigh")
    )
    shin_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a, b: scale_bones(a, b, "shin")
    )
    foot_size: FloatProperty(
        default=.5,
        soft_min=0,
        soft_max=1,
        update=lambda a, b: scale_bones(a, b, "foot")
    )


    ####### preview collections ########
    #creation
    pcoll_humans: EnumProperty(
        items = lambda a,b: get_pcoll_enum_items(a,b,"humans")
        )  

    #posing
    pcoll_poses: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"poses"),
        update = load_pose
        )   
    pose_sub : EnumProperty(
        name="Pose Library",
        items  = lambda a,b: find_folders(a,b,"poses", False),
        update = lambda a,b: refresh_pcoll(a,b,"poses")
        )   
    search_term_poses: StringProperty(
        name='Search:',
        default='',
        update=lambda a, b: refresh_pcoll(a, b, "poses")
    )

    #outfit
    pcoll_outfit: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"outfit"),
        update = lambda a,b: load_outfit(a,b, footwear = False)
        )  
    outfit_sub : EnumProperty(
        name="Outfit Library",
        items  = lambda a,b: find_folders(a,b,'outfits', True),
        update = lambda a,b: refresh_pcoll(a,b,"outfit")
        ) 
    search_term_outfit: StringProperty(
        name='Search:',
        default='',
        update=lambda a, b: refresh_pcoll(a, b, "outfit")
    )

    #hair
    pcoll_hair: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"hair"),
        update = lambda a,b: load_hair(a,b,"head")
        )  
    hair_sub : EnumProperty(
        name="Hair Library",
        items  = lambda a,b: find_folders(a,b,'hair/head', True),
        update = lambda a,b: refresh_pcoll(a,b,"hair")
        ) 
    pcoll_face_hair: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"face_hair"),
        update = lambda a,b: load_hair(a,b,"face")
        )  
    face_hair_sub : EnumProperty(
        name="Facial Hair Library",
        items  = lambda a,b: find_folders(a,b,'hair/face_hair', False),
        update = lambda a,b: refresh_pcoll(a,b,"face_hair")
        ) 

    #expression
    pcoll_expressions: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"expressions"),
        update = load_expression
        )  
    expressions_sub : EnumProperty(
        name="Expressions Library",
        items  = lambda a,b: find_folders(a,b,'expressions', False),
        update = lambda a,b: refresh_pcoll(a,b,"expressions")
        ) 
    search_term_expressions: StringProperty(
        name='Search:',
        default='',
        update=lambda a, b: refresh_pcoll(a, b, "expressions")
    )

    #footwear
    pcoll_footwear: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"footwear"),
        update = lambda a,b: load_outfit(a,b, footwear = True)
        )  
    footwear_sub : EnumProperty(
        name="Footwear Library",
        items  = lambda a,b: find_folders(a,b,'footwear', True),
        update = lambda a,b: refresh_pcoll(a,b,"footwear")
        ) 
    search_term_footwear: StringProperty(
        name='Search:',
        default='',
        update=lambda a, b: refresh_pcoll(a, b, "footwear")
    )

    #patterns
    pcoll_patterns: EnumProperty(
        items = lambda a,b: get_pcoll_enum_items(a,b,"patterns"),
        update = load_pattern
        )  
    patterns_sub : EnumProperty(
        name="Pattern Library",
        items  = lambda a,b: find_folders(a,b,"patterns", False),
        update = lambda a,b: refresh_pcoll(a,b,"patterns")
        )  
    search_term_patterns: StringProperty(
        name='Search:',
        default='',
        update=lambda a, b: refresh_pcoll(a, b, "patterns")
    )

    pcoll_textures: EnumProperty(
        items  = lambda a,b: get_pcoll_enum_items(a,b,"textures"),
        update = load_textures
        )  
    texture_library : EnumProperty(
        name="Texture Library",
        items  = lambda a,b: find_folders(a,b,"textures",
                                          True,
                                          include_all = False),
        update = lambda a,b: refresh_pcoll(a,b,"textures")
        )  
    ######### skin props ###########
    skin_sss: EnumProperty(
        description="Turns on/off subsurface scattering on the skin shader",
        items = [
                ("on",  "On ", "", 0),
                ("off", "Off", "", 1),
            ],
        default = "off",
        update = toggle_sss
        )  

    underwear_switch: EnumProperty(
        description="Turns on/off underwear layer",
        items = [
                ("on",  "On ", "", 0),
                ("off", "Off", "", 1),
            ],
        default = "on",
        update = toggle_underwear
        )          



    
    ######### Dev tools ######## 
    shapekey_calc_type: EnumProperty(
        name="calc type",   
        items = [
                ("pants", "Bottom",    "", 0),
                ("top",   "Top",       "", 1),
                ("shoe",  "Footwear",  "", 2),
                ("full",  "Full Body", "", 3),
            ],
        default = "top",
        )   
    dev_delete_unselected: BoolProperty(name="Delete unselected objs",
                                        default=True)
    dev_tools_ui: BoolProperty(name="Developer tools", default=True)
    calc_gender : BoolProperty(name="Calculate both genders", default=False)
    dev_mask_name: EnumProperty(
        name="mask_name",
        items = [
                ("lower_short", "Lower Short", "", 0),
                ("lower_long",  "Lower Long",  "", 1),
                ("torso",       "Torso",       "", 2),
                ("arms_short",  "Arms Short",  "", 3),
                ("arms_long",   "Arms Long",   "", 4),
                ("foot",        "Foot",        "", 5),
            ],
        default = "lower_short",
        )  

    hair_json_path: StringProperty(subtype = 'FILE_PATH')
    hair_json_name: StringProperty()

    pcoll_render: EnumProperty(
        items = [ 
                ("outfit",          "outfit",          "", 0),
                ("hair",            "hair",            "", 1),
                ("face_hair",       "facial hair",     "", 2),
                ("expressions",     "expressions",     "", 3),
                ("poses",           "poses",           "", 4),
                ("patterns",        "patterns",        "", 5),
                ("randomize_human", "randomize_human", "", 6),
            ],
        default = "outfit"
        )   

    thumb_render_path: StringProperty(
        default = '',
        subtype = 'DIR_PATH'
    )
    dont_export_thumb: BoolProperty(default = False)

    hair_mat_male: EnumProperty(
        name="posing",
        
        items = [
                ("eye",  "Eyebrows & Eyelashes", "", 0),
                ("face", "Facial Hair",          "", 1),
                ("head", "Hair",                 "", 2),
            ],
        default = "eye",
        )   

    hair_mat_female: EnumProperty(
        name="posing",
        
        items = [
                ("eye",  "Eyebrows & Eyelashes", "", 0),
                ("head", "Hair",                 "", 1),
            ],
        default = "eye",
        )   

    hair_shader_type: EnumProperty(
        name="Hair shader type",
        items = [
                ("fast",  "Fast", "", 0),
                ("accurate", "Accurate (Cycles only)", "", 1),
            ],
        default = "fast",
        update = update_hair_shader_type
        )   




