from kivymd.uix.picker import MDDatePicker
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string(
    """
#:import calendar calendar
#:import platform platform


<MDDatePicker>
    background: "{}/transparent.png".format(images_path)
    cal_layout: cal_layout
    label_year: label_year
    label_full_date: label_full_date
    size_hint: (None, None)
    size:
        (dp(328), dp(484)) \
        if self.theme_cls.device_orientation == "portrait" \
        else (dp(512), dp(304))
    pos_hint: {"center_x": .5, "center_y": .5}
    canvas:
        Color:
            rgb: app.theme_cls.primary_color
        RoundedRectangle:
            size:
                (dp(328), dp(96)) \
                if self.theme_cls.device_orientation == "portrait" \
                else (dp(168), dp(304))
            pos:
                (root.pos[0], root.pos[1] + root.height - dp(96)) \
                if self.theme_cls.device_orientation == "portrait" \
                else (root.pos[0], root.pos[1] + root.height - dp(304))
            radius: [root.radius[0], root.radius[1], dp(0), dp(0)] \
                    if self.theme_cls.device_orientation == "portrait" \
                    else [root.radius[0], dp(0), dp(0), root.radius[3]]
        Color:
            rgb: app.theme_cls.bg_normal

        RoundedRectangle:
            size:
                (dp(328), dp(484) - dp(96)) \
                if self.theme_cls.device_orientation == "portrait" \
                else [dp(344), dp(304)]
            pos:
                (root.pos[0], root.pos[1] + root.height - dp(96) - (dp(484) - dp(96))) \
                if self.theme_cls.device_orientation == "portrait" \
                else (root.pos[0] + dp(168), root.pos[1])
            radius: [dp(0), dp(0), root.radius[2], root.radius[3]] \
                    if self.theme_cls.device_orientation == "portrait" \
                    else [dp(0), root.radius[1], root.radius[2], dp(0)]

    MDLabel:
        id: label_full_date
        font_style: "H4"
        text_color: root.specific_text_color
        theme_text_color: "Custom"
        size_hint: (None, None)
        size:
            (root.width, dp(30)) \
            if root.theme_cls.device_orientation == "portrait" \
            else (dp(168), dp(30))
        pos:
            (root.pos[0] + dp(23), root.pos[1] + root.height - dp(74)) \
            if root.theme_cls.device_orientation == "portrait" \
            else (root.pos[0] + dp(3), root.pos[1] + dp(214))
        line_height: .84
        valign: "middle"
        text_size:
            (root.width, None) \
            if root.theme_cls.device_orientation == "portrait" \
            else (dp(149), None)
        bold: True
        text:
            root.fmt_lbl_date(root.sel_year, root.sel_month, root.sel_day, \
            root.theme_cls.device_orientation)

    MDLabel:
        id: label_year
        font_style: "Subtitle1"
        text_color: root.specific_text_color
        theme_text_color: "Custom"
        size_hint: (None, None)
        size: root.width, dp(30)
        pos:
            (root.pos[0] + dp(23), root.pos[1] + root.height - dp(40)) \
            if root.theme_cls.device_orientation == "portrait" \
            else (root.pos[0] + dp(16), root.pos[1] + root.height - dp(41))
        valign: "middle"
        text: str(root.sel_year)

    GridLayout:
        id: cal_layout
        cols: 7
        size:
            (dp(44 * 7), dp(40 * 7)) \
            if root.theme_cls.device_orientation == "portrait" \
            else (dp(46 * 7), dp(32 * 7))
        col_default_width:
            dp(42) if root.theme_cls.device_orientation == "portrait" \
            else dp(39)
        size_hint: (None, None)
        padding:
            (dp(2), 0) if root.theme_cls.device_orientation == "portrait" \
            else (dp(7), 0)
        spacing:
            (dp(2), 0) if root.theme_cls.device_orientation == "portrait" \
            else (dp(7), 0)
        pos:
            (root.pos[0] + dp(10), root.pos[1] + dp(60)) \
            if root.theme_cls.device_orientation == "portrait" \
            else (root.pos[0] + dp(168) + dp(8), root.pos[1] + dp(48))

    MDLabel:
        id: label_month_selector
        font_style: "Body2"
        text: calendar.month_name[root.month].capitalize() + " " + str(root.year)
        size_hint: (None, None)
        size: root.width, dp(30)
        pos: root.pos
        pos_hint:
            {"center_x": .5, "center_y": .75} \
            if self.theme_cls.device_orientation == "portrait" \
            else {"center_x": .67, "center_y": .915}
        valign: "middle"
        halign: "center"

    MDIconButton:
        icon: "chevron-left"
        theme_text_color: "Secondary"
        pos_hint:
            {"center_x": .08, "center_y": .745} \
            if root.theme_cls.device_orientation == "portrait" \
            else {"center_x": .53, "center_y": .925}
        on_release: root.change_year("prev")

    MDIconButton:
        icon: "chevron-right"
        theme_text_color: "Secondary"
        pos_hint:
            {"center_x": .92, "center_y": .745} \
            if root.theme_cls.device_orientation == "portrait" \
            else {"center_x": .80, "center_y": .925}
        on_release: root.change_year("next")

    MDIconButton:
        icon: "chevron-left"
        theme_text_color: "Secondary"
        pos_hint:
            {"center_x": .08, "center_y": .745} \
            if root.theme_cls.device_orientation == "portrait" \
            else {"center_x": .39, "center_y": .925}

    MDIconButton:
        icon: "chevron-right"
        theme_text_color: "Secondary"
        pos_hint:
            {"center_x": .92, "center_y": .745} \
            if root.theme_cls.device_orientation == "portrait" \
            else {"center_x": .94, "center_y": .925}

    MDFlatButton:
        width: dp(32)
        id: ok_button
        pos: root.pos[0] + root.size[0] - self.width - dp(10), root.pos[1] + dp(10)
        text: "OK"
        on_release: root.ok_click()

    MDFlatButton:
        id: cancel_button
        pos: root.pos[0] + root.size[0] - self.width - ok_button.width - dp(10), root.pos[1] + dp(10)
        text: "Cancel"
        on_release: root.dismiss()


<DayButton>
    size_hint: None, None
    size:
        (dp(40), dp(40)) if root.theme_cls.device_orientation == "portrait" \
        else (dp(32), dp(32))

    MDLabel:
        font_style: "Caption"
        theme_text_color: "Custom" if root.is_today and not root.is_selected else "Primary"
        text_color: root.theme_cls.primary_color
        opposite_colors:
            root.is_selected if root.owner.sel_month == root.owner.month \
            and root.owner.sel_year == root.owner.year \
            and str(self.text) == str(root.owner.sel_day) else False
        size_hint_x: None
        valign: "middle"
        halign: "center"
        text: root.text


<WeekdayLabel>
    font_style: "Caption"
    theme_text_color: "Secondary"
    size: (dp(40), dp(40)) if root.theme_cls.device_orientation == "portrait" \
        else (dp(32), dp(32))
    size_hint: None, None
    text_size: self.size
    valign:
        "middle" if root.theme_cls.device_orientation == "portrait" \
        else "bottom"
    halign: "center"


<DaySelector>
    size:
        (dp(40), dp(40)) if root.theme_cls.device_orientation == "portrait" \
        else (dp(32), dp(32))
    size_hint: (None, None)

    canvas:
        Color:
            rgba: self.theme_cls.primary_color if self.shown else [0, 0, 0, 0]
        Ellipse:
            size:
                (dp(40), dp(40)) \
                if root.theme_cls.device_orientation == "portrait" \
                else (dp(32), dp(32))
            pos:
                self.pos if root.theme_cls.device_orientation == "portrait" \
                else (self.pos[0], self.pos[1])
"""
)

class CostumeMDDatePicker(MDDatePicker):
    label_year = ObjectProperty()

    def __init__(self, callback, **kwargs):
        super().__init__(callback, **kwargs)
        self.day = 1
        self.mount = 1
        self.year = 2000
        self.set_date(day=self.day, month=self.mount, year=self.year)

    def change_year(self, operation):
        if operation == "next":
            self.year += 1
        else:
            self.year -= 1
        self.update_cal_matrix(self.year, self.month)
        self.set_date(day=self.day, month=self.mount, year=self.year)
