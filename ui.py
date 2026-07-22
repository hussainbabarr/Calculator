"""
Premium CustomTkinter UI — sidebar navigation, glassmorphism, and all tool pages.

Designed by Hussain Babar
"""

from __future__ import annotations

import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

import customtkinter as ctk

from calculator import (
    AngleMode,
    CalculatorError,
    CalculatorMemory,
    NumberBase,
    UndoRedoStack,
    apply_percent,
    convert_base,
    evaluate_expression,
    format_number,
    parse_base,
    random_float,
    random_int,
    statistics_summary,
)
from converter import CURRENCY_CODES, CurrencyConverter, UNIT_CATEGORIES, convert_unit
from history import HistoryManager
from settings import AppSettings, SettingsStore
from themes import THEMES, Theme

try:
    import winsound

    HAS_WINSOUND = sys.platform.startswith("win")
except ImportError:
    HAS_WINSOUND = False


FONT_DISPLAY = ("Segoe UI", 42, "bold")
FONT_EXPR = ("Segoe UI", 18)
FONT_UI = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI Semibold", 22)


def play_click(enabled: bool) -> None:
    if enabled and HAS_WINSOUND:
        try:
            winsound.Beep(880, 25)
        except RuntimeError:
            pass


class GlassButton(ctk.CTkButton):
    """Rounded button with theme-aware hover."""

    def __init__(
        self,
        master,
        theme: Theme,
        text: str = "",
        command: Callable | None = None,
        operator: bool = False,
        danger: bool = False,
        width: int = 72,
        height: int = 48,
        **kwargs,
    ):
        fg = theme.operator if operator else theme.danger if danger else theme.button
        hover = theme.operator_hover if operator else theme.danger if danger else theme.button_hover
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=14,
            font=FONT_UI,
            fg_color=fg,
            hover_color=hover,
            text_color=theme.text,
            border_width=0,
            **kwargs,
        )
        self._theme = theme

    def apply_theme(self, theme: Theme, operator: bool = False, danger: bool = False) -> None:
        self._theme = theme
        fg = theme.operator if operator else theme.danger if danger else theme.button
        hover = theme.operator_hover if operator else theme.danger if danger else theme.button_hover
        self.configure(fg_color=fg, hover_color=hover, text_color=theme.text)


class SidebarNav(ctk.CTkFrame):
    """Left navigation rail."""

    NAV_ITEMS = (
        ("Calculator", "🧮"),
        ("Currency", "💱"),
        ("Units", "📐"),
        ("Statistics", "📊"),
        ("History", "📜"),
        ("Graph", "📈"),
        ("Settings", "⚙"),
    )

    def __init__(self, master, theme: Theme, on_select: Callable[[str], None]):
        super().__init__(master, width=220, corner_radius=0, fg_color=theme.sidebar)
        self.theme = theme
        self.on_select = on_select
        self.buttons: dict[str, ctk.CTkButton] = {}
        self.pack_propagate(False)

        brand = ctk.CTkLabel(
            self,
            text="Precision\nCalculator",
            font=FONT_TITLE,
            text_color=theme.cyan,
            justify="left",
        )
        brand.pack(anchor="w", padx=24, pady=(28, 8))

        sub = ctk.CTkLabel(
            self,
            text="Scientific Suite",
            font=FONT_SMALL,
            text_color=theme.text_muted,
        )
        sub.pack(anchor="w", padx=24, pady=(0, 24))

        for name, icon in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}  {name}",
                anchor="w",
                height=44,
                corner_radius=12,
                font=FONT_UI,
                fg_color="transparent",
                hover_color=theme.panel_alt,
                text_color=theme.text,
                command=lambda n=name: self._select(n),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.buttons[name] = btn

        credit = ctk.CTkLabel(
            self,
            text="Designed by\nHussain Babar",
            font=FONT_SMALL,
            text_color=theme.text_muted,
            justify="left",
        )
        credit.pack(side="bottom", anchor="w", padx=24, pady=24)

    def _select(self, name: str) -> None:
        self.on_select(name)
        self.highlight(name)

    def highlight(self, name: str) -> None:
        for key, btn in self.buttons.items():
            if key == name:
                btn.configure(fg_color=self.theme.panel_alt, text_color=self.theme.cyan)
            else:
                btn.configure(fg_color="transparent", text_color=self.theme.text)

    def apply_theme(self, theme: Theme) -> None:
        self.theme = theme
        self.configure(fg_color=theme.sidebar)


