"""Boîtes de dialogue pour le module Technologies."""

from __future__ import annotations

from typing import Iterable

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)


class _BaseEditDialog(QDialog):
    def __init__(self, title: str, text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.edit = QLineEdit(text)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QFormLayout(self)
        layout.addRow("Nom", self.edit)
        layout.addWidget(buttons)

    def get_text(self) -> str:
        return self.edit.text().strip()


class CategoryEditDialog(_BaseEditDialog):
    """Ajout ou renommage d'une catégorie."""

    def __init__(self, existing: Iterable[str], text: str = "", parent=None) -> None:
        super().__init__("Catégorie", text, parent)
        self._existing = {n.lower() for n in existing}

    def accept(self) -> None:  # type: ignore[override]
        name = self.get_text()
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom ne peut pas être vide")
            return
        if name.lower() in self._existing:
            QMessageBox.warning(self, "Erreur", "Nom déjà utilisé")
            return
        super().accept()


class OptionEditDialog(_BaseEditDialog):
    """Ajout ou renommage d'une option."""

    def __init__(self, existing: Iterable[str], text: str = "", parent=None) -> None:
        super().__init__("Option", text, parent)
        self._existing = {n.lower() for n in existing}

    def accept(self) -> None:  # type: ignore[override]
        label = self.get_text()
        if not label:
            QMessageBox.warning(self, "Erreur", "Le libellé ne peut pas être vide")
            return
        if label.lower() in self._existing:
            QMessageBox.warning(self, "Erreur", "Option déjà existante")
            return
        super().accept()
