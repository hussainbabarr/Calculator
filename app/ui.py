"""Single-window CustomTkinter dashboard for Precision Calculator."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk

from . import config
from .calculator import CalculatorError, CalculatorState, evaluate_expression, format_number, statistics_summary
from .converter import UNITS, convert_unit
from .currency_converter import CurrencyConverter, CurrencyConverterError
from .history import HistoryStore
from .settings import Settings
from .themes import FONT, THEMES

class PageFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, app: "PrecisionApp", title: str, subtitle: str) -> None:
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.title_text = title
        self.subtitle_text = subtitle
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=title.upper(), text_color=app.colors["accent"], font=(FONT, 11, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self, text=subtitle, text_color=app.colors["text"], font=(FONT, 28, "bold")).grid(row=1, column=0, sticky="w", pady=(3, 20))

    def card(self, parent: ctk.CTkBaseClass | None = None) -> ctk.CTkFrame:
        return ctk.CTkFrame(parent or self, fg_color=self.app.colors["panel"], corner_radius=18)


class CalculatorFrame(PageFrame):
    def __init__(self, parent: ctk.CTkFrame, app: "PrecisionApp") -> None:
        super().__init__(parent, app, "Calculator", "Precision, without the clutter.")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.calc_card = self.card(); self.calc_card.grid(row=2, column=0, sticky="nsew", padx=(0, 16))
        self.history_card = self.card(); self.history_card.grid(row=2, column=1, sticky="nsew")
        self._build_calculator()
        self._build_history()

    def _build_calculator(self) -> None:
        card = self.calc_card
        card.grid_columnconfigure(tuple(range(6)), weight=1)
        card.grid_rowconfigure(tuple(range(11)), weight=1)
        display_frame = ctk.CTkFrame(card, fg_color=self.app.colors["panel2"], corner_radius=14)
        display_frame.grid(row=0, column=0, columnspan=6, sticky="ew", padx=18, pady=18)
        ctk.CTkLabel(display_frame, textvariable=self.app.expression, text_color=self.app.colors["muted"], font=(FONT, 14), anchor="e").pack(fill="x", padx=20, pady=(18, 0))
        ctk.CTkLabel(display_frame, textvariable=self.app.display, text_color=self.app.colors["text"], font=(FONT, 42, "bold"), anchor="e").pack(fill="x", padx=20, pady=(4, 18))
        modes = ctk.CTkSegmentedButton(card, values=["DEG", "RAD", "GRAD"], command=self._angle)
        modes.set(self.app.calc_state.angle_mode); modes.grid(row=1, column=0, columnspan=3, sticky="ew", padx=(18, 6), pady=(0, 10))
        ctk.CTkLabel(card, textvariable=self.app.status, text_color=self.app.colors["muted"], anchor="e").grid(row=1, column=3, columnspan=3, sticky="ew", padx=18, pady=(0, 10))
        keys = [("MC", "memory"), ("MR", "memory"), ("M+", "memory"), ("M-", "memory"), ("MS", "memory"), ("⌫", "danger"), ("sin", "function"), ("cos", "function"), ("tan", "function"), ("log", "function"), ("ln", "function"), ("÷", "operator"), ("asin", "function"), ("acos", "function"), ("atan", "function"), ("sqrt", "function"), ("x²", "function"), ("×", "operator"), ("sinh", "function"), ("cosh", "function"), ("tanh", "function"), ("π", "constant"), ("e", "constant"), ("-", "operator"), ("7", "number"), ("8", "number"), ("9", "number"), ("(", "number"), (")", "number"), ("+", "operator"), ("4", "number"), ("5", "number"), ("6", "number"), ("xʸ", "function"), ("%", "operator"), ("1/x", "function"), ("1", "number"), ("2", "number"), ("3", "number"), (".", "number"), ("ANS", "constant"), ("=", "equals"), ("AC", "danger"), ("0", "number"), ("00", "number"), ("cbrt", "function"), ("x!", "function"), ("mod", "operator")]
        colors = {"number": self.app.colors["button"], "function": self.app.colors["panel2"], "constant": self.app.colors["panel2"], "operator": self.app.colors["accent2"], "equals": self.app.colors["accent"], "danger": self.app.colors["danger"], "memory": self.app.colors["panel2"]}
        for index, (label, kind) in enumerate(keys):
            row, col = divmod(index, 6)
            fg = self.app.colors["bg"] if kind in ("operator", "equals", "danger") else self.app.colors["text"]
            ctk.CTkButton(card, text=label, height=42, corner_radius=10, fg_color=colors[kind], hover_color=self.app.colors["accent"], text_color=fg, font=(FONT, 12, "bold"), command=lambda value=label: self._press(value)).grid(row=row + 2, column=col, sticky="nsew", padx=4, pady=4)

    def _build_history(self) -> None:
        panel = self.history_card
        ctk.CTkLabel(panel, text="HISTORY", text_color=self.app.colors["accent"], font=(FONT, 11, "bold")).pack(anchor="w", padx=20, pady=(22, 4))
        ctk.CTkLabel(panel, text="Your recent calculations", text_color=self.app.colors["text"], font=(FONT, 18, "bold")).pack(anchor="w", padx=20, pady=(0, 16))
        self.search = ctk.CTkEntry(panel, placeholder_text="Search history", height=36); self.search.pack(fill="x", padx=18, pady=(0, 12)); self.search.bind("<KeyRelease>", lambda _: self._refresh_history())
        self.history_box = ctk.CTkTextbox(panel, state="disabled", fg_color=self.app.colors["panel2"], text_color=self.app.colors["text"], corner_radius=12); self.history_box.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        row = ctk.CTkFrame(panel, fg_color="transparent"); row.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkButton(row, text="Export CSV", command=self._export).pack(side="left", expand=True, fill="x", padx=(0, 5)); ctk.CTkButton(row, text="Clear", fg_color="transparent", border_width=1, command=self._clear_history).pack(side="left", expand=True, fill="x", padx=(5, 0))
        self._refresh_history()

    def _press(self, label: str) -> None:
        try:
            state = self.app.calc_state
            if label == "AC": state.display = "0"; self.app.expression.set("")
            elif label == "⌫": state.display = state.display[:-1] or "0"
            elif label == "=":
                expression = state.display; result = state.calculate(); self.app.expression.set(f"{expression}  ="); self.app.history.add(expression, result); self.app.status.set("Calculated"); self._refresh_history(); return
            elif label in {"sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "log", "ln", "sqrt", "cbrt", "x²", "x!", "1/x"}:
                funcs = {"x²": "({})^2", "x!": "factorial({})", "1/x": "reciprocal({})"}; state.display = funcs.get(label, f"{label}({{}})").format(state.display)
            elif label == "xʸ": state.display += "^"
            elif label == "π": state.display += "pi"
            elif label == "e": state.display += "e"
            elif label == "ANS": state.display += "ANS"
            elif label in {"MC", "MR", "M+", "M-", "MS"}: self._memory(label)
            elif label == "mod": state.display += "%"
            else: state.display = "" if state.display == "0" and label not in "+-×÷" else state.display; state.display += label
            self.app.display.set(state.display)
        except CalculatorError as exc:
            self.app.status.set(str(exc)); self.app.display.set("Error")

    def _memory(self, label: str) -> None:
        state = self.app.calc_state; value = evaluate_expression(state.display, angle_mode=state.angle_mode, ans=state.ans)
        if label == "MC": state.memory = 0
        elif label == "MR": state.display = format_number(state.memory)
        elif label == "M+": state.memory += value
        elif label == "M-": state.memory -= value
        else: state.memory = value
        self.app.display.set(state.display); self.app.status.set(f"Memory {label}")

    def _angle(self, value: str) -> None:
        self.app.calc_state.angle_mode = value; self.app.settings.values["angle"] = value; self.app.settings.save(); self.app.status.set(f"Angle mode: {value}")

    def _refresh_history(self) -> None:
        self.history_box.configure(state="normal"); self.history_box.delete("1.0", "end")
        for item in self.app.history.search(self.search.get()): self.history_box.insert("end", f"{item['time']}\n{item['expression']}\n= {item['result']}\n\n")
        self.history_box.configure(state="disabled")

    def _clear_history(self) -> None: self.app.history.clear(); self._refresh_history()
    def _export(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path: self.app.history.export_csv(path); self.app.status.set("History exported")


class CurrencyFrame(PageFrame):
    def __init__(self, parent: ctk.CTkFrame, app: "PrecisionApp") -> None:
        super().__init__(parent, app, "Currency Converter", "Exchange rates, in one calm workspace.")
        self.grid_rowconfigure(2, weight=1)
        card = self.card(); card.grid(row=2, column=0, sticky="nsew", padx=80, pady=20); card.grid_columnconfigure(0, weight=1)
        self.amount = ctk.CTkEntry(card, placeholder_text="Amount", height=44); self.amount.insert(0, "1"); self.amount.grid(row=0, column=0, sticky="ew", padx=32, pady=(36, 12))
        codes = list(config.CURRENCIES)
        self.source = ctk.CTkComboBox(card, values=codes, height=40); self.source.set("USD"); self.source.grid(row=1, column=0, sticky="ew", padx=32, pady=8)
        self.target = ctk.CTkComboBox(card, values=codes, height=40); self.target.set("EUR"); self.target.grid(row=2, column=0, sticky="ew", padx=32, pady=8)
        self.result = ctk.CTkLabel(card, text="Loading live rates...", text_color=app.colors["accent"], font=(FONT, 30, "bold")); self.result.grid(row=3, column=0, pady=30)
        ctk.CTkButton(card, text="Convert", height=42, command=self._load).grid(row=4, column=0, padx=32, pady=(0, 36), sticky="ew")
        self.converter = CurrencyConverter(); threading.Thread(target=self._load, daemon=True).start()

    def _load(self) -> None:
        try:
            self.converter.refresh_rates(); converted = self.converter.convert(float(self.amount.get()), self.source.get(), self.target.get())
            self.after(0, lambda: self.result.configure(text=f"{converted.converted_amount:,.2f} {converted.to_currency}"))
        except (CurrencyConverterError, ValueError) as exc: self.after(0, lambda: self.result.configure(text=str(exc)))


class UnitFrame(PageFrame):
    def __init__(self, parent: ctk.CTkFrame, app: "PrecisionApp") -> None:
        super().__init__(parent, app, "Unit Converter", "Convert everyday measurements with clarity.")
        self.grid_rowconfigure(2, weight=1)
        card = self.card(); card.grid(row=2, column=0, sticky="nsew", padx=80, pady=20); card.grid_columnconfigure(0, weight=1)
        self.category = ctk.CTkComboBox(card, values=[*UNITS, "Temperature"], height=40, command=self._category_changed); self.category.set("Length"); self.category.grid(row=0, column=0, sticky="ew", padx=32, pady=(36, 12))
        self.value = ctk.CTkEntry(card, placeholder_text="Value", height=40); self.value.insert(0, "1"); self.value.grid(row=1, column=0, sticky="ew", padx=32, pady=8)
        self.source = ctk.CTkComboBox(card, values=list(UNITS["Length"]), height=40); self.source.set("Meter"); self.source.grid(row=2, column=0, sticky="ew", padx=32, pady=8)
        self.target = ctk.CTkComboBox(card, values=list(UNITS["Length"]), height=40); self.target.set("Kilometer"); self.target.grid(row=3, column=0, sticky="ew", padx=32, pady=8)
        self.output = ctk.CTkLabel(card, text="", text_color=app.colors["accent"], font=(FONT, 30, "bold")); self.output.grid(row=4, column=0, pady=24)
        ctk.CTkButton(card, text="Convert", height=42, command=self._convert).grid(row=5, column=0, padx=32, pady=(0, 36), sticky="ew")

    def _category_changed(self, _: str) -> None:
        units = ["Celsius", "Fahrenheit", "Kelvin"] if self.category.get() == "Temperature" else list(UNITS[self.category.get()])
        self.source.configure(values=units); self.target.configure(values=units); self.source.set(units[0]); self.target.set(units[1] if len(units) > 1 else units[0])

    def _convert(self) -> None:
        try: self.output.configure(text=format_number(convert_unit(self.category.get(), float(self.value.get()), self.source.get(), self.target.get())))
        except (ValueError, KeyError): self.output.configure(text="Enter a valid value")


class StatisticsFrame(PageFrame):
    def __init__(self, parent: ctk.CTkFrame, app: "PrecisionApp") -> None:
        super().__init__(parent, app, "Statistics", "Turn a list of numbers into useful signals.")
        self.grid_rowconfigure(2, weight=1)
        card = self.card(); card.grid(row=2, column=0, sticky="nsew", padx=80, pady=20); card.grid_columnconfigure(0, weight=1); card.grid_rowconfigure(1, weight=1)
        self.values = ctk.CTkEntry(card, placeholder_text="Numbers separated by commas", height=44); self.values.grid(row=0, column=0, sticky="ew", padx=32, pady=(36, 14))
        self.output = ctk.CTkTextbox(card, fg_color=self.app.colors["panel2"], text_color=self.app.colors["text"], corner_radius=12); self.output.grid(row=1, column=0, sticky="nsew", padx=32, pady=12)
        ctk.CTkButton(card, text="Analyze", height=42, command=self._calculate).grid(row=2, column=0, padx=32, pady=(12, 36), sticky="ew")

    def _calculate(self) -> None:
        try:
            summary = statistics_summary([float(item.strip()) for item in self.values.get().split(",")]); self.output.delete("1.0", "end"); self.output.insert("end", "\n".join(f"{key}: {value}" for key, value in summary.items()))
        except (ValueError, CalculatorError) as exc: self.output.delete("1.0", "end"); self.output.insert("end", str(exc))


class SettingsFrame(PageFrame):
    def __init__(self, parent: ctk.CTkFrame, app: "PrecisionApp") -> None:
        super().__init__(parent, app, "Settings", "A few quiet controls for your workspace.")
        self.grid_rowconfigure(2, weight=1)
        card = self.card(); card.grid(row=2, column=0, sticky="nsew", padx=80, pady=20); card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Appearance", text_color=app.colors["muted"], font=(FONT, 12, "bold")).grid(row=0, column=0, sticky="w", padx=32, pady=(34, 8))
        self.theme = ctk.CTkOptionMenu(card, values=list(THEMES), command=app.change_theme, fg_color=app.colors["panel2"], button_color=app.colors["accent2"], height=40); self.theme.set(app.theme); self.theme.grid(row=1, column=0, sticky="ew", padx=32, pady=8)
        ctk.CTkLabel(card, text="Angle mode is available directly on the Calculator page.\nPreferences are saved automatically.", text_color=app.colors["muted"], justify="left", wraplength=620).grid(row=2, column=0, sticky="w", padx=32, pady=30)


class PrecisionApp(ctk.CTk):
    def __init__(self) -> None:
        self.settings = Settings(); self.theme = self.settings.values.get("theme", "Dark"); self.colors = THEMES.get(self.theme, THEMES["Dark"])
        ctk.set_appearance_mode("dark" if self.theme != "Light" else "light"); ctk.set_default_color_theme("blue"); super().__init__()
        self.title("Precision | Scientific Calculator"); self.geometry("1400x900"); self.minsize(1200, 800); self.configure(fg_color=self.colors["bg"])
        self.calc_state = CalculatorState(angle_mode=self.settings.values.get("angle", "DEG")); self.history = HistoryStore(); self.expression = ctk.StringVar(value=""); self.display = ctk.StringVar(value="0"); self.status = ctk.StringVar(value="Ready")
        self._build_shell(); self.show_page("Calculator"); self.bind("<Key>", self._keyboard); self.after(80, lambda: self.page_host.pack(fill="both", expand=True, padx=28, pady=(8, 24)))

    def _build_shell(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=244, corner_radius=0, fg_color=self.colors["panel"]); self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)
        ctk.CTkLabel(self.sidebar, text="PRECISION", text_color=self.colors["accent"], font=(FONT, 20, "bold")).pack(anchor="w", padx=28, pady=(36, 4)); ctk.CTkLabel(self.sidebar, text="SCIENTIFIC WORKSPACE", text_color=self.colors["muted"], font=(FONT, 10, "bold")).pack(anchor="w", padx=30, pady=(0, 34))
        for label in ("Calculator", "Currency Converter", "Unit Converter", "Statistics", "Settings"):
            ctk.CTkButton(self.sidebar, text=label, anchor="w", height=44, corner_radius=10, fg_color="transparent", hover_color=self.colors["panel2"], text_color=self.colors["text"], command=lambda name=label: self.show_page(name)).pack(fill="x", padx=14, pady=3)
        ctk.CTkLabel(self.sidebar, text="DESIGNED BY HAUSSAIN BABAR", text_color=self.colors["muted"], font=(FONT, 9, "bold")).pack(side="bottom", padx=26, pady=22)
        self.page_host = ctk.CTkFrame(self, fg_color="transparent")

    def show_page(self, name: str) -> None:
        for child in self.page_host.winfo_children(): child.destroy()
        pages: dict[str, type[PageFrame]] = {"Calculator": CalculatorFrame, "Currency Converter": CurrencyFrame, "Unit Converter": UnitFrame, "Statistics": StatisticsFrame, "Settings": SettingsFrame}
        pages[name](self.page_host, self).pack(fill="both", expand=True)

    def change_theme(self, value: str) -> None:
        self.settings.values["theme"] = value; self.settings.save(); self.theme = value; self.colors = THEMES[value]; ctk.set_appearance_mode("light" if value == "Light" else "dark"); self.sidebar.destroy(); self.page_host.destroy(); self._build_shell(); self.show_page("Settings"); self.page_host.pack(fill="both", expand=True, padx=28, pady=(8, 24))

    def _keyboard(self, event: tk.Event) -> None:
        if event.keysym == "Return": self._active_calculator()._press("=")
        elif event.keysym == "BackSpace": self._active_calculator()._press("⌫")
        elif event.keysym == "Escape": self._active_calculator()._press("AC")
        elif event.char in "0123456789.+-*/()%": self._active_calculator()._press({"*": "×", "/": "÷"}.get(event.char, event.char))

    def _active_calculator(self) -> CalculatorFrame:
        for child in self.page_host.winfo_children():
            if isinstance(child, CalculatorFrame): return child
        self.show_page("Calculator")
        return self._active_calculator()


def run_app() -> None:
    PrecisionApp().mainloop()
