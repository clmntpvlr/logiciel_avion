"""Gestion de la persistance pour le module Cahier des charges."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .model import CahierDesChargesModel
from .validators import sanitize_loaded_dict, trim_model

FILE_NAME = "cahier_des_charges.json"


def load_cahier_des_charges(project_path: Path) -> CahierDesChargesModel:
    """Charge les données du projet."""
    file_path = project_path / FILE_NAME
    if not file_path.is_file():
        return CahierDesChargesModel()
    with open(file_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    data = sanitize_loaded_dict(data)
    return CahierDesChargesModel.from_dict(data)


def save_cahier_des_charges(project_path: Path, model: CahierDesChargesModel) -> CahierDesChargesModel:
    """Sauvegarde les données du module de manière atomique."""
    trim_model(model)
    model.last_modified_utc = datetime.utcnow().isoformat() + "Z"
    data = model.to_dict()
    file_path = project_path / FILE_NAME
    tmp_path = file_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    tmp_path.replace(file_path)
    return model
