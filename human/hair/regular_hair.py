from HumGen3D.human.hair.basehair import ImportableHair

from HumGen3D.backend import refresh_pcoll
import bpy

from HumGen3D.human.base.decorators import injected_context


class RegularHairSettings(ImportableHair):
    def __init__(self, _human):
        self._human = _human
        self._notstartswith = ("Eye", "ff_")
        self._pcoll_name = "hair"
        self._pcoll_gender_split = True

    @injected_context
    def get_preset_options(self, context=None):
        refresh_pcoll(self, context, "hair", hg_rig=self._human.rig_obj)

        return context.scene.HG3D["previews_list_hair"]
