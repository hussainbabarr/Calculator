"""Application-wide configuration and constants."""

from __future__ import annotations

# --- Networking -------------------------------------------------------------
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
REQUEST_TIMEOUT_SECONDS = 8
RATE_CACHE_TTL_SECONDS = 15 * 60  # Refresh rates at most every 15 minutes

# --- Supported currencies ----------------------------------------------------
CURRENCIES: dict[str, str] = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "PKR": "Pakistani Rupee",
    "AED": "UAE Dirham",
    "SAR": "Saudi Riyal",
    "QAR": "Qatari Riyal",
    "KWD": "Kuwaiti Dinar",
    "BHD": "Bahraini Dinar",
    "OMR": "Omani Rial",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
    "KRW": "South Korean Won",
    "RUB": "Russian Ruble",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "NZD": "New Zealand Dollar",
    "CHF": "Swiss Franc",
    "INR": "Indian Rupee",
    "TRY": "Turkish Lira",
    "MYR": "Malaysian Ringgit",
    "SGD": "Singapore Dollar",
    "THB": "Thai Baht",
    "IDR": "Indonesian Rupiah",
    "BDT": "Bangladeshi Taka",
    "LKR": "Sri Lankan Rupee",
    "NPR": "Nepalese Rupee",
    "AFN": "Afghan Afghani",
    "IRR": "Iranian Rial",
    "IQD": "Iraqi Dinar",
    "EGP": "Egyptian Pound",
    "ZAR": "South African Rand",
    "NGN": "Nigerian Naira",
    "MXN": "Mexican Peso",
    "BRL": "Brazilian Real",
    "ARS": "Argentine Peso",
    "SEK": "Swedish Krona",
    "NOK": "Norwegian Krone",
    "DKK": "Danish Krone",
    "PLN": "Polish Zloty",
    "CZK": "Czech Koruna",
    "HUF": "Hungarian Forint",
    "RON": "Romanian Leu",
    "UAH": "Ukrainian Hryvnia",
    "HKD": "Hong Kong Dollar",
    "TWD": "Taiwan Dollar",
    "PHP": "Philippine Peso",
    "VND": "Vietnamese Dong",
}

DEFAULT_FROM_CURRENCY = "USD"
DEFAULT_TO_CURRENCY = "EUR"

# --- UI -----------------------------------------------------------------
WINDOW_TITLE = "Calculator & Currency Converter"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 560

COLOR_BACKGROUND = "#10141D"
COLOR_PANEL = "#181E29"
COLOR_DISPLAY = "#0C1017"
COLOR_TEXT_PRIMARY = "#F4F7FB"
COLOR_TEXT_SECONDARY = "#8D99AA"
COLOR_ACCENT = "#63A7FF"
COLOR_ACCENT_HOVER = "#7AB4FF"
COLOR_FUNCTION = "#202B3A"
COLOR_FUNCTION_HOVER = "#2B3A4F"
COLOR_DANGER = "#B84C58"
COLOR_DANGER_HOVER = "#CF5E6A"
COLOR_SUCCESS = "#278A70"
COLOR_SUCCESS_HOVER = "#35A083"
COLOR_KEY = "#252D3A"
COLOR_KEY_MUTED = "#1E2632"
COLOR_KEY_HOVER = "#344153"

_DARK_PALETTE = {
    "COLOR_BACKGROUND": "#10141D", "COLOR_PANEL": "#181E29", "COLOR_DISPLAY": "#0C1017",
    "COLOR_TEXT_PRIMARY": "#F4F7FB", "COLOR_TEXT_SECONDARY": "#8D99AA", "COLOR_ACCENT": "#63A7FF",
    "COLOR_FUNCTION": "#202B3A", "COLOR_KEY": "#252D3A", "COLOR_KEY_MUTED": "#1E2632",
}
_LIGHT_PALETTE = {
    "COLOR_BACKGROUND": "#EEF2F7", "COLOR_PANEL": "#FFFFFF", "COLOR_DISPLAY": "#E4EAF2",
    "COLOR_TEXT_PRIMARY": "#18212F", "COLOR_TEXT_SECONDARY": "#5C6878", "COLOR_ACCENT": "#2769C7",
    "COLOR_FUNCTION": "#E7EEF8", "COLOR_KEY": "#F5F7FA", "COLOR_KEY_MUTED": "#E8EDF3",
}
_dark_mode = True


def toggle_palette() -> None:
    """Switch the process palette; the next window is created with new colors."""
    global _dark_mode
    _dark_mode = not _dark_mode
    for name, value in (_DARK_PALETTE if _dark_mode else _LIGHT_PALETTE).items():
        globals()[name] = value

FONT_FAMILY = "Segoe UI"