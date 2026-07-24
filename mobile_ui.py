"""Professional Kivy interface for the Android calculator build.

Designed by Hussain Babar
"""

from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from calculator import (
    AngleMode,
    CalculatorError,
    evaluate_expression,
    format_number,
    statistics_summary,
)
from converter import CURRENCY_CODES, CurrencyConverter, UNIT_CATEGORIES, convert_unit
from history import HistoryManager
from settings import SettingsStore


THEMES = {
    "Dark": {
        "background": (0.020, 0.035, 0.067, 1),
        "surface": (0.043, 0.071, 0.125, 1),
        "surface_alt": (0.065, 0.102, 0.169, 1),
        "surface_pressed": (0.090, 0.140, 0.225, 1),
        "accent": (0.102, 0.443, 0.831, 1),
        "accent_pressed": (0.075, 0.345, 0.680, 1),
        "cyan": (0.145, 0.800, 0.925, 1),
        "danger": (0.890, 0.255, 0.310, 1),
        "danger_pressed": (0.720, 0.170, 0.225, 1),
        "success": (0.180, 0.820, 0.600, 1),
        "text": (0.945, 0.969, 1, 1),
        "muted": (0.570, 0.660, 0.760, 1),
        "line": (0.110, 0.175, 0.275, 1),
    },
    "Light": {
        "background": (0.914, 0.941, 0.969, 1),
        "surface": (1, 1, 1, 1),
        "surface_alt": (0.855, 0.910, 0.957, 1),
        "surface_pressed": (0.760, 0.850, 0.930, 1),
        "accent": (0.030, 0.494, 0.686, 1),
        "accent_pressed": (0.020, 0.390, 0.560, 1),
        "cyan": (0.000, 0.550, 0.720, 1),
        "danger": (0.820, 0.180, 0.240, 1),
        "danger_pressed": (0.680, 0.110, 0.170, 1),
        "success": (0.050, 0.590, 0.400, 1),
        "text": (0.055, 0.120, 0.200, 1),
        "muted": (0.300, 0.400, 0.500, 1),
        "line": (0.650, 0.740, 0.830, 1),
    },
    "AMOLED": {
        "background": (0, 0, 0, 1),
        "surface": (0.030, 0.035, 0.045, 1),
        "surface_alt": (0.070, 0.085, 0.110, 1),
        "surface_pressed": (0.105, 0.135, 0.180, 1),
        "accent": (0.000, 0.400, 0.950, 1),
        "accent_pressed": (0.000, 0.300, 0.760, 1),
        "cyan": (0.000, 0.900, 1.000, 1),
        "danger": (0.930, 0.170, 0.270, 1),
        "danger_pressed": (0.730, 0.100, 0.180, 1),
        "success": (0.100, 0.900, 0.570, 1),
        "text": (0.980, 0.990, 1, 1),
        "muted": (0.550, 0.610, 0.690, 1),
        "line": (0.130, 0.160, 0.210, 1),
    },
    "Neon Blue": {
        "background": (0.012, 0.035, 0.090, 1),
        "surface": (0.025, 0.085, 0.180, 1),
        "surface_alt": (0.055, 0.125, 0.285, 1),
        "surface_pressed": (0.080, 0.180, 0.390, 1),
        "accent": (0.000, 0.380, 1.000, 1),
        "accent_pressed": (0.000, 0.270, 0.800, 1),
        "cyan": (0.345, 0.925, 1.000, 1),
        "danger": (0.920, 0.170, 0.340, 1),
        "danger_pressed": (0.720, 0.100, 0.250, 1),
        "success": (0.160, 0.900, 0.640, 1),
        "text": (0.940, 0.970, 1, 1),
        "muted": (0.570, 0.700, 0.850, 1),
        "line": (0.100, 0.270, 0.560, 1),
    },
}

COLORS = dict(THEMES["Dark"])


def apply_color_theme(name: str) -> None:
    """Update the palette used when constructing mobile widgets."""

    COLORS.clear()
    COLORS.update(THEMES.get(name, THEMES["Dark"]))


class Surface(BoxLayout):
    """Rounded layout used for cards and panels."""

    background_color = ListProperty(COLORS["surface"])

    def __init__(self, radius=18, **kwargs):
        self._radius = dp(radius)
        kwargs.setdefault("background_color", COLORS["surface"])
        super().__init__(**kwargs)
        with self.canvas.before:
            self._canvas_color = Color(rgba=self.background_color)
            self._canvas_shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self._radius],
            )
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            background_color=self._update_canvas,
        )

    def _update_canvas(self, *_):
        self._canvas_color.rgba = self.background_color
        self._canvas_shape.pos = self.pos
        self._canvas_shape.size = self.size
        self._canvas_shape.radius = [self._radius]


