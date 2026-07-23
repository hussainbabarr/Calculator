"""
Calculation history persistence, search, and export.

Designed by Hussain Babar
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

from app_paths import app_data_dir


@dataclass
class HistoryEntry:
    timestamp: str
    expression: str
    result: str
    angle_mode: str = "DEG"
    note: str = ""


class HistoryManager:
    """Unlimited in-memory history with disk backup."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else app_data_dir() / "history.json"
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        self.entries: list[HistoryEntry] = []
        self.load()

    def add(self, expression: str, result: str, angle_mode: str = "DEG") -> None:
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            expression=expression,
            result=result,
            angle_mode=angle_mode,
        )
        self.entries.insert(0, entry)
        self.save()

    def search(self, query: str) -> list[HistoryEntry]:
        q = query.strip().lower()
        if not q:
            return list(self.entries)
        return [
            e
            for e in self.entries
            if q in e.expression.lower() or q in e.result.lower()
        ]

    def clear(self) -> None:
        self.entries.clear()
        self.save()

    def load(self) -> None:
        try:
            if not self.path.is_file():
                return
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise TypeError("History data must be a list.")
            self.entries = [HistoryEntry(**item) for item in data]
        except (json.JSONDecodeError, OSError, TypeError):
            self.entries = []

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = [asdict(e) for e in self.entries]
            self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    def export_csv(self, destination: Path) -> None:
        with destination.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Timestamp", "Expression", "Result", "Angle Mode"])
            for e in self.entries:
                writer.writerow([e.timestamp, e.expression, e.result, e.angle_mode])

    def export_pdf(self, destination: Path) -> None:
        try:
            from fpdf import FPDF
        except ImportError as exc:
            raise RuntimeError("Install fpdf2 for PDF export.") from exc

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Calculator History", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, "Designed by Hussain Babar", ln=True)
        pdf.ln(4)
        for e in self.entries[:500]:
            line = f"{e.timestamp}  |  {e.expression}  =  {e.result}"
            pdf.multi_cell(0, 5, line[:200])
        pdf.output(str(destination))

    def iter_entries(self) -> Iterator[HistoryEntry]:
        yield from self.entries
