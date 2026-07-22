# Precision Calculator

Premium cross-platform scientific calculator for desktop — **Designed by Hussain Babar**.

Modern **CustomTkinter** UI with dark glassmorphism, sidebar navigation, live currency rates, unit conversion, statistics, graphs, and unlimited history export.

## Features

- Full scientific engine (trig, hyperbolic, logs, powers, factorial, rounding, memory, ANS)
- Angle modes: **DEG**, **RAD**, **GRAD**
- Number bases: binary, octal, decimal, hexadecimal
- Currency converter with live rates ([Frankfurter API](https://www.frankfurter.app/)) and offline cache
- Unit converter (length, weight, temperature, area, volume, time, speed, pressure, energy, power, data)
- Statistics: mean, median, mode, variance, standard deviation
- History search, copy, CSV/PDF export
- Themes: Dark, Light, AMOLED, Neon Blue, Cyberpunk, Material Design
- Keyboard shortcuts, undo/redo, tooltips, optional sound

## Requirements

- Python 3.10+
- Windows, macOS, or Linux

## Install

```bash
cd calculator
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Project layout

| File | Role |
|------|------|
| `main.py` | Application entry |
| `ui.py` | CustomTkinter interface and pages |
| `calculator.py` | Safe AST evaluator and math helpers |
| `converter.py` | Currency and unit conversion |
| `history.py` | Persistent history and export |
| `settings.py` | User preferences |
| `themes.py` | Color palettes |

## Notes

- Expressions use `*` `/` `**` internally; the UI shows × ÷ and power buttons.
- Currency rates refresh in the background; offline mode uses the last saved file in `~/.precision_calculator/exchange_rates.json`.
- PDF export requires `fpdf2` (included in requirements).

## Legacy Kivy build

The previous Android/Kivy entry was replaced by this desktop app. If you still need mobile builds, restore the Kivy `main.py` from version control history.

---

**Designed by Hussain Babar**

## Android APK build

The desktop interface uses CustomTkinter. Android uses `mobile_ui.py`, a Kivy
entry point that reuses the calculator, unit conversion, currency, statistics,
and history engines. Buildozer must be run from Linux, WSL2, or a Linux CI
runner; native Windows Buildozer does not provide the Android target.

From Ubuntu/WSL2:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip buildozer cython
buildozer android debug
```

The debug APK is written under `bin/`. For a release build:

```bash
buildozer android release
```

The release artifact must then be signed and aligned with an Android keystore
before Play Store distribution. Only the `INTERNET` permission is declared;
the currency converter uses it for live rates and falls back to its local
cache when offline.
