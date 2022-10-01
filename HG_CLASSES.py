#core
from .core.HG_CALLBACK import HG_LEGACY_ACTIVATE
from .core.settings.HG_PROPS import HG_LEGACY_SETTINGS
from .features.common.HG_COMMON_OPS import (
    HG_LEGACY_CLEAR_SEARCH,
    HG_LEGACY_DELETE,
    HG_LEGACY_DESELECT,
    HG_LEGACY_NEXT_PREV_HUMAN,
    HG_LEGACY_OPENPREF,
    HG_LEGACY_SECTION_TOGGLE,
)
from .features.common.HG_INFO_POPUPS import HG_LEGACY_OT_INFO
from .features.common.HG_RANDOM import HG_LEGACY_COLOR_RANDOM, HG_LEGACY_RANDOM
from .features.creation_phase.HG_BACKUP import HG_LEGACY_REVERT_TO_CREATION
from .features.creation_phase.HG_CREATION import HG_LEGACY_START_CREATION
from .features.creation_phase.HG_FACE import HG_LEGACY_RESET_FACE
from .features.creation_phase.HG_FINISH_CREATION_PHASE import HG_LEGACY_FINISH_CREATION
from .features.creation_phase.HG_HAIR import (
    HG_LEGACY_EYEBROW_SWITCH,
    HG_LEGACY_REMOVE_HAIR,
    HG_LEGACY_TOGGLE_HAIR_CHILDREN,
)
from .features.creation_phase.HG_LENGTH import HG_LEGACY_RANDOM_LENGTH
from .features.finalize_phase.HG_CLOTHING import (
    HG_LEGACY_BACK_TO_HUMAN,
    HG_LEGACY_DELETE_CLOTH,
    HG_LEGACY_OT_PATTERN,
)
from .features.finalize_phase.HG_EXPRESSION import (
    HG_LEGACY_ADD_FRIG,
    HG_LEGACY_REMOVE_FRIG,
    HG_LEGACY_REMOVE_SHAPEKEY,
)
from .features.finalize_phase.HG_POSE import HG_LEGACY_RIGIFY

#user interface
from .user_interface import HG_MAIN_PANEL

#features
    #common
    #creation phase
    #finalize phase
    #utility section

hg_classes = (
    #Add-on backbones
    HG_LEGACY_ACTIVATE,
    
    #Props
    HG_LEGACY_SETTINGS,

    #Panels
    HG_MAIN_PANEL.HG_PT_LEGACY, 
    HG_MAIN_PANEL.HG_PT_ROT_LOC_SCALE_LEGACY,

    #Panel ops
    HG_LEGACY_CLEAR_SEARCH,
    HG_LEGACY_FINISH_CREATION,
    HG_LEGACY_NEXT_PREV_HUMAN,
    HG_LEGACY_RANDOM,
    HG_LEGACY_SECTION_TOGGLE,
    HG_LEGACY_OT_INFO,
    HG_LEGACY_OPENPREF,

    #Model ops
    HG_LEGACY_DELETE,
    HG_LEGACY_DESELECT,   

    #eyes
    HG_LEGACY_EYEBROW_SWITCH,

    #Face
    HG_LEGACY_RESET_FACE,

    #Posing
    HG_LEGACY_RIGIFY,
    
    #Clothing
    HG_LEGACY_BACK_TO_HUMAN,
    HG_LEGACY_OT_PATTERN,
    HG_LEGACY_COLOR_RANDOM,   
    HG_LEGACY_DELETE_CLOTH,

    #Creation
    HG_LEGACY_START_CREATION,
    HG_LEGACY_REVERT_TO_CREATION,

    #Length
    HG_LEGACY_RANDOM_LENGTH,

    #Hair
    HG_LEGACY_TOGGLE_HAIR_CHILDREN,
    HG_LEGACY_REMOVE_HAIR,

    #expression
    HG_LEGACY_REMOVE_SHAPEKEY,
    HG_LEGACY_ADD_FRIG,
    HG_LEGACY_REMOVE_FRIG,

    )
