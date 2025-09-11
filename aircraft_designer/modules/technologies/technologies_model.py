"""Modèle de données pour le module Technologies."""

from __future__ import annotations

from typing import Dict, List
from uuid import uuid4

from PyQt5.QtCore import QObject, pyqtSignal

from .technologies_defaults import get_default_payload


class TechnologiesModel(QObject):
    """Maintient en mémoire la structure des technologies."""

    dataChanged = pyqtSignal()
    dirtyStateChanged = pyqtSignal(bool)

    def __init__(self, payload: Dict | None = None) -> None:
        super().__init__()
        self.payload: Dict = payload or get_default_payload()
        self._dirty = False

    # ------------------------------------------------------------------
    # Helpers
    def _mark_dirty(self, value: bool = True) -> None:
        if self._dirty != value:
            self._dirty = value
            self.dirtyStateChanged.emit(self._dirty)
        if value:
            self.dataChanged.emit()

    @property
    def dirty(self) -> bool:
        return self._dirty

    def reset_dirty(self) -> None:
        """Réinitialise l'état modifié."""
        self._mark_dirty(False)

    # ------------------------------------------------------------------
    # Category operations
    def add_category(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Le nom de catégorie ne peut pas être vide")
        if self._find_category_by_name(name) is not None:
            raise ValueError("Nom de catégorie déjà utilisé")
        cat_id = str(uuid4())
        self.payload.setdefault("categories", []).append(
            {
                "id": cat_id,
                "name": name,
                "options": [],
                "selected_option_ids": [],
                "justification": "",
            }
        )
        self._mark_dirty()
        return cat_id

    def rename_category(self, cat_id: str, new_name: str) -> None:
        category = self._find_category(cat_id)
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Le nom de catégorie ne peut pas être vide")
        existing = self._find_category_by_name(new_name)
        if existing and existing is not category:
            raise ValueError("Nom de catégorie déjà utilisé")
        category["name"] = new_name
        self._mark_dirty()

    def remove_category(self, cat_id: str) -> None:
        categories = self.payload.get("categories", [])
        for i, cat in enumerate(categories):
            if cat["id"] == cat_id:
                del categories[i]
                self._mark_dirty()
                return
        raise KeyError(cat_id)

    # ------------------------------------------------------------------
    # Option operations
    def add_option(self, cat_id: str, label: str) -> str:
        category = self._find_category(cat_id)
        label = label.strip()
        if not label:
            raise ValueError("Le libellé ne peut pas être vide")
        if self._find_option_by_label(category, label) is not None:
            raise ValueError("Option déjà existante")
        opt_id = str(uuid4())
        category["options"].append({"id": opt_id, "label": label})
        self._mark_dirty()
        return opt_id

    def rename_option(self, cat_id: str, opt_id: str, new_label: str) -> None:
        category = self._find_category(cat_id)
        option = self._find_option(category, opt_id)
        new_label = new_label.strip()
        if not new_label:
            raise ValueError("Le libellé ne peut pas être vide")
        existing = self._find_option_by_label(category, new_label)
        if existing and existing is not option:
            raise ValueError("Option déjà existante")
        option["label"] = new_label
        self._mark_dirty()

    def remove_option(self, cat_id: str, opt_id: str) -> None:
        category = self._find_category(cat_id)
        options = category["options"]
        for i, opt in enumerate(options):
            if opt["id"] == opt_id:
                del options[i]
                if opt_id in category["selected_option_ids"]:
                    category["selected_option_ids"].remove(opt_id)
                self._mark_dirty()
                return
        raise KeyError(opt_id)

    # ------------------------------------------------------------------
    # Selection & justification
    def set_selected_options(self, cat_id: str, option_ids: List[str]) -> None:
        category = self._find_category(cat_id)
        category["selected_option_ids"] = option_ids
        self._mark_dirty()

    def set_justification(self, cat_id: str, text: str) -> None:
        category = self._find_category(cat_id)
        category["justification"] = text
        self._mark_dirty()

    # ------------------------------------------------------------------
    # Access helpers
    def _find_category(self, cat_id: str) -> Dict:
        for cat in self.payload.get("categories", []):
            if cat["id"] == cat_id:
                return cat
        raise KeyError(cat_id)

    def _find_category_by_name(self, name: str) -> Dict | None:
        for cat in self.payload.get("categories", []):
            if cat["name"].lower() == name.lower():
                return cat
        return None

    def _find_option(self, category: Dict, opt_id: str) -> Dict:
        for opt in category["options"]:
            if opt["id"] == opt_id:
                return opt
        raise KeyError(opt_id)

    def _find_option_by_label(self, category: Dict, label: str) -> Dict | None:
        for opt in category["options"]:
            if opt["label"].lower() == label.lower():
                return opt
        return None