class ProfessionalButton(Button):
    """Elevated rounded button with border and reliable touch feedback."""

    normal_color = ListProperty(COLORS["surface_alt"])
    pressed_color = ListProperty(COLORS["surface_pressed"])

    def __init__(self, radius=14, **kwargs):
        self._radius = dp(radius)
        kwargs.setdefault("normal_color", COLORS["surface_alt"])
        kwargs.setdefault("pressed_color", COLORS["surface_pressed"])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", COLORS["text"])
        kwargs.setdefault("font_size", sp(14))
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        with self.canvas.before:
            self._shadow_color = Color(rgba=(0, 0, 0, 0.28))
            self._shadow_shape = RoundedRectangle(
                pos=(self.x, self.y - dp(3)),
                size=self.size,
                radius=[self._radius],
            )
            self._canvas_color = Color(rgba=self.normal_color)
            self._canvas_shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self._radius],
            )
        with self.canvas.after:
            self._border_color = Color(rgba=COLORS["line"])
            self._border_shape = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self._radius,
                ),
                width=dp(0.8),
            )
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            state=self._update_canvas,
            normal_color=self._update_canvas,
            pressed_color=self._update_canvas,
        )

    def _update_canvas(self, *_):
        is_pressed = self.state == "down"
        self._canvas_color.rgba = self.pressed_color if is_pressed else self.normal_color
        self._shadow_color.rgba = (0, 0, 0, 0.10 if is_pressed else 0.28)
        self._shadow_shape.pos = (
            self.x,
            self.y - (dp(1) if is_pressed else dp(3)),
        )
        self._shadow_shape.size = self.size
        self._shadow_shape.radius = [self._radius]
        self._canvas_shape.pos = self.pos
        self._canvas_shape.size = self.size
        self._canvas_shape.radius = [self._radius]
        self._border_color.rgba = (
            (0.18, 0.48, 0.78, 0.85) if is_pressed else COLORS["line"]
        )
        self._border_shape.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self._radius,
        )

    def set_active(self, active: bool) -> None:
        self.normal_color = COLORS["accent"] if active else COLORS["surface"]
        self.pressed_color = (
            COLORS["accent_pressed"] if active else COLORS["surface_pressed"]
        )
        self.color = COLORS["text"] if active else COLORS["muted"]


