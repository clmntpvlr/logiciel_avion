"""Persistance JSON pour le module Technologies."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from .technologies_defaults import get_default_payload


FILENAME = "technologies.json"


def migrate_if_needed(payload: Dict) -> Dict:
    """Met à jour le payload si la version change."""
    # Version actuelle : 1
    return payload


def load_for_project(project_path: Path) -> Dict:
    """Charge les données pour un projet."""
    modules_dir = project_path / "modules"
    file_path = modules_dir / FILENAME
    if not file_path.exists():
        return get_default_payload()
    with file_path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return migrate_if_needed(payload)


def save_for_project(project_path: Path, payload: Dict) -> None:
    """Sauvegarde les données pour un projet."""
    modules_dir = project_path / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)
    file_path = modules_dir / FILENAME
    tmp_path = file_path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    os.replace(tmp_path, file_path)
