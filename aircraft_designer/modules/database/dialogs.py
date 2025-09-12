"""Various dialogs used by Database module."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QFileDialog,
)


class AddAircraftDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un avion")
        self.name_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        layout = QFormLayout(self)
        layout.addRow("Nom", self.name_edit)
        layout.addRow("Notes", self.notes_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.name_edit.text().strip():
            return
        super().accept()

    @property
    def name(self) -> str:
        return self.name_edit.text().strip()

    @property
    def notes(self) -> str:
        return self.notes_edit.toPlainText().strip() or None


class RenameDialog(QDialog):
    def __init__(self, title: str, label: str, initial: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.edit = QLineEdit(initial)
        layout = QFormLayout(self)
        layout.addRow(label, self.edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.edit.text().strip():
            return
        super().accept()

    @property
    def text(self) -> str:
        return self.edit.text().strip()


class EditNotesDialog(QDialog):
    def __init__(self, notes: str | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Éditer les notes")
        self.notes_edit = QTextEdit()
        if notes:
            self.notes_edit.setPlainText(notes)
        layout = QFormLayout(self)
        layout.addRow("Notes", self.notes_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def notes(self) -> str | None:
        return self.notes_edit.toPlainText().strip() or None


class NewCharacteristicDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle caractéristique")
        self.name_edit = QLineEdit()
        self.unit_edit = QLineEdit()
        layout = QFormLayout(self)
        layout.addRow("Nom", self.name_edit)
        layout.addRow("Unité", self.unit_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.name_edit.text().strip():
            return
        super().accept()

    @property
    def name(self) -> str:
        return self.name_edit.text().strip()

    @property
    def unit(self) -> str | None:
        return self.unit_edit.text().strip() or None


class ImportJsonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importer JSON")
        self.path_edit = QLineEdit()
        browse_btn = QDialogButtonBox()
        layout = QFormLayout(self)
        layout.addRow("Fichier", self.path_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not Path(self.path_edit.text()).is_file():
            return
        super().accept()

    @property
    def path(self) -> Path:
        return Path(self.path_edit.text())
