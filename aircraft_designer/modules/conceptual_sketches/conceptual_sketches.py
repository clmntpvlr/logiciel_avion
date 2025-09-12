"""Gestion des croquis conceptuels par projet."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QFileDialog,
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from ...core.module_loader import ModuleBase
from ...core.paths import ensure_dir, get_project_conceptual_sketches_dir


class ConceptualSketchesWidget(QWidget):
    """Interface utilisateur pour la gestion des croquis conceptuels."""

    module_name = "Conceptual Sketches"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root: Path | None = None
        self.data_dir: Path | None = None
        self.json_path: Path | None = None
        self.images: List[dict] = []
        self.current_index: int | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.add_btn = QPushButton("Ajouter une image")
        self.add_btn.clicked.connect(self._add_image)

        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(128, 128))
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.itemClicked.connect(self._on_item_selected)
        self.image_list.itemDoubleClicked.connect(self._show_full_image)

        left = QVBoxLayout()
        left.addWidget(self.add_btn)
        left.addWidget(self.image_list)

        self.preview = QLabel()
        self.preview.setMinimumSize(200, 200)
        self.preview.setAlignment(Qt.AlignCenter)

        self.desc_edit = QTextEdit()
        self.desc_edit.textChanged.connect(self._on_desc_changed)

        self.del_btn = QPushButton("Supprimer")
        self.del_btn.clicked.connect(self._remove_current)

        right = QVBoxLayout()
        right.addWidget(self.preview, 1)
        right.addWidget(self.desc_edit)
        right.addWidget(self.del_btn)

        layout = QHBoxLayout(self)
        layout.addLayout(left)
        layout.addLayout(right, 1)

    # ------------------------------------------------------------------
    def load_from_project(self, project_root: Path) -> None:
        """Charge les données du projet spécifié."""
        self.project_root = Path(project_root)
        self.data_dir = get_project_conceptual_sketches_dir(self.project_root)
        self.json_path = self.data_dir / "conceptual_sketches.json"
        self._load_images()

    # ------------------------------------------------------------------
    def _load_images(self) -> None:
        self.images = []
        if self.json_path and self.json_path.exists():
            try:
                self.images = json.loads(self.json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.images = []
        self._refresh_list()

    # ------------------------------------------------------------------
    def _refresh_list(self) -> None:
        self.image_list.clear()
        for img in self.images:
            path = self.data_dir / img["filename"] if self.data_dir else None
            icon = QIcon(str(path)) if path and path.exists() else QIcon()
            item = QListWidgetItem(icon, img["filename"])
            self.image_list.addItem(item)

    # ------------------------------------------------------------------
    def _add_image(self) -> None:
        if not self.data_dir:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return
        src = Path(file_path)
        dest = self.data_dir / src.name
        i = 1
        while dest.exists():
            dest = self.data_dir / f"{src.stem}_{i}{src.suffix}"
            i += 1
        shutil.copy(src, dest)
        self.images.append({"filename": dest.name, "description": ""})
        self._save()
        self._refresh_list()

    # ------------------------------------------------------------------
    def _on_item_selected(self, item: QListWidgetItem) -> None:
        self.current_index = self.image_list.row(item)
        self._update_preview()
        self.desc_edit.blockSignals(True)
        self.desc_edit.setPlainText(self.images[self.current_index]["description"])
        self.desc_edit.blockSignals(False)

    # ------------------------------------------------------------------
    def _update_preview(self) -> None:
        if self.current_index is None or not self.data_dir:
            self.preview.clear()
            return
        path = self.data_dir / self.images[self.current_index]["filename"]
        if not path.exists():
            self.preview.clear()
            return
        pix = QPixmap(str(path))
        self.preview.setPixmap(
            pix.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    # ------------------------------------------------------------------
    def resizeEvent(self, event):  # noqa: ANN001 - Qt signature
        super().resizeEvent(event)
        self._update_preview()

    # ------------------------------------------------------------------
    def _on_desc_changed(self) -> None:
        if self.current_index is None:
            return
        self.images[self.current_index]["description"] = self.desc_edit.toPlainText()
        self._save()

    # ------------------------------------------------------------------
    def _remove_current(self) -> None:
        if self.current_index is None or not self.data_dir:
            return
        img = self.images.pop(self.current_index)
        try:
            (self.data_dir / img["filename"]).unlink()
        except FileNotFoundError:
            pass
        self.current_index = None
        self.preview.clear()
        self.desc_edit.clear()
        self._save()
        self._refresh_list()

    # ------------------------------------------------------------------
    def _show_full_image(self, item: QListWidgetItem) -> None:
        if not self.data_dir:
            return
        idx = self.image_list.row(item)
        path = self.data_dir / self.images[idx]["filename"]
        if not path.exists():
            QMessageBox.warning(self, "Erreur", "Fichier introuvable")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(self.images[idx]["filename"])
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(path))
        lbl.setPixmap(pix)
        scroll = QScrollArea()
        scroll.setWidget(lbl)
        scroll.setWidgetResizable(True)
        lay = QVBoxLayout(dlg)
        lay.addWidget(scroll)
        dlg.resize(600, 600)
        dlg.exec_()

    # ------------------------------------------------------------------
    def _save(self) -> None:
        if not self.json_path:
            return
        ensure_dir(self.json_path.parent)
        self.json_path.write_text(
            json.dumps(self.images, indent=2, ensure_ascii=False), encoding="utf-8"
        )


class ConceptualSketchesModule(ModuleBase):
    """Point d'entrée du module Conceptual Sketches."""

    module_name = "Conceptual Sketches"

    def get_widget(self):  # noqa: ANN201 - Qt API
        widget = ConceptualSketchesWidget()
        widget.load_from_project(self.project.path)
        return widget
