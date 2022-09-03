#core
from .core.content.HG_CONTENT_PACKS import (
    HG_CONTENT_PACK,
    HG_DELETE_CPACK,
    HG_DELETE_INSTALLPACK,
    HG_INSTALL_CPACK,
    HG_INSTALLPACK,
    HG_REFRESH_CPACKS,
    HG_SELECT_CPACK,
    HG_UL_CONTENTPACKS,
    HG_UL_INSTALLPACKS,
    cpacks_refresh,
)
from .core.content.HG_CUSTOM_CONTENT_PACKS import (
    CUSTOM_CONTENT_ITEM,
    HG_OT_CREATE_CPACK,
    HG_OT_EDIT_CPACK,
    HG_OT_EXIT_CPACK_EDIT,
    HG_OT_SAVE_CPACK,
)
from .core.content.HG_UPDATE import UPDATE_INFO_ITEM, check_update
from .core.HG_CALLBACK import HG_ACTIVATE
from .core.settings.HG_PROPS import HG_OBJECT_PROPS, HG_SETTINGS
from .features.common.HG_COMMON_OPS import (
    HG_CLEAR_SEARCH,
    HG_DELETE,
    HG_DESELECT,
    HG_NEXT_PREV_HUMAN,
    HG_NEXTPREV_CONTENT_SAVING_TAB,
    HG_OPENPREF,
    HG_SECTION_TOGGLE,
)
from .features.common.HG_INFO_POPUPS import HG_OT_INFO
from .features.common.HG_RANDOM import HG_COLOR_RANDOM, HG_RANDOM
from .features.creation_phase.HG_BACKUP import HG_REVERT_TO_CREATION
from .features.creation_phase.HG_CREATION import HG_START_CREATION
from .features.creation_phase.HG_FACE import HG_RESET_FACE
from .features.creation_phase.HG_FINISH_CREATION_PHASE import HG_FINISH_CREATION
from .features.creation_phase.HG_HAIR import (
    HG_EYEBROW_SWITCH,
    HG_REMOVE_HAIR,
    HG_TOGGLE_HAIR_CHILDREN,
)
from .features.creation_phase.HG_HAIRCARDS import HG_CONVERT_HAIRCARDS
from .features.creation_phase.HG_LENGTH import HG_RANDOM_LENGTH
from .features.finalize_phase.HG_CLOTHING import (
    HG_BACK_TO_HUMAN,
    HG_DELETE_CLOTH,
    HG_OT_PATTERN,
)
from .features.finalize_phase.HG_EXPRESSION import (
    HG_ADD_FRIG,
    HG_REMOVE_FRIG,
    HG_REMOVE_SHAPEKEY,
)
from .features.finalize_phase.HG_POSE import HG_RIGIFY

#user interface
from .user_interface import HG_MAIN_PANEL

#features
    #common
    #creation phase
    #finalize phase
    #utility section

hg_classes = (
    #Add-on backbones
    HG_ACTIVATE,
    
    #Props
    HG_SETTINGS,
    HG_OBJECT_PROPS,
    
    #Installation & content packs
    HG_CONTENT_PACK,
    HG_UL_CONTENTPACKS,
    HG_REFRESH_CPACKS,
    HG_DELETE_CPACK,
    HG_INSTALL_CPACK,
    HG_INSTALLPACK,
    HG_SELECT_CPACK,
    HG_UL_INSTALLPACKS,
    HG_DELETE_INSTALLPACK,
    
    #Custom content packs
    HG_OT_SAVE_CPACK,
    HG_OT_EDIT_CPACK,
    HG_OT_EXIT_CPACK_EDIT,
    CUSTOM_CONTENT_ITEM,
    HG_OT_CREATE_CPACK,
    
    #Panels
    HG_MAIN_PANEL.HG_PT_PANEL, 
    HG_MAIN_PANEL.HG_PT_ROT_LOC_SCALE,

    #Panel ops
    HG_CLEAR_SEARCH,
    HG_FINISH_CREATION,
    HG_NEXT_PREV_HUMAN,
    HG_RANDOM,
    HG_SECTION_TOGGLE,
    HG_OT_INFO,
    HG_OPENPREF,

    #Model ops
    HG_DELETE,
    HG_DESELECT,   

    #eyes
    HG_EYEBROW_SWITCH,

    #Face
    HG_RESET_FACE,

    #Posing
    HG_RIGIFY,
    
    #Clothing
    HG_BACK_TO_HUMAN,
    HG_OT_PATTERN,
    HG_COLOR_RANDOM,   
    HG_DELETE_CLOTH,

    #Creation
    HG_START_CREATION,
    HG_REVERT_TO_CREATION,

    #Length
    HG_RANDOM_LENGTH,

    #Hair
    HG_TOGGLE_HAIR_CHILDREN,
    HG_REMOVE_HAIR,
    HG_CONVERT_HAIRCARDS,

    #expression
    HG_REMOVE_SHAPEKEY,
    HG_ADD_FRIG,
    HG_REMOVE_FRIG,


    #Update
    UPDATE_INFO_ITEM,

    )
