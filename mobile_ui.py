"""Kivy Android UI backed by the existing calculator and conversion engines."""

from __future__ import annotations

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from calculator import AngleMode, CalculatorError, evaluate_expression, format_number, statistics_summary
from converter import CURRENCY_CODES, CurrencyConverter, UNIT_CATEGORIES, convert_unit
from history import HistoryManager
from settings import SettingsStore


class MobileCalculator(BoxLayout):
    """Phone-sized interface for the shared application features."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=6, padding=8, **kwargs)
        self.settings = SettingsStore().load()
        self.ans = 0.0
        self.history = HistoryManager()
        self.currency = CurrencyConverter()
        self.expression = TextInput(multiline=False, font_size=24, size_hint_y=None, height=54)
        self.result = Label(text="0", font_size=30, size_hint_y=None, height=52)
        self.status = Label(text="Ready", size_hint_y=None, height=28)
        self.add_widget(Label(text="PRECISION CALCULATOR", font_size=20, size_hint_y=None, height=36))
        self.add_widget(self.expression)
        self.add_widget(self.result)
        self.add_widget(self.status)
        self.content = BoxLayout(orientation="vertical")
        self.add_widget(self.content)
        self.show_calculator()

    def nav_row(self):
        row = BoxLayout(size_hint_y=None, height=44, spacing=3)
        for name, callback in (("Calculator", self.show_calculator), ("Units", self.show_units), ("Stats", self.show_stats), ("Currency", self.show_currency), ("History", self.show_history)):
            button = Button(text=name)
            button.bind(on_release=lambda _, callback=callback: callback())
            row.add_widget(button)
        return row

    def show_calculator(self):
        self.content.clear_widgets()
        self.content.add_widget(self.nav_row())
        keys = ("AC", "⌫", "(", ")", "sin", "cos", "tan", "log", "ln", "sqrt", "π", "e", "7", "8", "9", "÷", "4", "5", "6", "×", "1", "2", "3", "−", "0", ".", "%", "+", "ANS", "=", "x²", "x!", "1/x")
        grid = GridLayout(cols=4, spacing=4)
        for key in keys:
            button = Button(text=key)
            button.bind(on_release=lambda _, value=key: self.press(value))
            grid.add_widget(button)
        self.content.add_widget(grid)

    def press(self, key):
        if key == "AC":
            self.expression.text = ""
        elif key == "⌫":
            self.expression.text = self.expression.text[:-1]
        elif key == "=":
            try:
                value = evaluate_expression(self.expression.text, angle_mode=AngleMode(self.settings.angle_mode), ans=self.ans)
                self.ans = value
                self.result.text = format_number(value)
                self.history.add(self.expression.text, self.result.text, self.settings.angle_mode)
                self.status.text = "Calculated"
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

    def show_units(self):
        self.content.clear_widgets()
        self.content.add_widget(self.nav_row())
        category = Spinner(text="Length", values=list(UNIT_CATEGORIES), size_hint_y=None, height=48)
        value = TextInput(text="1", input_filter="float", multiline=False, size_hint_y=None, height=48)
        source = Spinner(text="Meter", values=list(UNIT_CATEGORIES["Length"]), size_hint_y=None, height=48)
        target = Spinner(text="Kilometer", values=list(UNIT_CATEGORIES["Length"]), size_hint_y=None, height=48)
        output = Label(text="", font_size=24)

        def category_changed(_, selected):
            units = list(UNIT_CATEGORIES[selected])
            source.values = target.values = units
            source.text, target.text = units[0], units[min(1, len(units) - 1)]

        category.bind(text=category_changed)
        button = Button(text="Convert", size_hint_y=None, height=48)
        button.bind(on_release=lambda *_: self.convert_unit_value(category, value, source, target, output))
        for widget in (category, value, source, target, button, output):
            self.content.add_widget(widget)

    def convert_unit_value(self, category, value, source, target, output):
        try:
            output.text = format_number(convert_unit(category.text, float(value.text), source.text, target.text))
        except (CalculatorError, ValueError):
            output.text = "Enter a valid value"

    def show_stats(self):
        self.content.clear_widgets()
        self.content.add_widget(self.nav_row())
        values = TextInput(hint_text="Numbers separated by commas", multiline=False, size_hint_y=None, height=48)
        output = Label(text="")
        button = Button(text="Analyze", size_hint_y=None, height=48)
        button.bind(on_release=lambda *_: self.analyze(values, output))
        for widget in (values, button, output):
            self.content.add_widget(widget)

    def analyze(self, values, output):
        try:
            summary = statistics_summary([float(item.strip()) for item in values.text.split(",")])
            output.text = "\n".join(f"{key}: {value}" for key, value in summary.items())
        except (CalculatorError, ValueError) as exc:
            output.text = str(exc)

    def show_currency(self):
        self.content.clear_widgets()
        self.content.add_widget(self.nav_row())
        amount = TextInput(text="1", input_filter="float", multiline=False, size_hint_y=None, height=48)
        source = Spinner(text="USD", values=CURRENCY_CODES, size_hint_y=None, height=48)
        target = Spinner(text="EUR", values=CURRENCY_CODES, size_hint_y=None, height=48)
        output = Label(text="Using saved rates", font_size=22)
        button = Button(text="Convert", size_hint_y=None, height=48)
        button.bind(on_release=lambda *_: self.convert_currency(amount, source, target, output))
        for widget in (amount, source, target, button, output):
            self.content.add_widget(widget)

    def convert_currency(self, amount, source, target, output):
        try:
            output.text = f"{self.currency.convert(float(amount.text), source.text, target.text):,.2f} {target.text}"
        except (CalculatorError, ValueError) as exc:
            output.text = str(exc)

    def show_history(self):
        self.content.clear_widgets()
        self.content.add_widget(self.nav_row())
        text = "\n\n".join(f"{item.timestamp}\n{item.expression} = {item.result}" for item in self.history.entries)
        self.content.add_widget(Label(text=text or "No calculations yet", halign="left", valign="top"))


class PrecisionAndroidApp(App):
    def build(self):
        return MobileCalculator()


def run_mobile_app():
    PrecisionAndroidApp().run()