class CalculatorPage(ctk.CTkFrame):
    """Main scientific calculator workspace."""

    KEY_ROWS = [
        ("MC", "MR", "M+", "M-", "MS", "⌫"),
        ("sin", "cos", "tan", "log", "ln", "÷"),
        ("asin", "acos", "atan", "sqrt", "x²", "×"),
        ("sinh", "cosh", "tanh", "π", "e", "−"),
        ("7", "8", "9", "(", ")", "+"),
        ("4", "5", "6", "xʸ", "%", "1/x"),
        ("1", "2", "3", ".", "ANS", "="),
        ("AC", "0", "00", "cbrt", "x!", "mod"),
        ("φ", "10^x", "e^x", "x³", "Rand", "RandInt"),
    ]

    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.expression = ""
        self.result_text = "0"
        self.ans = 0.0
        self.memory = CalculatorMemory()
        self.undo_stack = UndoRedoStack()
        self.error_active = False
        self._key_buttons: list[GlassButton] = []

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self.display_frame = ctk.CTkFrame(left, corner_radius=20, height=160)
        self.display_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.display_frame.grid_propagate(False)

        self.expr_label = ctk.CTkLabel(
            self.display_frame,
            text="",
            font=FONT_EXPR,
            anchor="e",
            wraplength=680,
        )
        self.expr_label.pack(fill="x", padx=24, pady=(18, 0))

        self.result_label = ctk.CTkLabel(
            self.display_frame,
            text="0",
            font=FONT_DISPLAY,
            anchor="e",
        )
        self.result_label.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        toolbar = ctk.CTkFrame(left, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.mode_menu = ctk.CTkOptionMenu(
            toolbar,
            values=[m.value for m in AngleMode],
            command=self._set_angle,
            width=100,
        )
        self.mode_menu.set(app.settings.angle_mode)
        self.mode_menu.pack(side="left", padx=(0, 8))

        self.base_menu = ctk.CTkOptionMenu(
            toolbar,
            values=[b.value for b in NumberBase],
            command=self._set_base,
            width=130,
        )
        self.base_menu.set(app.settings.number_base)
        self.base_menu.pack(side="left", padx=(0, 8))

        self.status_label = ctk.CTkLabel(toolbar, text="Ready", font=FONT_SMALL)
        self.status_label.pack(side="left", padx=12)

        pad = ctk.CTkFrame(left, fg_color="transparent")
        pad.grid(row=2, column=0, sticky="nsew")
        for r, row in enumerate(self.KEY_ROWS):
            pad.grid_rowconfigure(r, weight=1)
        pad.grid_columnconfigure(tuple(range(6)), weight=1)

        for r, row in enumerate(self.KEY_ROWS):
            for c, key in enumerate(row):
                op = key in {"=", "÷", "×", "−", "+", "%", "mod"}
                danger = key == "AC"
                btn = GlassButton(
                    pad,
                    app.theme,
                    text=key,
                    operator=op,
                    danger=danger,
                    command=lambda k=key: self.on_key(k),
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self._key_buttons.append(btn)

        right = ctk.CTkFrame(self, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Expression History", font=FONT_UI).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 8)
        )
        self.mini_history = ctk.CTkTextbox(right, font=FONT_SMALL, activate_scrollbars=True)
        self.mini_history.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.mini_history.configure(state="disabled")

        self._bind_keys()
        self.undo_stack.push("")

    def _bind_keys(self) -> None:
        bindings = {
            "<Return>": lambda e: self.on_key("="),
            "<KP_Enter>": lambda e: self.on_key("="),
            "<BackSpace>": lambda e: self.on_key("⌫"),
            "<Escape>": lambda e: self.on_key("AC"),
            "<Control-z>": lambda e: self.undo(),
            "<Control-y>": lambda e: self.redo(),
            "<Control-c>": lambda e: self.copy_result(),
            "<Control-v>": lambda e: self.paste_clipboard(),
        }
        for seq, handler in bindings.items():
            self.winfo_toplevel().bind(seq, handler)

        for char in "0123456789.()+-*/":
            self.winfo_toplevel().bind(char, self._type_char)

    def _type_char(self, event) -> None:
        self.on_key(event.char)

    def _set_angle(self, value: str) -> None:
        self.app.settings.angle_mode = value
        self.app.settings_store.save()
        self.status_label.configure(text=f"Angle: {value}")

    def _set_base(self, value: str) -> None:
        self.app.settings.number_base = value
        self.app.settings_store.save()
        try:
            dec = parse_base(self.result_text, NumberBase(value))
            self.result_text = convert_base(dec, NumberBase(value))
            self._refresh_display()
        except CalculatorError:
            pass

    def _refresh_display(self) -> None:
        self.expr_label.configure(text=self.expression)
        color = self.app.theme.error if self.error_active else self.app.theme.text
        self.result_label.configure(text=self.result_text[:24], text_color=color)

    def _snapshot(self) -> None:
        self.undo_stack.push(self.expression)

    def undo(self) -> None:
        prev = self.undo_stack.undo(self.expression)
        if prev is not None:
            self.expression = prev
            self.error_active = False
            self._refresh_display()

    def redo(self) -> None:
        nxt = self.undo_stack.redo(self.expression)
        if nxt is not None:
            self.expression = nxt
            self.error_active = False
            self._refresh_display()

    def copy_result(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self.result_text)
        self.status_label.configure(text="Result copied")

    def paste_clipboard(self) -> None:
        try:
            text = self.clipboard_get()
            self._snapshot()
            self.expression += text
            self._refresh_display()
        except tk.TclError:
            pass

    def on_key(self, key: str) -> None:
        play_click(self.app.settings.sound_enabled)
        mapping = {
            "×": "*",
            "÷": "/",
            "−": "-",
            "xʸ": "**",
            "x²": "**2",
            "x³": "**3",
            "π": "π",
            "φ": "φ",
            "mod": " mod ",
            "ANS": "ANS",
            "sqrt": "sqrt(",
            "cbrt": "cbrt(",
            "x!": "factorial(",
            "1/x": "reciprocal(",
            "10^x": "pow10(",
            "e^x": "exp(",
            "Rand": None,
            "RandInt": None,
        }
        if key == "AC":
            self._snapshot()
            self.expression = ""
            self.result_text = "0"
            self.error_active = False
            self._refresh_display()
            return
        if key == "⌫":
            self._snapshot()
            self.expression = self.expression[:-1]
            self.error_active = False
            self._refresh_display()
            return
        if key == "=":
            self.evaluate()
            return
        if key in {"MC", "MR", "M+", "M-", "MS"}:
            self._memory(key)
            return
        if key == "%":
            self._snapshot()
            self.expression = apply_percent(self.expression)
            self._refresh_display()
            return
        if key == "Rand":
            v = format_number(random_float(0, 1))
            self._snapshot()
            self.expression += v
            self._refresh_display()
            return
        if key == "RandInt":
            v = str(random_int(1, 100))
            self._snapshot()
            self.expression += v
            self._refresh_display()
            return

        token = mapping.get(key, key)
        if token is None:
            return
        self._snapshot()
        self.expression += token
        self.error_active = False
        self._refresh_display()

    def _memory(self, op: str) -> None:
        try:
            current = float(self.result_text) if self.result_text else 0.0
        except ValueError:
            current = self.ans
        if op == "MC":
            self.memory.clear()
            self.status_label.configure(text="Memory cleared")
        elif op == "MR":
            self.expression += format_number(self.memory.recall())
            self._refresh_display()
        elif op == "M+":
            self.memory.add(current)
            self.status_label.configure(text="M+")
        elif op == "M-":
            self.memory.subtract(current)
            self.status_label.configure(text="M−")
        elif op == "MS":
            self.memory.store(current)
            self.status_label.configure(text="Memory stored")

    def evaluate(self) -> None:
        try:
            mode = AngleMode(self.app.settings.angle_mode)
            value = evaluate_expression(self.expression, mode, self.ans)
            base = NumberBase(self.app.settings.number_base)
            if base != NumberBase.DEC:
                self.result_text = convert_base(value, base)
            else:
                self.result_text = format_number(value)
            self.ans = value
            self.error_active = False
            self.app.history.add(self.expression, self.result_text, mode.value)
            self._append_mini_history(f"{self.expression} = {self.result_text}")
            self.status_label.configure(text="OK")
        except CalculatorError as exc:
            self.error_active = True
            self.result_text = str(exc)
            self.status_label.configure(text="Error")
        except Exception:
            self.error_active = True
            self.result_text = "Unexpected error"
            self.status_label.configure(text="Error")
        self._refresh_display()

    def _append_mini_history(self, line: str) -> None:
        self.mini_history.configure(state="normal")
        self.mini_history.insert("1.0", line + "\n")
        self.mini_history.configure(state="disabled")

    def apply_theme(self, theme: Theme) -> None:
        self.display_frame.configure(fg_color=theme.display_bg)
        self.expr_label.configure(text_color=theme.text_muted)
        self.result_label.configure(text_color=theme.text if not self.error_active else theme.error)
        for btn in self._key_buttons:
            op = btn.cget("text") in {"=", "÷", "×", "−", "+", "%", "mod"}
            danger = btn.cget("text") == "AC"
            btn.apply_theme(theme, operator=op, danger=danger)


class CurrencyPage(ctk.CTkFrame):
    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.converter = app.currency

        header = ctk.CTkLabel(self, text="Currency Converter", font=FONT_TITLE)
        header.pack(anchor="w", pady=(0, 8))

        self.rate_label = ctk.CTkLabel(self, text="Loading rates…", font=FONT_SMALL)
        self.rate_label.pack(anchor="w", pady=(0, 16))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=8)

        self.amount = ctk.CTkEntry(row, placeholder_text="Amount", width=200)
        self.amount.pack(side="left", padx=(0, 12))
        self.amount.insert(0, "1")

        self.from_var = tk.StringVar(value=app.settings.last_currency_from)
        self.to_var = tk.StringVar(value=app.settings.last_currency_to)

        self.from_menu = ctk.CTkOptionMenu(row, variable=self.from_var, values=CURRENCY_CODES, width=100)
        self.from_menu.pack(side="left", padx=6)

        swap = ctk.CTkButton(row, text="⇄", width=40, command=self.swap)
        swap.pack(side="left", padx=6)

        self.to_menu = ctk.CTkOptionMenu(row, variable=self.to_var, values=CURRENCY_CODES, width=100)
        self.to_menu.pack(side="left", padx=6)

        GlassButton(row, app.theme, text="Convert", operator=True, command=self.convert).pack(
            side="left", padx=12
        )
        GlassButton(row, app.theme, text="Refresh Rates", command=self.refresh).pack(side="left")

        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", pady=12)
        self.search = ctk.CTkEntry(search_row, placeholder_text="Search currency code…", width=280)
        self.search.pack(side="left")
        self.search.bind("<KeyRelease>", self._filter_currencies)

        self.output = ctk.CTkLabel(self, text="", font=FONT_DISPLAY)
        self.output.pack(anchor="w", pady=24)

        self.refresh()

    def _filter_currencies(self, _event=None) -> None:
        matches = self.converter.search_currencies(self.search.get())
        self.from_menu.configure(values=matches)
        self.to_menu.configure(values=matches)

    def swap(self) -> None:
        a, b = self.from_var.get(), self.to_var.get()
        self.from_var.set(b)
        self.to_var.set(a)

    def refresh(self) -> None:
        self.rate_label.configure(text="Fetching live rates…")
        self.converter.refresh(on_done=self._on_rates)

    def _on_rates(self, ok: bool, msg: str) -> None:
        self.after(0, lambda: self.rate_label.configure(text=msg))

    def convert(self) -> None:
        try:
            amount = float(self.amount.get())
            result = self.converter.convert(amount, self.from_var.get(), self.to_var.get())
            self.output.configure(
                text=f"{format_number(result)} {self.to_var.get()}",
                text_color=self.app.theme.cyan,
            )
            self.app.settings.last_currency_from = self.from_var.get()
            self.app.settings.last_currency_to = self.to_var.get()
            self.app.settings_store.save()
        except (CalculatorError, ValueError) as exc:
            self.output.configure(text=str(exc), text_color=self.app.theme.error)


class UnitPage(ctk.CTkFrame):
    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Unit Converter", font=FONT_TITLE).pack(anchor="w", pady=(0, 16))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        self.category = ctk.CTkOptionMenu(
            row, values=list(UNIT_CATEGORIES.keys()), command=self._on_category, width=160
        )
        self.category.pack(side="left", padx=(0, 12))

        self.amount = ctk.CTkEntry(row, placeholder_text="Value", width=140)
        self.amount.pack(side="left", padx=6)
        self.amount.insert(0, "1")

        self.source = ctk.CTkOptionMenu(row, values=[], width=140)
        self.source.pack(side="left", padx=6)
        ctk.CTkLabel(row, text="→").pack(side="left", padx=6)
        self.target = ctk.CTkOptionMenu(row, values=[], width=140)
        self.target.pack(side="left", padx=6)

        GlassButton(row, app.theme, text="Convert", operator=True, command=self.convert).pack(
            side="left", padx=12
        )

        self.output = ctk.CTkLabel(self, text="", font=FONT_DISPLAY)
        self.output.pack(anchor="w", pady=24)

        self._on_category(self.category.get())

    def _on_category(self, cat: str) -> None:
        units = list(UNIT_CATEGORIES[cat].keys())
        self.source.configure(values=units)
        self.target.configure(values=units)
        self.source.set(units[0])
        self.target.set(units[1] if len(units) > 1 else units[0])

    def convert(self) -> None:
        try:
            val = float(self.amount.get())
            out = convert_unit(
                self.category.get(), val, self.source.get(), self.target.get()
            )
            self.output.configure(
                text=f"{format_number(out)} {self.target.get()}",
                text_color=self.app.theme.cyan,
            )
        except (CalculatorError, ValueError) as exc:
            self.output.configure(text=str(exc), text_color=self.app.theme.error)


