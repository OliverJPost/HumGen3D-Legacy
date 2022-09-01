import bpy

from ..panel_functions import draw_sub_spoiler
from ..ui_baseclasses import MainPanelPart, subpanel_draw


class HG_PT_EXPRESSION(MainPanelPart, bpy.types.Panel):
    bl_idname = "HG_PT_EXPRESSION"
    phase_name = "expression"

    @subpanel_draw
    def draw(self, context):
        """section for selecting expressions from template_icon_view or adding
        facial rig
        """

        row = self.layout.row(align=True)
        row.scale_y = 1.5
        row.prop(self.sett.ui, "expression_type", expand=True)

        if self.sett.ui.expression_type == "1click":
            self._draw_oneclick_subsection()
        else:
            self._draw_frig_subsection(self.layout)

    def _draw_oneclick_subsection(self):
        if "facial_rig" in self.human.body_obj:
            self.layout.label(text="Library not compatible with face rig")

            col = self.layout.column()
            col.alert = True
            col.scale_y = 1.5
            col.operator(
                "hg3d.removefrig",
                text="Remove facial rig",
                icon="TRASH",
                depress=True,
            )
            return

        self.searchbox(self.sett, "expressions", self.layout)

        self.layout.template_icon_view(
            self.sett.pcoll,
            "expressions",
            show_labels=True,
            scale=10,
            scale_popup=6,
        )

        row_h = self.layout.row(align=True)
        row_h.scale_y = 1.5
        row_h.prop(self.sett.pcoll, "expression_category", text="")
        row_h.operator(
            "hg3d.random", text="Random", icon="FILE_REFRESH"
        ).random_type = "expressions"

        filtered_obj_sks = self.human.body_obj.data.shape_keys
        if filtered_obj_sks:
            self._draw_sk_sliders_subsection(filtered_obj_sks)

    def _draw_sk_sliders_subsection(self, filtered_obj_sks):
        """draws sliders for each non-corrective shapekey to adjust the strength

        Args:
            sett (PropertyGroup): HumGen props
            box (UILayout): layout.box of expression section
            obj_sks (list): list of non-basis and non-corrective shapekeys
        """
        expr_sks = [
            sk
            for sk in filtered_obj_sks.key_blocks
            if sk.name != "Basis"
            and not sk.name.startswith("cor")
            and not sk.name.startswith("eyeLook")
        ]
        if not expr_sks:
            return

        is_open, boxbox = draw_sub_spoiler(
            self.layout, self.sett, "expression_slider", "Strength"
        )
        if not is_open:
            return

        flow = self.get_flow(self.layout, animation=True)
        for sk in self.human.expression.shape_keys:
            display_name = sk.name.replace("expr_", "").replace("_", " ") + ":"

            row = flow.row(align=True)
            row.active = not sk.mute
            row.prop(sk, "value", text=display_name.capitalize())
            row.operator("hg3d.removesk", text="", icon="TRASH").shapekey = sk.name

    def _draw_frig_subsection(self, box):
        """draws subsection for adding facial rig

        Args:
            box (UILayout): layout.box of expression section
        """
        col = box.column()
        if "facial_rig" in self.human.body_obj:
            col.label(text="Facial rig added")
            col.label(text="Use pose mode to adjust", icon="INFO")
            col_h = col.column()
            col_h.scale_y = 1.5
            tutorial_op = col_h.operator(
                "hg3d.draw_tutorial", text="ARKit tutorial", icon="HELP"
            )
            tutorial_op.first_time = False
            tutorial_op.tutorial_name = "arkit_tutorial"
        else:
            col.scale_y = 2
            col.alert = True
            col.operator("hg3d.addfrig", text="Add facial rig", depress=True)