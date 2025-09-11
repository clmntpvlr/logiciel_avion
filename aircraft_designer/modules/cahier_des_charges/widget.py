"""Interface utilisateur pour le module Cahier des charges."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QScrollArea,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .model import CahierDesChargesModel
from .storage import load_cahier_des_charges, save_cahier_des_charges

CLASSIC_FIELDS: Dict[str, str] = {
    "mission": "Définition de la mission",
    "performances": "Performances requises",
    "handling": "Handling",
    "manufacturing": "Ease of manufacturing",
    "certifiability": "Certifiability",
    "upgradability": "Upgradability",
    "maintainability": "Maintainability",
    "accessibility": "Accessibility",
    "aesthetic": "Aesthetic",
    "client": "Client",
}

CONCEPT_FIELDS: Dict[str, str] = {
    "inspiration": "Inspiration / Intention",
    "public_cible": "Public cible / Scénario d’usage",
    "innovations": "Vision de rupture ou innovations",
    "contraintes": "Contraintes auto-imposées",
    "fonctionnalites_cles": "Fonctionnalités clés souhaitées",
    "croquis_ou_notes": "Croquis ou notes libres",
}

CONCEPT_TO_CLASSIC: Dict[str, str] = {
    "inspiration": "mission",
    "public_cible": "client",
    "innovations": "performances",
    "contraintes": "handling",
    "fonctionnalites_cles": "manufacturing",
    "croquis_ou_notes": "aesthetic",
}


class CahierDesChargesWidget(QWidget):
    """Widget principal du module Cahier des charges."""

    module_id = "cahier_des_charges"
    module_name = "Cahier des charges / Nouveau concept"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_path: Path | None = None
        self.model = CahierDesChargesModel()
        self.classic_edits: Dict[str, QPlainTextEdit] = {}
        self.concept_edits: Dict[str, QPlainTextEdit] = {}

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        classic_tab = self._create_classic_tab()
        concept_tab = self._create_concept_tab()
        self.tabs.addTab(classic_tab, "Cahier classique")
        self.tabs.addTab(concept_tab, "Nouveau concept")

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.save_action = QAction("Sauvegarder", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._on_save)
        self.reload_action = QAction("Recharger", self)
        self.reload_action.triggered.connect(self._on_reload)
        self.convert_action = QAction("Convertir concept → classique", self)
        self.convert_action.triggered.connect(self._convert_concept)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.reload_action)
        self.toolbar.addAction(self.convert_action)

        self.status_label = QLabel("Dernière sauvegarde : -")

        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.toolbar)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.status_label)

    # ------------------------------------------------------------------
    # UI creation helpers
    def _create_classic_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        for key, label in CLASSIC_FIELDS.items():
            group = QGroupBox(label)
            group_layout = QVBoxLayout(group)
            edit = QPlainTextEdit()
            group_layout.addWidget(edit)
            layout.addWidget(group)
            self.classic_edits[key] = edit
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def _create_concept_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        for key, label in CONCEPT_FIELDS.items():
            group = QGroupBox(label)
            group_layout = QVBoxLayout(group)
            edit = QPlainTextEdit()
            group_layout.addWidget(edit)
            layout.addWidget(group)
            self.concept_edits[key] = edit
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    # ------------------------------------------------------------------
    # Project interaction
    def load_from_project(self, project_path: Path | None) -> None:
        self.project_path = project_path
        if project_path is None:
            self.model = CahierDesChargesModel()
            self._update_ui_from_model()
            return
        self.model = load_cahier_des_charges(project_path)
        self._update_ui_from_model()

    def save_to_project(self, project_path: Path | None = None) -> None:
        project_path = project_path or self.project_path
        if project_path is None:
            return
        self._update_model_from_ui()
        self.model = save_cahier_des_charges(project_path, self.model)
        self._update_status_label()

    # ------------------------------------------------------------------
    # Event handlers
    def _on_save(self) -> None:
        self.save_to_project()

    def _on_reload(self) -> None:
        if self.project_path is not None:
            self.load_from_project(self.project_path)

    def _convert_concept(self) -> None:
        for src, dst in CONCEPT_TO_CLASSIC.items():
            self.classic_edits[dst].setPlainText(self.concept_edits[src].toPlainText())
        self.tabs.setCurrentIndex(0)
        self.model.mode = "classique"

    def _on_tab_changed(self, index: int) -> None:
        self.model.mode = "classique" if index == 0 else "concept"

    # ------------------------------------------------------------------
    # Helpers
    def _update_ui_from_model(self) -> None:
        for key, edit in self.classic_edits.items():
            edit.setPlainText(getattr(self.model.classique, key))
        for key, edit in self.concept_edits.items():
            edit.setPlainText(getattr(self.model.concept, key))
        self.tabs.setCurrentIndex(0 if self.model.mode == "classique" else 1)
        self._update_status_label()

    def _update_model_from_ui(self) -> None:
        for key, edit in self.classic_edits.items():
            setattr(self.model.classique, key, edit.toPlainText())
        for key, edit in self.concept_edits.items():
            setattr(self.model.concept, key, edit.toPlainText())

    def _update_status_label(self) -> None:
        if not self.model.last_modified_utc:
            self.status_label.setText("Dernière sauvegarde : -")
            return
        dt = datetime.fromisoformat(self.model.last_modified_utc.replace("Z", "+00:00"))
        local_dt = dt.astimezone()
        self.status_label.setText(f"Dernière sauvegarde : {local_dt:%H:%M:%S}")