class StatisticsPage(ctk.CTkFrame):
    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        ctk.CTkLabel(self, text="Statistics", font=FONT_TITLE).pack(anchor="w", pady=(0, 12))
        ctk.CTkLabel(
            self,
            text="Enter numbers separated by commas or spaces",
            font=FONT_SMALL,
            text_color=app.theme.text_muted,
        ).pack(anchor="w")

        self.input = ctk.CTkTextbox(self, height=100)
        self.input.pack(fill="x", pady=12)
        GlassButton(self, app.theme, text="Calculate", operator=True, command=self.run).pack(anchor="w")

        self.output = ctk.CTkTextbox(self, height=220)
        self.output.pack(fill="both", expand=True, pady=12)

    def run(self) -> None:
        raw = self.input.get("1.0", "end")
        tokens = raw.replace(",", " ").split()
        try:
            values = [float(t) for t in tokens]
            summary = statistics_summary(values)
            self.output.delete("1.0", "end")
            for k, v in summary.items():
                self.output.insert("end", f"{k}: {v}\n")
        except (CalculatorError, ValueError) as exc:
            self.output.delete("1.0", "end")
            self.output.insert("1.0", str(exc))


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="History", font=FONT_TITLE).pack(side="left")
        self.search = ctk.CTkEntry(top, placeholder_text="Search…", width=220)
        self.search.pack(side="left", padx=16)
        self.search.bind("<KeyRelease>", lambda e: self.refresh())

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=8)
        GlassButton(btn_row, app.theme, text="Copy Selected", command=self.copy_line).pack(side="left", padx=4)
        GlassButton(btn_row, app.theme, text="Export CSV", command=self.export_csv).pack(side="left", padx=4)
        GlassButton(btn_row, app.theme, text="Export PDF", command=self.export_pdf).pack(side="left", padx=4)
        GlassButton(btn_row, app.theme, text="Clear", danger=True, command=self.clear).pack(side="left", padx=4)

        self.listbox = ctk.CTkTextbox(self)
        self.listbox.pack(fill="both", expand=True, pady=8)
        self.refresh()

    def refresh(self) -> None:
        entries = self.app.history.search(self.search.get())
        self.listbox.delete("1.0", "end")
        for e in entries:
            self.listbox.insert("end", f"{e.timestamp}  |  {e.expression}  =  {e.result}\n")

    def copy_line(self) -> None:
        try:
            line = self.listbox.selection_get()
        except tk.TclError:
            text = self.listbox.get("1.0", "2.0").strip()
            line = text.split("=")[-1].strip() if "=" in text else text
        self.clipboard_clear()
        self.clipboard_append(line)

    def export_csv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            self.app.history.export_csv(Path(path))
            messagebox.showinfo("Export", "History exported to CSV.")

    def export_pdf(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        try:
            self.app.history.export_pdf(Path(path))
            messagebox.showinfo("Export", "History exported to PDF.")
        except RuntimeError as exc:
            messagebox.showerror("Export", str(exc))

    def clear(self) -> None:
        if messagebox.askyesno("Clear history", "Remove all history entries?"):
            self.app.history.clear()
            self.refresh()


class GraphPage(ctk.CTkFrame):
    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        ctk.CTkLabel(self, text="Function Graph", font=FONT_TITLE).pack(anchor="w")
        ctk.CTkLabel(
            self,
            text="Plot y = f(x)  e.g. sin(x), x**2, sqrt(abs(x))",
            font=FONT_SMALL,
            text_color=app.theme.text_muted,
        ).pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=8)
        self.expr = ctk.CTkEntry(row, placeholder_text="Expression in x", width=360)
        self.expr.pack(side="left", padx=(0, 8))
        self.expr.insert(0, "sin(x)")
        GlassButton(row, app.theme, text="Plot", operator=True, command=self.plot).pack(side="left")

        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            self._Figure = Figure
            self._Canvas = FigureCanvasTkAgg
            self.fig = Figure(figsize=(6, 4), dpi=100, facecolor=app.theme.panel)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=12)
        except ImportError:
            ctk.CTkLabel(self, text="Install matplotlib to enable graphs.", font=FONT_UI).pack(pady=24)
            self.fig = None

    def plot(self) -> None:
        if not self.fig:
            return
        import numpy as np

        expr = self.expr.get().strip()
        xs = np.linspace(-2 * math.pi, 2 * math.pi, 400)
        ys = []
        mode = AngleMode(self.app.settings.angle_mode)
        for x in xs:
            try:
                ys.append(
                    evaluate_expression(
                        expr.replace("x", f"({x})"),
                        mode,
                        0.0,
                    )
                )
            except CalculatorError:
                ys.append(float("nan"))
        self.ax.clear()
        self.ax.set_facecolor(self.app.theme.display_bg)
        self.ax.plot(xs, ys, color=self.app.theme.cyan, linewidth=2)
        self.ax.grid(True, alpha=0.25)
        self.ax.set_title(f"y = {expr}", color=self.app.theme.text)
        self.canvas.draw()


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app: "PrecisionCalculatorUI"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        ctk.CTkLabel(self, text="Settings", font=FONT_TITLE).pack(anchor="w", pady=(0, 16))

        self.theme_menu = ctk.CTkOptionMenu(
            self, values=list(THEMES.keys()), command=app.set_theme
        )
        self.theme_menu.set(app.settings.theme)
        self._row("Theme", self.theme_menu)

        self.sound = ctk.CTkSwitch(self, text="Sound effects", command=self._toggle_sound)
        if app.settings.sound_enabled:
            self.sound.select()
        self.sound.pack(anchor="w", pady=8)

        self.tips = ctk.CTkSwitch(self, text="Show tooltips", command=self._toggle_tips)
        if app.settings.show_tooltips:
            self.tips.select()
        self.tips.pack(anchor="w", pady=8)

        ctk.CTkLabel(
            self,
            text="Shortcuts: Enter = evaluate, Esc = clear, Ctrl+Z/Y undo/redo, Ctrl+C/V copy/paste",
            font=FONT_SMALL,
            text_color=app.theme.text_muted,
            wraplength=600,
            justify="left",
        ).pack(anchor="w", pady=16)

        ctk.CTkLabel(
            self,
            text="Designed by Hussain Babar",
            font=FONT_UI,
            text_color=app.theme.cyan,
        ).pack(anchor="w", pady=24)

    def _row(self, label: str, widget) -> None:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=6)
        ctk.CTkLabel(row, text=label, width=120, anchor="w").pack(side="left")
        widget.pack(side="left")

    def _toggle_sound(self) -> None:
        self.app.settings.sound_enabled = bool(self.sound.get())
        self.app.settings_store.save()

    def _toggle_tips(self) -> None:
        self.app.settings.show_tooltips = bool(self.tips.get())
        self.app.settings_store.save()


