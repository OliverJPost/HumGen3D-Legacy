import bpy #type: ignore
from .. HG_PROP_FUNCTIONS import find_folders, find_item_amount
from .. HG_PCOLL import preview_collections

class HG_UL_CLOTHING(bpy.types.UIList):
    """
    UIList showing clothing libraries
    """   

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        uilist_layout(layout, context, item)

class HG_UL_POSE(bpy.types.UIList):
    """
    UIList showing clothing libraries
    """   

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        uilist_layout(layout, context, item)

class HG_UL_EXPRESSIONS(bpy.types.UIList):
    """
    UIList showing clothing libraries
    """   

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        uilist_layout(layout, context, item)


def uilist_layout(layout, context, item):
    enabledicon = "CHECKBOX_HLT" if item.enabled else "CHECKBOX_DEHLT"
    hg_icons = preview_collections["hg_icons"]
    
    #islockedicon = "LOCKED" if item.islocked else "BLANK1"


    row = layout.row(align = True)
    row.prop(item, "enabled", text="", icon=enabledicon, emboss=False)

    row.label(text=item.library_name)

    subrow = row.row(align = True) 
    try:
        subrow.scale_x = .7
        subrow.label(text= str(item.male_items), icon_value = hg_icons['male_true'].icon_id if item.male_items != 0 else hg_icons['male_false'].icon_id)

        subrow.label(text= str(item.female_items), icon_value = hg_icons['female_true'].icon_id if item.female_items != 0 else hg_icons['female_false'].icon_id)
    except:
        subrow.alignment = 'RIGHT'
        subrow.label(text = str(item.count))


class CLOTHING_ITEM_M(bpy.types.PropertyGroup):
    """
    Properties of the items in the uilist
    """
    library_name: bpy.props.StringProperty(
        name='Library Name',
        description="",
        default= '',
        )  
    enabled: bpy.props.BoolProperty(default = True)
    male_items : bpy.props.IntProperty(default = 0)
    female_items : bpy.props.IntProperty(default = 0)

class POSE_ITEM(bpy.types.PropertyGroup):
    """
    Properties of the items in the uilist
    """
    library_name: bpy.props.StringProperty(
        name='Library Name',
        description="",
        default= '',
        )  
    enabled: bpy.props.BoolProperty(default = True)
    count : bpy.props.IntProperty(default = 0)

class EXPRESSION_ITEM(bpy.types.PropertyGroup):
    """
    Properties of the items in the uilist
    """
    library_name: bpy.props.StringProperty(
        name='Library Name',
        description="",
        default= '',
        )  
    enabled: bpy.props.BoolProperty(default = True)
    count : bpy.props.IntProperty(default = 0)


def uilist_refresh(self, context, categ):
    """
    Refreshes uilist
    """
    add_temp =[]

    if categ == 'outfits':
        collection = context.scene.outfits_col_m
        gender = True
    else:
        if categ == 'poses':
            collection = context.scene.pose_col
        elif categ == 'expressions':
            collection = context.scene.expressions_col
        
        gender = False

    found_folders_male = find_folders(self, context, categ, 'male' if gender else False, include_all = False)

    collection.clear()

    for folder in found_folders_male:
        item = collection.add()
        #['{}_col{}'.format(categ, '' if not gender else '_{}'.format(gender[0]))]
        item.name = folder[0]
        item.library_name = folder[0]
        if gender:
            item.male_items = find_item_amount(context, categ, 'male', folder[0])
        else:
            item.count = find_item_amount(context, categ, False, folder[0])

    if not gender:
        #print(categ, [item for item in collection])
        return

    found_folders_female = find_folders(self, context, categ, 'female', include_all = False)

    for folder in found_folders_female:
        if folder[0] in [item.library_name for item in collection]:
            item = collection[folder[0]]
        else:
            item = collection.add()
            item.name = folder[0]
            item.library_name = folder[0]
        item.female_items = find_item_amount(context, categ, 'female', folder[0])



class HG_REFRESH_UILISTS(bpy.types.Operator):
    """
    clears searchfield
    """
    bl_idname = "hg3d.uilists"
    bl_label = "Refresh"
    bl_description = "Refresh the library list"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self,context):
        uilist_refresh(self, context, 'outfits')
        uilist_refresh(self, context, 'poses')
        uilist_refresh(self, context, 'expressions')

        return {'FINISHED'}