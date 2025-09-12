"""Utilities for managing application paths."""
from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "shared"
DATA_DIR = SHARED_DIR / "data"
LOGS_DIR = SHARED_DIR / "logs"
EXPORT_DIR = SHARED_DIR / "export"


def ensure_dir(path: Path | str) -> Path:
    """Ensure directory exists and return Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def app_shared_dir() -> Path:
    return ensure_dir(SHARED_DIR)


def db_path() -> Path:
    ensure_dir(DATA_DIR)
    return DATA_DIR / "database.sqlite"


def logs_dir() -> Path:
    return ensure_dir(LOGS_DIR)


def export_dir() -> Path:
    return ensure_dir(EXPORT_DIR)