class SplashOverlay(ctk.CTkToplevel):
    """Brief startup animation."""

    def __init__(self, parent, theme: Theme, on_finish: Callable[[], None]):
        super().__init__(parent)
        self.on_finish = on_finish
        self.overrideredirect(True)
        self.configure(fg_color=theme.bg)
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        w, h = 480, 280
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        frame = ctk.CTkFrame(self, corner_radius=24, fg_color=theme.panel)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(frame, text="Precision Calculator", font=("Segoe UI", 28, "bold"), text_color=theme.cyan).pack(
            pady=(48, 8)
        )
        ctk.CTkLabel(frame, text="Loading scientific engine…", font=FONT_UI, text_color=theme.text_muted).pack()
        self.progress = ctk.CTkProgressBar(frame, width=320, mode="indeterminate")
        self.progress.pack(pady=32)
        self.progress.start()

        ctk.CTkLabel(
            frame,
            text="Designed by Hussain Babar",
            font=FONT_SMALL,
            text_color=theme.text_muted,
        ).pack(side="bottom", pady=16)

        self.after(1600, self._close)

    def _close(self) -> None:
        self.progress.stop()
        self.destroy()
        self.on_finish()


class PrecisionCalculatorUI(ctk.CTk):
    """Root application window."""

    MIN_W, MIN_H = 1200, 800

    def __init__(self) -> None:
        super().__init__()
        self.settings_store = SettingsStore()
        self.settings: AppSettings = self.settings_store.load()
        self.theme = THEMES.get(self.settings.theme, THEMES["Dark"])
        self.history = HistoryManager()
        self.currency = CurrencyConverter()

        self.title("Precision Calculator — Designed by Hussain Babar")
        self.minsize(self.MIN_W, self.MIN_H)
        try:
            self.geometry(self.settings.window_geometry)
        except tk.TclError:
            self.geometry("1280x860")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color=self.theme.bg)

        self.sidebar = SidebarNav(self, self.theme, self.show_page)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self, fg_color=self.theme.bg, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True, padx=16, pady=16)

        self.pages: dict[str, ctk.CTkFrame] = {
            "Calculator": CalculatorPage(self.content, self),
            "Currency": CurrencyPage(self.content, self),
            "Units": UnitPage(self.content, self),
            "Statistics": StatisticsPage(self.content, self),
            "History": HistoryPage(self.content, self),
            "Graph": GraphPage(self.content, self),
            "Settings": SettingsPage(self.content, self),
        }
        self._current = "Calculator"
        self._show_immediate("Calculator")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._startup_splash)

    def _startup_splash(self) -> None:
        SplashOverlay(self, self.theme, lambda: None)

    def show_page(self, name: str) -> None:
        if name == self._current:
            return
        for page in self.pages.values():
            page.pack_forget()
        self._current = name
        page = self.pages[name]
        page.pack(fill="both", expand=True)
        if name == "History" and isinstance(page, HistoryPage):
            page.refresh()
        self.sidebar.highlight(name)

    def _show_immediate(self, name: str) -> None:
        self.pages[name].pack(fill="both", expand=True)
        self.sidebar.highlight(name)

    def set_theme(self, name: str) -> None:
        self.settings.theme = name
        self.theme = THEMES.get(name, THEMES["Dark"])
        self.settings_store.save()
        self._apply_theme()

    def _apply_theme(self) -> None:
        t = self.theme
        self.configure(fg_color=t.bg)
        self.content.configure(fg_color=t.bg)
        self.sidebar.apply_theme(t)
        for page in self.pages.values():
            if isinstance(page, CalculatorPage):
                page.apply_theme(t)

    def _on_close(self) -> None:
        self.settings.window_geometry = self.geometry()
        self.settings_store.save()
        self.destroy()
