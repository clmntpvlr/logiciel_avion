"""Utilities for managing application paths."""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "AircraftDesigner"


def ensure_dir(path: Path | str) -> Path:
    """Ensure directory exists and return Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _resolve_user_root() -> Path:
    """Return the base directory for user-specific data."""
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_DIR_NAME
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def user_root() -> Path:
    return ensure_dir(_resolve_user_root())


def app_shared_dir() -> Path:
    # Backward compatibility helper; returns the user data root.
    return user_root()


def db_path() -> Path:
    data_dir = ensure_dir(user_root() / "data")
    return data_dir / "database.sqlite"


def logs_dir() -> Path:
    return ensure_dir(user_root() / "logs")


def export_dir() -> Path:
    return ensure_dir(user_root() / "export")


def projects_dir() -> Path:
    return ensure_dir(user_root() / "projects")
