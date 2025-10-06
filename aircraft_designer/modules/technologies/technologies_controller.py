"""Contrôleur pour le module Technologies."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import pandas as pd

from .technologies_model import TechnologiesModel
from .technologies_storage import load_for_project, save_for_project
from .technologies_widget import TechnologiesWidget


class TechnologiesController(QObject):
    """Lie le modèle, la vue et la persistance."""

    def __init__(self, project_path: Path | None = None, parent=None) -> None:
        super().__init__(parent)
        self.project_path = project_path
        self.model = TechnologiesModel()
        self.widget = TechnologiesWidget(self)
        self.widget.set_model(self.model)
        if project_path is not None:
            self.on_project_loaded(project_path)

    # ------------------------------------------------------------------
    # Project interaction
    def on_project_loaded(self, project_path: Path) -> None:
        self.project_path = project_path
        payload = load_for_project(project_path)
        self.model = TechnologiesModel(payload)
        self.widget.set_model(self.model)

    def on_before_project_close(self) -> bool:
        if not self.model.dirty:
            return True
        res = QMessageBox.question(
            self.widget,
            "Sauvegarder ?",
            "Les données ont été modifiées. Sauvegarder ?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )
        if res == QMessageBox.Cancel:
            return False
        if res == QMessageBox.Yes:
            self.save()
        return True

    # ------------------------------------------------------------------
    # Persistence
    def save(self) -> None:
        if self.project_path is None:
            return
        save_for_project(self.project_path, self.model.payload)
        self.model.reset_dirty()

    def reload(self) -> None:
        if self.project_path is None:
            return
        payload = load_for_project(self.project_path)
        self.model = TechnologiesModel(payload)
        self.widget.set_model(self.model)

    # ------------------------------------------------------------------
    # Export
    def export_dataframe(self) -> pd.DataFrame:
        rows = []
        for cat in self.model.payload.get("categories", []):
            for opt in cat["options"]:
                rows.append(
                    {
                        "Category": cat["name"],
                        "Option": opt["label"],
                        "Selected": opt["id"] in cat["selected_option_ids"],
                        "Justification": cat.get("justification", ""),
                    }
                )
        return pd.DataFrame(rows)

    def export_to_file(self) -> None:
        df = self.export_dataframe()
        path, _ = QFileDialog.getSaveFileName(
            self.widget,
            "Exporter",
            str(self.project_path) if self.project_path else "",
            "CSV (*.csv)",
        )
        if path:
            df.to_csv(path, index=False)

    # ------------------------------------------------------------------
    # Model proxies
    def add_category(self, name: str) -> None:
        self.model.add_category(name)

    def rename_category(self, cat_id: str, name: str) -> None:
        self.model.rename_category(cat_id, name)

    def remove_category(self, cat_id: str) -> None:
        self.model.remove_category(cat_id)

    def add_option(self, cat_id: str, label: str) -> None:
        self.model.add_option(cat_id, label)

    def rename_option(self, cat_id: str, opt_id: str, label: str) -> None:
        self.model.rename_option(cat_id, opt_id, label)

    def remove_option(self, cat_id: str, opt_id: str) -> None:
        self.model.remove_option(cat_id, opt_id)

    def set_selected_options(self, cat_id: str, option_ids: list[str]) -> None:
        self.model.set_selected_options(cat_id, option_ids)

    def set_justification(self, cat_id: str, text: str) -> None:
        self.model.set_justification(cat_id, text)
