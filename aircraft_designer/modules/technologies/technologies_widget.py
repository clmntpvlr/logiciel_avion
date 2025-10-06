"""Widget principal pour les technologies à utiliser."""

from __future__ import annotations

from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from .technologies_dialogs import CategoryEditDialog, OptionEditDialog
from .technologies_model import TechnologiesModel

ICONS_DIR = Path(__file__).resolve().parents[2] / "ui" / "icons"


class TechnologiesWidget(QWidget):
    """UI du module Technologies."""

    module_id = "technologies"
    module_name = "Technologies à utiliser"

    def __init__(self, controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.model: TechnologiesModel | None = None
        self.current_category_id: str | None = None

        # Widgets catégorie
        self.category_list = QListWidget()
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        self.cat_toolbar = QToolBar()
        self.cat_add_act = QAction(QIcon(str(ICONS_DIR / "tech_add.svg")), "Ajouter", self)
        self.cat_add_act.triggered.connect(self._add_category)
        self.cat_ren_act = QAction(QIcon(str(ICONS_DIR / "tech_edit.svg")), "Renommer", self)
        self.cat_ren_act.triggered.connect(self._rename_category)
        self.cat_del_act = QAction(QIcon(str(ICONS_DIR / "tech_delete.svg")), "Supprimer", self)
        self.cat_del_act.triggered.connect(self._remove_category)
        self.cat_toolbar.addAction(self.cat_add_act)
        self.cat_toolbar.addAction(self.cat_ren_act)
        self.cat_toolbar.addAction(self.cat_del_act)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.cat_toolbar)
        left_layout.addWidget(self.category_list)

        # Widgets options
        self.option_list = QListWidget()
        self.option_list.itemChanged.connect(self._on_option_toggled)
        self.opt_toolbar = QToolBar()
        self.opt_add_act = QAction(QIcon(str(ICONS_DIR / "tech_add.svg")), "Ajouter", self)
        self.opt_add_act.triggered.connect(self._add_option)
        self.opt_ren_act = QAction(QIcon(str(ICONS_DIR / "tech_edit.svg")), "Renommer", self)
        self.opt_ren_act.triggered.connect(self._rename_option)
        self.opt_del_act = QAction(QIcon(str(ICONS_DIR / "tech_delete.svg")), "Supprimer", self)
        self.opt_del_act.triggered.connect(self._remove_option)
        self.opt_toolbar.addAction(self.opt_add_act)
        self.opt_toolbar.addAction(self.opt_ren_act)
        self.opt_toolbar.addAction(self.opt_del_act)
        opt_layout = QVBoxLayout()
        opt_layout.addWidget(self.opt_toolbar)
        opt_layout.addWidget(self.option_list)
        self.options_group = QGroupBox("Options disponibles")
        self.options_group.setLayout(opt_layout)

        # Justification
        self.justif_edit = QTextEdit()
        self.justif_edit.textChanged.connect(self._on_justification_changed)
        just_layout = QVBoxLayout()
        just_layout.addWidget(self.justif_edit)
        self.justif_group = QGroupBox("Justification")
        self.justif_group.setLayout(just_layout)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self.options_group)
        right_layout.addWidget(self.justif_group)
        right_layout.addStretch()

        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)

        # Boutons bas
        self.save_btn = QPushButton("Sauvegarder")
        self.save_btn.clicked.connect(self.controller.save)
        self.reload_btn = QPushButton("Restaurer")
        self.reload_btn.clicked.connect(self.controller.reload)
        self.export_btn = QPushButton("Exporter…")
        self.export_btn.clicked.connect(self.controller.export_to_file)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(self.save_btn)
        bottom.addWidget(self.reload_btn)
        bottom.addWidget(self.export_btn)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)
        main_layout.addLayout(bottom)

    # ------------------------------------------------------------------
    def set_model(self, model: TechnologiesModel) -> None:
        self.model = model
        self.model.dataChanged.connect(lambda: self.update_from_model())
        self.model.dirtyStateChanged.connect(self._on_dirty_changed)
        self.update_from_model()

    def update_from_model(self) -> None:
        if self.model is None:
            return
        self.category_list.blockSignals(True)
        self.category_list.clear()
        for cat in self.model.payload.get("categories", []):
            item = QListWidgetItem(cat["name"])
            item.setData(Qt.UserRole, cat["id"])
            self.category_list.addItem(item)
        self.category_list.blockSignals(False)
        if self.category_list.count() and self.category_list.currentRow() == -1:
            self.category_list.setCurrentRow(0)
        self._populate_category_details()

    def _populate_category_details(self) -> None:
        if self.model is None:
            return
        item = self.category_list.currentItem()
        if item is None:
            self.current_category_id = None
            self.option_list.clear()
            self.justif_edit.clear()
            return
        self.current_category_id = item.data(Qt.UserRole)
        category = self.model._find_category(self.current_category_id)
        self.option_list.blockSignals(True)
        self.option_list.clear()
        for opt in category["options"]:
            it = QListWidgetItem(opt["label"])
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            if opt["id"] in category["selected_option_ids"]:
                it.setCheckState(Qt.Checked)
            else:
                it.setCheckState(Qt.Unchecked)
            it.setData(Qt.UserRole, opt["id"])
            self.option_list.addItem(it)
        self.option_list.blockSignals(False)
        self.justif_edit.blockSignals(True)
        self.justif_edit.setPlainText(category.get("justification", ""))
        self.justif_edit.blockSignals(False)

    # ------------------------------------------------------------------
    # Slots
    def _on_category_changed(self, index: int) -> None:
        self._populate_category_details()

    def _on_option_toggled(self, item: QListWidgetItem) -> None:
        if self.model is None or self.current_category_id is None:
            return
        ids: List[str] = []
        for i in range(self.option_list.count()):
            it = self.option_list.item(i)
            if it.checkState() == Qt.Checked:
                ids.append(it.data(Qt.UserRole))
        self.controller.set_selected_options(self.current_category_id, ids)

    def _on_justification_changed(self) -> None:
        if self.current_category_id is None or self.model is None:
            return
        self.controller.set_justification(self.current_category_id, self.justif_edit.toPlainText())

    def _on_dirty_changed(self, dirty: bool) -> None:
        self.save_btn.setEnabled(dirty)

    # ------------------------------------------------------------------
    # Category actions
    def _add_category(self) -> None:
        existing = [self.category_list.item(i).text() for i in range(self.category_list.count())]
        dlg = CategoryEditDialog(existing, parent=self)
        if dlg.exec_() == dlg.Accepted:
            self.controller.add_category(dlg.get_text())

    def _rename_category(self) -> None:
        item = self.category_list.currentItem()
        if item is None:
            return
        existing = [self.category_list.item(i).text() for i in range(self.category_list.count()) if self.category_list.item(i) is not item]
        dlg = CategoryEditDialog(existing, item.text(), self)
        if dlg.exec_() == dlg.Accepted:
            self.controller.rename_category(item.data(Qt.UserRole), dlg.get_text())

    def _remove_category(self) -> None:
        item = self.category_list.currentItem()
        if item is None:
            return
        if QMessageBox.question(
            self,
            "Confirmation",
            "Cette opération supprimera aussi toutes ses options et sélections.",
        ) == QMessageBox.Yes:
            self.controller.remove_category(item.data(Qt.UserRole))

    # ------------------------------------------------------------------
    # Option actions
    def _add_option(self) -> None:
        if self.current_category_id is None or self.model is None:
            return
        category = self.model._find_category(self.current_category_id)
        existing = [opt["label"] for opt in category["options"]]
        dlg = OptionEditDialog(existing, parent=self)
        if dlg.exec_() == dlg.Accepted:
            self.controller.add_option(self.current_category_id, dlg.get_text())

    def _rename_option(self) -> None:
        if self.current_category_id is None:
            return
        item = self.option_list.currentItem()
        if item is None or self.model is None:
            return
        category = self.model._find_category(self.current_category_id)
        existing = [opt["label"] for opt in category["options"] if opt["id"] != item.data(Qt.UserRole)]
        dlg = OptionEditDialog(existing, item.text(), self)
        if dlg.exec_() == dlg.Accepted:
            self.controller.rename_option(self.current_category_id, item.data(Qt.UserRole), dlg.get_text())

    def _remove_option(self) -> None:
        if self.current_category_id is None:
            return
        item = self.option_list.currentItem()
        if item is None:
            return
        if QMessageBox.question(self, "Confirmation", "Supprimer cette option ?") == QMessageBox.Yes:
            self.controller.remove_option(self.current_category_id, item.data(Qt.UserRole))
