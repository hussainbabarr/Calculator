"""
Cross-platform paths for persistent calculator data.

Designed by Hussain Babar
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


APP_DIR_NAME = ".precision_calculator"


def _android_app_storage() -> Path | None:
    """Return Android's private writable storage directory when available."""
    if sys.platform != "android" and "ANDROID_ARGUMENT" not in os.environ:
        return None

    try:
        from android.storage import app_storage_path

        storage_path = app_storage_path()
        if storage_path:
            return Path(storage_path)
    except (ImportError, OSError, RuntimeError, TypeError):
        # python-for-android also exposes its private directory in the
        # environment, which is a safe fallback during early app startup.
        pass

    private_path = os.environ.get("ANDROID_PRIVATE")
    return Path(private_path) if private_path else None


def app_data_dir() -> Path:
    """
    Return the calculator's writable data directory.

    Directory creation is best-effort so unavailable storage can never prevent
    the calculator UI from starting. Individual stores also handle write
    failures and continue with in-memory defaults.
    """
    base = _android_app_storage()
    if base is None:
        base = Path.home() / APP_DIR_NAME

    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return base
