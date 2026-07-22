"""
Persistent application settings.

Designed by Hussain Babar
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from calculator import AngleMode, NumberBase


@dataclass
class AppSettings:
    theme: str = "Dark"
    angle_mode: str = AngleMode.DEG.value
    number_base: str = NumberBase.DEC.value
    sound_enabled: bool = False
    show_tooltips: bool = True
    font_scale: float = 1.0
    last_currency_from: str = "USD"
    last_currency_to: str = "EUR"
    window_geometry: str = "1280x860"
    recent_currencies: list[str] = field(default_factory=lambda: ["USD", "EUR", "GBP", "PKR"])


class SettingsStore:
    """Load/save settings JSON in the user config directory."""

    def __init__(self, path: Path | None = None) -> None:
        base = Path.home() / ".precision_calculator"
        base.mkdir(parents=True, exist_ok=True)
        self.path = path or (base / "settings.json")
        self.data = AppSettings()

    def load(self) -> AppSettings:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                for key, value in raw.items():
                    if hasattr(self.data, key):
                        setattr(self.data, key, value)
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        return self.data

    def save(self) -> None:
        try:
            self.path.write_text(
                json.dumps(asdict(self.data), indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass
