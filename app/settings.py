"""Small persisted settings store."""

import json
from pathlib import Path


class Settings:
    path = Path.home() / ".precision_calculator.json"

    def __init__(self) -> None:
        self.values = {"theme": "Dark", "angle": "DEG"}
        try:
            self.values.update(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass

    def save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.values), encoding="utf-8")
        except OSError:
            pass