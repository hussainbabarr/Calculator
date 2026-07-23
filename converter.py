"""
Currency and unit conversion with live rates and offline cache.

Designed by Hussain Babar
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import requests

from app_paths import app_data_dir
from calculator import CalculatorError


# ISO 4217 codes (broad world coverage for UI + API resolution)
CURRENCY_CODES = sorted(
    {
        "USD", "EUR", "GBP", "PKR", "INR", "AED", "SAR", "CAD", "AUD", "JPY", "CNY",
        "CHF", "SGD", "HKD", "NZD", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "RON",
        "BGN", "HRK", "RUB", "TRY", "ZAR", "BRL", "MXN", "ARS", "CLP", "COP", "PEN",
        "KRW", "TWD", "THB", "MYR", "IDR", "PHP", "VND", "BDT", "LKR", "NPR", "MMK",
        "KES", "NGN", "EGP", "MAD", "TND", "QAR", "KWD", "BHD", "OMR", "JOD", "ILS",
        "UAH", "ISK", "ALL", "MKD", "RSD", "BAM", "GEL", "AZN", "KZT", "UZS",
    }
)

UNIT_CATEGORIES: dict[str, dict[str, float]] = {
    "Length": {
        "Meter": 1.0,
        "Kilometer": 1000.0,
        "Centimeter": 0.01,
        "Millimeter": 0.001,
        "Mile": 1609.344,
        "Yard": 0.9144,
        "Foot": 0.3048,
        "Inch": 0.0254,
        "Nautical Mile": 1852.0,
    },
    "Weight": {
        "Kilogram": 1.0,
        "Gram": 0.001,
        "Milligram": 1e-6,
        "Metric Ton": 1000.0,
        "Pound": 0.45359237,
        "Ounce": 0.028349523125,
        "Stone": 6.35029318,
    },
    "Temperature": {"Celsius": 1.0, "Fahrenheit": 1.0, "Kelvin": 1.0},
    "Area": {
        "Square Meter": 1.0,
        "Square Kilometer": 1e6,
        "Square Foot": 0.09290304,
        "Square Mile": 2589988.110336,
        "Acre": 4046.8564224,
        "Hectare": 10000.0,
    },
    "Volume": {
        "Liter": 1.0,
        "Milliliter": 0.001,
        "Cubic Meter": 1000.0,
        "Gallon (US)": 3.785411784,
        "Quart (US)": 0.946352946,
        "Pint (US)": 0.473176473,
        "Fluid Ounce (US)": 0.0295735295625,
    },
    "Time": {
        "Second": 1.0,
        "Millisecond": 0.001,
        "Minute": 60.0,
        "Hour": 3600.0,
        "Day": 86400.0,
        "Week": 604800.0,
    },
    "Speed": {
        "m/s": 1.0,
        "km/h": 1 / 3.6,
        "mph": 0.44704,
        "knot": 0.514444,
    },
    "Pressure": {
        "Pascal": 1.0,
        "Kilopascal": 1000.0,
        "Bar": 100000.0,
        "PSI": 6894.757293168,
        "atm": 101325.0,
        "mmHg": 133.322387415,
    },
    "Energy": {
        "Joule": 1.0,
        "Kilojoule": 1000.0,
        "Calorie": 4.184,
        "Kilocalorie": 4184.0,
        "kWh": 3.6e6,
        "BTU": 1055.05585262,
    },
    "Power": {
        "Watt": 1.0,
        "Kilowatt": 1000.0,
        "Megawatt": 1e6,
        "Horsepower": 745.69987158227,
    },
    "Data Storage": {
        "Byte": 1.0,
        "KB": 1024.0,
        "MB": 1048576.0,
        "GB": 1073741824.0,
        "TB": 1099511627776.0,
    },
}


def convert_unit(category: str, value: float, source: str, target: str) -> float:
    if category not in UNIT_CATEGORIES:
        raise CalculatorError("Unknown unit category.")
    units = UNIT_CATEGORIES[category]
    if source not in units or target not in units:
        raise CalculatorError("Invalid unit selection.")
    if category == "Temperature":
        celsius = _to_celsius(value, source)
        return _from_celsius(celsius, target)
    return value * units[source] / units[target]


def _to_celsius(value: float, unit: str) -> float:
    if unit == "Kelvin":
        return value - 273.15
    if unit == "Fahrenheit":
        return (value - 32) * 5 / 9
    return value


def _from_celsius(celsius: float, unit: str) -> float:
    if unit == "Kelvin":
        return celsius + 273.15
    if unit == "Fahrenheit":
        return celsius * 9 / 5 + 32
    return celsius


class CurrencyConverter:
    """
    Fetches EUR-based rates from Frankfurter (free, no API key).
    Falls back to cached rates on disk when offline.
    """

    API_URL = "https://api.frankfurter.app/latest"
    CACHE_FILE = app_data_dir() / "exchange_rates.json"

    def __init__(self, cache_file: Path | None = None) -> None:
        self.cache_file = Path(cache_file) if cache_file is not None else self.CACHE_FILE
        self.base = "EUR"
        self.rates: dict[str, float] = {"EUR": 1.0}
        self.updated_at: str | None = None
        self._load_cache()

    def _load_cache(self) -> None:
        try:
            data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("rates"), dict):
                raise ValueError("Invalid exchange-rate cache.")
            self.rates = data["rates"]
            self.updated_at = data.get("updated_at")
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            self._seed_fallback()

    def _seed_fallback(self) -> None:
        """Approximate static rates (EUR base) for offline use."""
        self.rates = {
            "EUR": 1.0,
            "USD": 1.08,
            "GBP": 0.85,
            "PKR": 300.0,
            "INR": 90.0,
            "AED": 3.97,
            "SAR": 4.05,
            "CAD": 1.47,
            "AUD": 1.65,
            "JPY": 163.0,
            "CNY": 7.85,
            "CHF": 0.96,
            "SGD": 1.45,
            "TRY": 35.0,
            "ZAR": 20.0,
            "BRL": 5.4,
            "MXN": 18.5,
        }
        self.updated_at = "offline (approximate)"

    def _save_cache(self) -> None:
        payload = {
            "updated_at": self.updated_at,
            "rates": self.rates,
        }
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    def refresh(self, on_done: Callable[[bool, str], None] | None = None) -> None:
        def worker() -> None:
            ok, msg = self._fetch()
            if on_done:
                on_done(ok, msg)

        threading.Thread(target=worker, daemon=True).start()

    def _fetch(self) -> tuple[bool, str]:
        try:
            response = requests.get(self.API_URL, timeout=12)
            response.raise_for_status()
            data = response.json()
            self.base = data.get("base", "EUR")
            self.rates = {self.base: 1.0, **data.get("rates", {})}
            self.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            self._save_cache()
            return True, f"Rates updated ({self.updated_at})"
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            if len(self.rates) <= 2:
                self._seed_fallback()
            return False, "Using saved offline exchange rates."

    def convert(self, amount: float, source: str, target: str) -> float:
        source = source.upper()
        target = target.upper()
        if source == target:
            return amount
        if source not in self.rates or target not in self.rates:
            raise CalculatorError(
                f"Rate unavailable for {source} or {target}. Refresh rates when online."
            )
        # Convert via EUR base: amount in source -> EUR -> target
        in_eur = amount / self.rates[source]
        return in_eur * self.rates[target]

    def search_currencies(self, query: str) -> list[str]:
        q = query.strip().upper()
        if not q:
            return list(CURRENCY_CODES)
        return [c for c in CURRENCY_CODES if q in c]
