"""
Precision Calculator — Premium desktop scientific calculator entry point.

Designed by Hussain Babar
"""

from __future__ import annotations

import sys


def main() -> None:
    if sys.platform == "android":
        from mobile_ui import run_mobile_app

        run_mobile_app()
        return

    try:
        from ui import PrecisionCalculatorUI
    except ImportError as exc:
        print("Missing dependencies. Run: pip install -r requirements.txt")
        print(exc)
        sys.exit(1)

    app = PrecisionCalculatorUI()
    app.mainloop()


if __name__ == "__main__":
    main()