class MobileCalculator(BoxLayout):
    """Responsive phone interface for all calculator tools."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            padding=(dp(10), dp(6), dp(10), dp(5)),
            **kwargs,
        )
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        if self.settings.theme not in THEMES:
            self.settings.theme = "Dark"
        apply_color_theme(self.settings.theme)
        from kivy.core.window import Window

        Window.clearcolor = COLORS["background"]
        self.ans = 0.0
        self.history = HistoryManager()
        self.currency = CurrencyConverter()
        self.current_page = "Calculator"
        self.menu: DropDown | None = None
        self.page_callbacks = {
            "Calculator": self.show_calculator,
            "Unit Converter": self.show_units,
            "Statistics": self.show_stats,
            "Currency Converter": self.show_currency,
            "History": self.show_history,
            "Themes": self.show_themes,
            "Settings": self.show_settings,
            "Precision Pro": self.show_pro,
        }

        self._build_shell()
        self.show_calculator()

    def _build_shell(self) -> None:
        self.expression = self._text_input(
            hint="Enter an expression",
            font_size=sp(18),
            height=dp(36),
            halign="right",
        )
        self.result = self._label(
            "0",
            font_size=sp(31),
            color=COLORS["text"],
            halign="right",
            height=dp(42),
        )
        self.status = self._label(
            "Ready",
            font_size=sp(11),
            color=COLORS["muted"],
            halign="right",
            height=dp(18),
        )

        self.add_widget(self._build_header())
        self.content = BoxLayout(orientation="vertical")
        self.add_widget(self.content)
        self.add_widget(
            self._label(
                "Designed by Hussain Babar",
                font_size=sp(10),
                color=COLORS["muted"],
                halign="center",
                height=dp(19),
                bold=True,
            )
        )

    # ---------- Shared UI helpers ----------

    def _label(
        self,
        text: str,
        *,
        font_size=sp(14),
        color=None,
        halign="left",
        valign="middle",
        height=None,
        bold=False,
    ) -> Label:
        if color is None:
            color = COLORS["text"]
        label = Label(
            text=text,
            font_size=font_size,
            color=color,
            halign=halign,
            valign=valign,
            bold=bold,
        )
        if height is not None:
            label.size_hint_y = None
            label.height = height
        label.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        return label

    def _text_input(
        self,
        *,
        text="",
        hint="",
        font_size=sp(17),
        height=dp(50),
        halign="left",
        input_filter=None,
    ) -> TextInput:
        return TextInput(
            text=text,
            hint_text=hint,
            multiline=False,
            font_size=font_size,
            size_hint_y=None,
            height=height,
            halign=halign,
            foreground_color=COLORS["text"],
            hint_text_color=COLORS["muted"],
            cursor_color=COLORS["cyan"],
            background_normal="",
            background_active="",
            background_color=COLORS["surface_alt"],
            padding=(dp(13), dp(13)),
            input_filter=input_filter,
        )

    def _spinner(self, text: str, values, height=dp(50)) -> Spinner:
        return Spinner(
            text=text,
            values=tuple(values),
            size_hint_y=None,
            height=height,
            font_size=sp(14),
            color=COLORS["text"],
            background_normal="",
            background_color=COLORS["surface_alt"],
        )

    def _button(
        self,
        text: str,
        *,
        height=dp(50),
        color=None,
        pressed=None,
        font_size=sp(14),
    ) -> ProfessionalButton:
        button = ProfessionalButton(
            text=text,
            size_hint_y=None,
            height=height,
            font_size=font_size,
        )
        if color is not None:
            button.normal_color = color
        if pressed is not None:
            button.pressed_color = pressed
        return button

    def _field_group(self, title: str, widget) -> BoxLayout:
        group = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            height=dp(76),
        )
        group.add_widget(
            self._label(
                title.upper(),
                font_size=sp(10),
                color=COLORS["muted"],
                height=dp(18),
            )
        )
        group.add_widget(widget)
        return group

    def _page_title(self, title: str, subtitle: str) -> BoxLayout:
        block = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(1),
        )
        block.add_widget(
            self._label(title, font_size=sp(21), bold=True, height=dp(31))
        )
        block.add_widget(
            self._label(
                subtitle,
                font_size=sp(11),
                color=COLORS["muted"],
                height=dp(22),
            )
        )
        return block

    def _scroll_page(self) -> tuple[ScrollView, BoxLayout]:
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        body = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(0, dp(2), 0, dp(8)),
            size_hint_y=None,
        )
        body.bind(minimum_height=body.setter("height"))
        scroll.add_widget(body)
        return scroll, body

    def _build_header(self) -> BoxLayout:
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        title_block = BoxLayout(orientation="vertical", spacing=0)
        title_block.add_widget(
            self._label(
                "PRECISION",
                font_size=sp(10),
                color=COLORS["cyan"],
                height=dp(17),
                bold=True,
            )
        )
        self.header_title = self._label(
            "Calculator",
            font_size=sp(21),
            color=COLORS["text"],
            height=dp(30),
            bold=True,
        )
        title_block.add_widget(self.header_title)
        header.add_widget(title_block)

        self.credit_button = ProfessionalButton(
            text="",
            size_hint=(None, None),
            size=(dp(88), dp(32)),
            font_size=sp(9),
            radius=16,
            normal_color=COLORS["surface"],
            pressed_color=COLORS["surface_pressed"],
            color=COLORS["cyan"],
        )
        self.credit_button.bind(on_release=self.show_pro)
        header.add_widget(self.credit_button)

        menu_button = ProfessionalButton(
            text="...",
            size_hint=(None, None),
            size=(dp(42), dp(32)),
            font_size=sp(18),
            radius=16,
            normal_color=COLORS["surface"],
            pressed_color=COLORS["surface_pressed"],
        )
        menu_button.bind(on_release=self.open_overflow_menu)
        header.add_widget(menu_button)
        self._update_credit_badge()
        return header

    def open_overflow_menu(self, anchor):
        if self.menu is not None:
            self.menu.dismiss()
        menu = DropDown(auto_width=False, width=dp(218))
        for name, callback in self.page_callbacks.items():
            button = Button(
                text=name,
                size_hint_y=None,
                height=dp(46),
                font_size=sp(13),
                bold=name == self.current_page,
                color=COLORS["cyan"] if name == self.current_page else COLORS["text"],
                background_normal="",
                background_down="",
                background_color=(
                    COLORS["surface_pressed"]
                    if name == self.current_page
                    else COLORS["surface"]
                ),
            )

            def select_page(_, action=callback):
                menu.dismiss()
                action()

            button.bind(on_release=select_page)
            menu.add_widget(button)
        self.menu = menu
        menu.bind(on_dismiss=lambda *_: setattr(self, "menu", None))
        menu.open(anchor)

    def _activate_page(self, page_name: str) -> None:
        self.current_page = page_name
        if hasattr(self, "header_title"):
            self.header_title.text = page_name
        if self.menu is not None:
            self.menu.dismiss()

    def _update_credit_badge(self) -> None:
        if not hasattr(self, "credit_button"):
            return
        if self.settings.is_pro:
            self.credit_button.text = "PRO ACTIVE"
            self.credit_button.normal_color = COLORS["success"]
            self.credit_button.color = COLORS["text"]
        else:
            self.credit_button.text = f"{self.settings.credits_remaining} CREDITS"
            self.credit_button.normal_color = COLORS["surface"]
            self.credit_button.color = COLORS["cyan"]
        self.credit_button.pressed_color = COLORS["surface_pressed"]

    def _has_credit(self) -> bool:
        if self.settings.is_pro or self.settings.credits_remaining > 0:
            return True
        self._show_credit_limit()
        return False

    def _consume_credit(self) -> None:
        if self.settings.is_pro:
            return
        self.settings.credits_remaining = max(
            0,
            self.settings.credits_remaining - 1,
        )
        self.settings_store.save()
        self._update_credit_badge()

    def _show_credit_limit(self) -> None:
        box = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(14),
        )
        box.add_widget(
            self._label(
                "Your 100 free credits are finished.\nUpgrade to Pro for unlimited use.",
                font_size=sp(14),
                halign="center",
            )
        )
        actions = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(46))
        close = self._button("Close", height=dp(46))
        upgrade = self._button(
            "View Pro",
            height=dp(46),
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
        )
        actions.add_widget(close)
        actions.add_widget(upgrade)
        box.add_widget(actions)
        popup = Popup(
            title="Credit limit reached",
            content=box,
            size_hint=(0.88, None),
            height=dp(235),
            auto_dismiss=False,
        )
        close.bind(on_release=popup.dismiss)

        def open_pro(*_):
            popup.dismiss()
            self.show_pro()

        upgrade.bind(on_release=open_pro)
        popup.open()

    # ---------- Calculator ----------

    def show_calculator(self, *_):
        self._activate_page("Calculator")
        self.content.clear_widgets()
        page = BoxLayout(orientation="vertical", spacing=dp(6))

        display = Surface(
            orientation="vertical",
            size_hint_y=None,
            height=dp(138),
            padding=(dp(12), dp(8)),
            spacing=dp(1),
            radius=16,
        )
        display_top = BoxLayout(size_hint_y=None, height=dp(18))
        display_top.add_widget(
            self._label(
                "EXPRESSION",
                font_size=sp(9),
                color=COLORS["muted"],
                bold=True,
            )
        )
        self.angle_button = ProfessionalButton(
            text=self.settings.angle_mode,
            size_hint=(None, None),
            size=(dp(54), dp(22)),
            font_size=sp(9),
            radius=11,
            normal_color=COLORS["accent"],
            pressed_color=COLORS["accent_pressed"],
        )
        self.angle_button.bind(on_release=self.cycle_angle_mode)
        display_top.add_widget(self.angle_button)
        display.add_widget(display_top)
        display.add_widget(self.expression)
        display.add_widget(self.result)
        display.add_widget(self.status)
        page.add_widget(display)

        keypad = GridLayout(cols=4, spacing=dp(6), padding=(0, dp(1)))
        keys = (
            "AC", "DEL", "(", ")",
            "sin", "cos", "tan", "sqrt",
            "log", "ln", "x²", "x!",
            "π", "e", "ANS", "1/x",
            "7", "8", "9", "÷",
            "4", "5", "6", "×",
            "1", "2", "3", "−",
            "0", ".", "%", "+",
        )
        for key in keys:
            normal = COLORS["surface_alt"]
            pressed = COLORS["surface_pressed"]
            text_color = COLORS["text"]
            if key == "AC":
                normal, pressed = COLORS["danger"], COLORS["danger_pressed"]
            elif key in {"÷", "×", "−", "+", "(", ")"}:
                normal, pressed = COLORS["accent"], COLORS["accent_pressed"]
            elif key in {
                "sin", "cos", "tan", "sqrt", "log", "ln",
                "x²", "x!", "π", "e", "ANS", "1/x",
            }:
                normal = COLORS["surface"]
                text_color = COLORS["cyan"]
            button = ProfessionalButton(
                text=key,
                font_size=sp(15),
                normal_color=normal,
                pressed_color=pressed,
                color=text_color,
            )
            button.bind(on_release=lambda _, value=key: self.press(value))
            keypad.add_widget(button)
        page.add_widget(keypad)

        equals = self._button(
            "=",
            height=dp(48),
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
            font_size=sp(22),
        )
        equals.bind(on_release=lambda *_: self.press("="))
        page.add_widget(equals)
        self.content.add_widget(page)

    def cycle_angle_mode(self, *_):
        modes = [mode.value for mode in AngleMode]
        try:
            index = modes.index(self.settings.angle_mode)
        except ValueError:
            index = -1
        self.settings.angle_mode = modes[(index + 1) % len(modes)]
        self.settings_store.save()
        self.angle_button.text = self.settings.angle_mode
        self.status.text = f"Angle mode: {self.settings.angle_mode}"

    def press(self, key: str):
        if key == "AC":
            self.expression.text = ""
            self.result.text = "0"
            self.status.text = "Ready"
        elif key == "DEL":
            self.expression.text = self.expression.text[:-1]
        elif key == "=":
            try:
                if not self._has_credit():
                    self.status.text = "No credits remaining"
                    return
                mode = AngleMode(self.settings.angle_mode)
                value = evaluate_expression(
                    self.expression.text,
                    angle_mode=mode,
                    ans=self.ans,
                )
                self.ans = value
                self.result.text = format_number(value)
                self.history.add(
                    self.expression.text,
                    self.result.text,
                    self.settings.angle_mode,
                )
                self._consume_credit()
                if self.settings.is_pro:
                    self.status.text = "Calculation saved to history"
                else:
                    self.status.text = (
                        f"Saved to history | {self.settings.credits_remaining} credits left"
                    )
            except (CalculatorError, ValueError) as exc:
                self.result.text = "Error"
                self.status.text = str(exc)
        elif key == "π":
            self.expression.text += "π"
        elif key == "ANS":
            self.expression.text += "ANS"
        elif key == "x²":
            self.expression.text = f"({self.expression.text})^2"
        elif key == "x!":
            self.expression.text = f"factorial({self.expression.text})"
        elif key == "1/x":
            self.expression.text = f"reciprocal({self.expression.text})"
        elif key in {"sin", "cos", "tan", "log", "ln", "sqrt"}:
            self.expression.text += f"{key}("
        elif key == "%":
            self.expression.text = f"({self.expression.text})/100"
        else:
            self.expression.text += key

    # ---------- Unit converter ----------

    def show_units(self, *_):
        self._activate_page("Units")
        self.content.clear_widgets()
        scroll, body = self._scroll_page()
        body.add_widget(
            self._page_title("Unit Converter", "Convert measurements accurately")
        )

        category = self._spinner("Length", UNIT_CATEGORIES)
        value = self._text_input(text="1", input_filter="float")
        source = self._spinner("Meter", UNIT_CATEGORIES["Length"])
        target = self._spinner("Kilometer", UNIT_CATEGORIES["Length"])

        fields = Surface(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12),
            size_hint_y=None,
            height=dp(328),
        )
        fields.add_widget(self._field_group("Category", category))
        fields.add_widget(self._field_group("Amount", value))
        pair = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(76))
        pair.add_widget(self._field_group("From", source))
        pair.add_widget(self._field_group("To", target))
        fields.add_widget(pair)

        def category_changed(_, selected):
            units = list(UNIT_CATEGORIES[selected])
            source.values = tuple(units)
            target.values = tuple(units)
            source.text = units[0]
            target.text = units[min(1, len(units) - 1)]

        category.bind(text=category_changed)
        convert_button = self._button(
            "Convert Units",
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
        )
        fields.add_widget(convert_button)
        body.add_widget(fields)

        output = self._label(
            "Result will appear here",
            font_size=sp(24),
            color=COLORS["cyan"],
            halign="center",
        )
        result_card = Surface(
            orientation="vertical",
            padding=dp(12),
            size_hint_y=None,
            height=dp(92),
            background_color=COLORS["surface_alt"],
        )
        result_card.add_widget(output)
        body.add_widget(result_card)
        convert_button.bind(
            on_release=lambda *_: self.convert_unit_value(
                category, value, source, target, output
            )
        )
        self.content.add_widget(scroll)

    def convert_unit_value(self, category, value, source, target, output):
        try:
            if not self._has_credit():
                output.text = "No credits remaining"
                return
            converted = convert_unit(
                category.text,
                float(value.text),
                source.text,
                target.text,
            )
            output.text = f"{format_number(converted)} {target.text}"
            self._consume_credit()
        except (CalculatorError, ValueError):
            output.text = "Enter a valid value"

    # ---------- Statistics ----------

    def show_stats(self, *_):
        self._activate_page("Stats")
        self.content.clear_widgets()
        scroll, body = self._scroll_page()
        body.add_widget(
            self._page_title("Statistics", "Instant summary for your number set")
        )
        values = self._text_input(
            hint="Example: 12, 18, 24, 30",
            font_size=sp(16),
        )
        input_card = Surface(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12),
            size_hint_y=None,
            height=dp(145),
        )
        input_card.add_widget(self._field_group("Values", values))
        analyze_button = self._button(
            "Analyze Data",
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
        )
        input_card.add_widget(analyze_button)
        body.add_widget(input_card)

        output = self._label(
            "Add numbers separated by commas.",
            font_size=sp(15),
            color=COLORS["text"],
            valign="top",
        )
        result_card = Surface(
            orientation="vertical",
            padding=dp(15),
            size_hint_y=None,
            height=dp(205),
            background_color=COLORS["surface_alt"],
        )
        result_card.add_widget(output)
        body.add_widget(result_card)
        analyze_button.bind(on_release=lambda *_: self.analyze(values, output))
        self.content.add_widget(scroll)

    def analyze(self, values, output):
        try:
            if not self._has_credit():
                output.text = "No credits remaining"
                return
            numbers = [
                float(item.strip())
                for item in values.text.split(",")
                if item.strip()
            ]
            summary = statistics_summary(numbers)
            output.text = "\n".join(
                f"{key.upper()}\n{value}" for key, value in summary.items()
            )
            self._consume_credit()
        except (CalculatorError, ValueError) as exc:
            output.text = str(exc)

    # ---------- Currency ----------

    def show_currency(self, *_):
        self._activate_page("Currency")
        self.content.clear_widgets()
        scroll, body = self._scroll_page()
        body.add_widget(
            self._page_title("Currency Converter", "Live rates with offline backup")
        )

        amount = self._text_input(text="1", input_filter="float")
        source = self._spinner(
            self.settings.last_currency_from or "USD",
            CURRENCY_CODES,
        )
        target = self._spinner(
            self.settings.last_currency_to or "EUR",
            CURRENCY_CODES,
        )
        fields = Surface(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12),
            size_hint_y=None,
            height=dp(250),
        )
        fields.add_widget(self._field_group("Amount", amount))
        pair = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(76))
        pair.add_widget(self._field_group("From", source))
        pair.add_widget(self._field_group("To", target))
        fields.add_widget(pair)
        convert_button = self._button(
            "Convert Currency",
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
        )
        fields.add_widget(convert_button)
        body.add_widget(fields)

        output = self._label(
            "Using saved exchange rates",
            font_size=sp(22),
            color=COLORS["cyan"],
            halign="center",
        )
        rate_status = self._label(
            self.currency.updated_at or "Offline rates available",
            font_size=sp(10),
            color=COLORS["muted"],
            halign="center",
            height=dp(24),
        )
        result_card = Surface(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(3),
            size_hint_y=None,
            height=dp(120),
            background_color=COLORS["surface_alt"],
        )
        result_card.add_widget(output)
        result_card.add_widget(rate_status)
        body.add_widget(result_card)

        refresh_button = self._button("Refresh Live Rates", height=dp(44))
        body.add_widget(refresh_button)
        convert_button.bind(
            on_release=lambda *_: self.convert_currency(
                amount, source, target, output
            )
        )
        refresh_button.bind(
            on_release=lambda *_: self.refresh_currency(rate_status)
        )
        self.content.add_widget(scroll)

    def convert_currency(self, amount, source, target, output):
        try:
            if not self._has_credit():
                output.text = "No credits remaining"
                return
            converted = self.currency.convert(
                float(amount.text),
                source.text,
                target.text,
            )
            output.text = f"{converted:,.2f} {target.text}"
            self.settings.last_currency_from = source.text
            self.settings.last_currency_to = target.text
            self._consume_credit()
            self.settings_store.save()
        except (CalculatorError, ValueError) as exc:
            output.text = str(exc)

    def refresh_currency(self, status_label):
        status_label.text = "Updating exchange rates..."

        def done(ok: bool, message: str):
            color = COLORS["success"] if ok else COLORS["muted"]

            def update_ui(_):
                status_label.text = message
                status_label.color = color

            Clock.schedule_once(update_ui, 0)

        self.currency.refresh(on_done=done)

    # ---------- History ----------

    def show_history(self, *_):
        self._activate_page("History")
        self.content.clear_widgets()
        page = BoxLayout(orientation="vertical", spacing=dp(8))
        title_row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        title_row.add_widget(
            self._page_title("History", f"{len(self.history.entries)} saved calculations")
        )
        if self.history.entries:
            clear_button = self._button(
                "Clear",
                height=dp(36),
                color=COLORS["danger"],
                pressed=COLORS["danger_pressed"],
                font_size=sp(12),
            )
            clear_button.size_hint_x = None
            clear_button.width = dp(72)
            clear_button.bind(on_release=self.clear_history)
            title_row.add_widget(clear_button)
        page.add_widget(title_row)

        scroll, body = self._scroll_page()
        if not self.history.entries:
            empty = Surface(
                orientation="vertical",
                padding=dp(18),
                size_hint_y=None,
                height=dp(130),
            )
            empty.add_widget(
                self._label(
                    "No calculations yet",
                    font_size=sp(18),
                    halign="center",
                )
            )
            empty.add_widget(
                self._label(
                    "Your completed calculations will appear here.",
                    font_size=sp(11),
                    color=COLORS["muted"],
                    halign="center",
                )
            )
            body.add_widget(empty)
        else:
            for item in self.history.entries[:100]:
                card = Surface(
                    orientation="vertical",
                    spacing=dp(2),
                    padding=(dp(13), dp(9)),
                    size_hint_y=None,
                    height=dp(86),
                )
                card.add_widget(
                    self._label(
                        item.expression,
                        font_size=sp(14),
                        color=COLORS["muted"],
                        height=dp(26),
                    )
                )
                card.add_widget(
                    self._label(
                        f"= {item.result}",
                        font_size=sp(20),
                        color=COLORS["cyan"],
                        height=dp(30),
                        bold=True,
                    )
                )
                card.add_widget(
                    self._label(
                        f"{item.angle_mode}  |  {item.timestamp.replace('T', ' ')}",
                        font_size=sp(9),
                        color=COLORS["muted"],
                        height=dp(18),
                    )
                )
                body.add_widget(card)
        page.add_widget(scroll)
        self.content.add_widget(page)

    def clear_history(self, *_):
        self.history.clear()
        self.show_history()

    # ---------- Themes ----------

    def show_themes(self, *_):
        self._activate_page("Themes")
        self.content.clear_widgets()
        scroll, body = self._scroll_page()
        body.add_widget(
            self._page_title("Themes", "Choose a polished color style")
        )

        descriptions = {
            "Dark": "Balanced navy theme for everyday use",
            "Light": "Clean bright theme with strong contrast",
            "AMOLED": "Pure black background for OLED displays",
            "Neon Blue": "Vivid blue accents with a modern look",
        }
        for name in THEMES:
            selected = name == self.settings.theme
            card = Surface(
                orientation="horizontal",
                spacing=dp(10),
                padding=(dp(13), dp(10)),
                size_hint_y=None,
                height=dp(74),
                background_color=(
                    COLORS["surface_pressed"] if selected else COLORS["surface"]
                ),
            )
            text = BoxLayout(orientation="vertical", spacing=dp(1))
            text.add_widget(
                self._label(
                    name,
                    font_size=sp(16),
                    height=dp(28),
                    bold=True,
                )
            )
            text.add_widget(
                self._label(
                    descriptions[name],
                    font_size=sp(10),
                    color=COLORS["muted"],
                    height=dp(24),
                )
            )
            card.add_widget(text)
            choose = self._button(
                "Active" if selected else "Apply",
                height=dp(38),
                color=COLORS["success"] if selected else COLORS["accent"],
                pressed=COLORS["surface_pressed"],
                font_size=sp(11),
            )
            choose.size_hint_x = None
            choose.width = dp(72)
            if not selected:
                choose.bind(
                    on_release=lambda _, theme_name=name: self.apply_theme(theme_name)
                )
            card.add_widget(choose)
            body.add_widget(card)
        self.content.add_widget(scroll)

    def apply_theme(self, name: str) -> None:
        if name not in THEMES:
            return
        self.settings.theme = name
        self.settings_store.save()
        apply_color_theme(name)
        from kivy.core.window import Window

        Window.clearcolor = COLORS["background"]
        self.clear_widgets()
        self._build_shell()
        self.show_themes()

    # ---------- Settings ----------

    def show_settings(self, *_):
        self._activate_page("Settings")
        self.content.clear_widgets()
        scroll, body = self._scroll_page()
        body.add_widget(
            self._page_title("Settings", "Personalize calculation preferences")
        )

        angle = self._spinner(
            self.settings.angle_mode,
            [mode.value for mode in AngleMode],
        )
        angle.bind(text=self.save_angle_setting)
        preferences = Surface(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12),
            size_hint_y=None,
            height=dp(178),
        )
        preferences.add_widget(
            self._label(
                "CALCULATION",
                font_size=sp(10),
                color=COLORS["cyan"],
                height=dp(22),
                bold=True,
            )
        )
        preferences.add_widget(self._field_group("Angle Mode", angle))
        preferences.add_widget(
            self._label(
                "DEG is best for everyday trigonometry. RAD is commonly used in advanced mathematics.",
                font_size=sp(11),
                color=COLORS["muted"],
                valign="top",
                height=dp(48),
            )
        )
        body.add_widget(preferences)

        appearance = Surface(
            orientation="horizontal",
            spacing=dp(10),
            padding=dp(14),
            size_hint_y=None,
            height=dp(82),
            background_color=COLORS["surface_alt"],
        )
        appearance_text = BoxLayout(orientation="vertical", spacing=dp(1))
        appearance_text.add_widget(
            self._label(
                "APPEARANCE",
                font_size=sp(10),
                color=COLORS["cyan"],
                height=dp(22),
                bold=True,
            )
        )
        appearance_text.add_widget(
            self._label(
                self.settings.theme,
                font_size=sp(17),
                height=dp(28),
                bold=True,
            )
        )
        appearance.add_widget(appearance_text)
        theme_button = self._button(
            "Themes",
            height=dp(40),
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
        )
        theme_button.size_hint_x = None
        theme_button.width = dp(90)
        theme_button.bind(on_release=self.show_themes)
        appearance.add_widget(theme_button)
        body.add_widget(appearance)

        about = Surface(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(14),
            size_hint_y=None,
            height=dp(145),
        )
        about.add_widget(
            self._label(
                "ABOUT",
                font_size=sp(10),
                color=COLORS["cyan"],
                height=dp(22),
                bold=True,
            )
        )
        about.add_widget(
            self._label(
                "Precision Calculator",
                font_size=sp(18),
                height=dp(30),
                bold=True,
            )
        )
        about.add_widget(
            self._label(
                "Scientific calculator, converters, statistics and private calculation history in one app.",
                font_size=sp(11),
                color=COLORS["muted"],
                valign="top",
                height=dp(48),
            )
        )
        about.add_widget(
            self._label(
                "Designed by Hussain Babar",
                font_size=sp(12),
                color=COLORS["cyan"],
                height=dp(25),
                bold=True,
            )
        )
        body.add_widget(about)
        self.content.add_widget(scroll)

    def save_angle_setting(self, _, selected):
        self.settings.angle_mode = selected
        self.settings_store.save()

    # ---------- Pro ----------

    def show_pro(self, *_):
        self._activate_page("Precision Pro")
        self.content.clear_widgets()
        scroll, body = self._scroll_page()
        body.add_widget(
            self._page_title("Precision Pro", "Unlimited access across every tool")
        )

        status_card = Surface(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(15),
            size_hint_y=None,
            height=dp(118),
            background_color=COLORS["surface_alt"],
        )
        status_card.add_widget(
            self._label(
                "PRO ACTIVE" if self.settings.is_pro else "FREE PLAN",
                font_size=sp(10),
                color=COLORS["success"] if self.settings.is_pro else COLORS["cyan"],
                height=dp(22),
                bold=True,
            )
        )
        status_card.add_widget(
            self._label(
                "Unlimited calculations"
                if self.settings.is_pro
                else f"{self.settings.credits_remaining} of 100 credits remaining",
                font_size=sp(24),
                height=dp(42),
                bold=True,
            )
        )
        status_card.add_widget(
            self._label(
                "One credit is used only after a successful result.",
                font_size=sp(11),
                color=COLORS["muted"],
                height=dp(25),
            )
        )
        body.add_widget(status_card)

        benefits = Surface(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(15),
            size_hint_y=None,
            height=dp(190),
        )
        benefits.add_widget(
            self._label(
                "PRO BENEFITS",
                font_size=sp(10),
                color=COLORS["cyan"],
                height=dp(22),
                bold=True,
            )
        )
        for line in (
            "Unlimited scientific calculations",
            "Unlimited currency and unit conversions",
            "Unlimited statistics analysis",
            "All premium themes",
        ):
            benefits.add_widget(
                self._label(
                    line,
                    font_size=sp(14),
                    height=dp(30),
                )
            )
        body.add_widget(benefits)

        if not self.settings.is_pro:
            payment = self._button(
                "EasyPaisa setup required",
                height=dp(52),
                color=COLORS["accent"],
                pressed=COLORS["accent_pressed"],
                font_size=sp(15),
            )
            payment.bind(on_release=self.show_payment_requirement)
            body.add_widget(payment)
            body.add_widget(
                self._label(
                    "Automatic activation needs a verified merchant checkout and secure server. A personal mobile number alone cannot verify purchases.",
                    font_size=sp(11),
                    color=COLORS["muted"],
                    valign="top",
                    height=dp(58),
                )
            )
        self.content.add_widget(scroll)

    def show_payment_requirement(self, *_):
        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(14),
        )
        box.add_widget(
            self._label(
                "Automatic EasyPaisa payment is not connected yet.\n\n"
                "A verified merchant account, payment API and secure backend are required before real money can be accepted and Pro can be unlocked safely.",
                font_size=sp(13),
                halign="center",
                valign="top",
            )
        )
        close = self._button(
            "Close",
            height=dp(46),
            color=COLORS["accent"],
            pressed=COLORS["accent_pressed"],
        )
        box.add_widget(close)
        popup = Popup(
            title="Secure payment setup",
            content=box,
            size_hint=(0.90, None),
            height=dp(300),
            auto_dismiss=False,
        )
        close.bind(on_release=popup.dismiss)
        popup.open()


class PrecisionAndroidApp(App):
    title = "Precision Calculator"

    def build(self):
        from kivy.core.window import Window

        Window.clearcolor = COLORS["background"]
        Window.softinput_mode = "below_target"
        return MobileCalculator()


def run_mobile_app():
    PrecisionAndroidApp().run()
