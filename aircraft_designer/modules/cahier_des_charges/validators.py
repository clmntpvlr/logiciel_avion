"""Fonctions de validation et de nettoyage."""

from __future__ import annotations

from typing import Any, Dict

from .model import CahierDesChargesModel


DEFAULT_DICT = CahierDesChargesModel().to_dict()


def _clean_str(value: Any) -> str:
    return str(value).strip()


def sanitize_loaded_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """S'assure que la structure des données correspond au modèle."""
    def recursive(default: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, default_value in default.items():
            if isinstance(default_value, dict):
                current_value = current.get(key, {}) if isinstance(current.get(key), dict) else {}
                result[key] = recursive(default_value, current_value)
            else:
                result[key] = _clean_str(current.get(key, default_value))
        return result

    return recursive(DEFAULT_DICT, data or {})


def trim_model(model: CahierDesChargesModel) -> None:
    """Supprime les espaces inutiles dans le modèle."""
    for key, value in model.classique.__dict__.items():
        setattr(model.classique, key, _clean_str(value))
    for key, value in model.concept.__dict__.items():
        setattr(model.concept, key, _clean_str(value))
    model.mode = model.mode.strip() or "classique"
