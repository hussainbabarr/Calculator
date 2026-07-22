"""Unlimited, searchable calculation history with CSV export."""

import csv
from datetime import datetime
from pathlib import Path


class HistoryStore:
    def __init__(self) -> None:
        self.items: list[dict[str, str]] = []

    def add(self, expression: str, result: str) -> None:
        self.items.insert(0, {"time": datetime.now().strftime("%H:%M"), "expression": expression, "result": result})

    def search(self, query: str = "") -> list[dict[str, str]]:
        query = query.lower().strip()
        return [item for item in self.items if not query or query in f"{item['expression']} {item['result']}".lower()]

    def clear(self) -> None:
        self.items.clear()

    def export_csv(self, path: str | Path) -> None:
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=("time", "expression", "result"))
            writer.writeheader()
            writer.writerows(self.items)