"""
Theme definitions for the premium calculator UI.

Designed by Hussain Babar
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    panel: str
    panel_alt: str
    glass: str
    text: str
    text_muted: str
    accent: str
    accent_hover: str
    cyan: str
    danger: str
    success: str
    shadow: str
    button: str
    button_hover: str
    operator: str
    operator_hover: str
    sidebar: str
    display_bg: str
    error: str


def _t(
    name: str,
    bg: str,
    panel: str,
    panel_alt: str,
    text: str,
    accent: str,
    cyan: str,
    *,
    light: bool = False,
) -> Theme:
    glass = panel_alt if light else f"{panel_alt}CC"
    return Theme(
        name=name,
        bg=bg,
        panel=panel,
        panel_alt=panel_alt,
        glass=glass,
        text=text,
        text_muted="#8ba3b8" if not light else "#5a7085",
        accent=accent,
        accent_hover=_blend(accent, cyan, 0.35),
        cyan=cyan,
        danger="#ff4d6d" if not light else "#c62828",
        success="#2ee59d" if not light else "#1b8a5a",
        shadow="#00000055" if not light else "#00000022",
        button=panel_alt,
        button_hover=_blend(panel_alt, accent, 0.25),
        operator=accent,
        operator_hover=_blend(accent, cyan, 0.4),
        sidebar=_blend(bg, panel, 0.5),
        display_bg=_blend(bg, panel, 0.35),
        error="#ff6b6b",
    )


def _blend(a: str, b: str, t: float) -> str:
    """Simple hex color blend."""
    ar, ag, ab = _hex_rgb(a)
    br, bg, bb = _hex_rgb(b)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    bl = int(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"


def _hex_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")[:6]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


THEMES: dict[str, Theme] = {
    "Dark": _t(
        "Dark",
        "#05080f",
        "#0c1424",
        "#121e33",
        "#e8f4ff",
        "#1a6fd4",
        "#28d7ff",
    ),
    "Light": _t(
        "Light",
        "#e8eef5",
        "#ffffff",
        "#dce8f4",
        "#0f1f33",
        "#087eaf",
        "#00a8cc",
        light=True,
    ),
    "AMOLED": _t(
        "AMOLED",
        "#000000",
        "#0a0c10",
        "#141820",
        "#f5fbff",
        "#0088ff",
        "#00e5ff",
    ),
    "Neon Blue": _t(
        "Neon Blue",
        "#040a18",
        "#0a1630",
        "#122050",
        "#eef6ff",
        "#0066ff",
        "#58ecff",
    ),
    "Cyberpunk": Theme(
        name="Cyberpunk",
        bg="#0d0814",
        panel="#1a1028",
        panel_alt="#2a1840",
        glass="#2a1840CC",
        text="#fff5ff",
        text_muted="#b89fd0",
        accent="#ff2d95",
        accent_hover="#ff6bb5",
        cyan="#ffdc4a",
        danger="#ff3355",
        success="#39ff14",
        shadow="#00000066",
        button="#241535",
        button_hover="#3d2558",
        operator="#ff2d95",
        operator_hover="#ff6bb5",
        sidebar="#120a1c",
        display_bg="#150f20",
        error="#ff5577",
    ),
    "Material Design": _t(
        "Material Design",
        "#121212",
        "#1e1e1e",
        "#2d2d2d",
        "#fafafa",
        "#bb86fc",
        "#03dac6",
    ),
}

DEFAULT_THEME = "Dark"
