"""Main widget for Database module."""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QGroupBox,
    QLabel,
    QToolBar,
    QAction,
    QMessageBox,
    QAbstractItemView,
    QFileDialog,
    QShortcut,
    QSizePolicy,
    QHeaderView,
)

from .repository import DatabaseRepository, DuplicateNameError, NotFoundError
from .dialogs import (
    AddAircraftDialog,
    RenameDialog,
    EditNotesDialog,
    NewCharacteristicDialog,
)
from ...utils.paths import export_dir
from ...ui.widgets.no_wheel_combobox import NoWheelComboBox

DEBUG = True


class DatabaseWidget(QWidget):
    module_name = "Database"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = DatabaseRepository()
        self.current_aircraft_id: Optional[int] = None
        self._build_ui()
        self.refresh_all()

    # UI setup
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        self.toolbar = QToolBar()
        self._setup_toolbar()
        main_layout.addWidget(self.toolbar)

        body = QHBoxLayout()
        main_layout.addLayout(body)

        # left column - aircraft list
        left_layout = QVBoxLayout()
        body.addLayout(left_layout)
        # Advanced filter group (above search)
        self.advFilterGroup = QGroupBox("Filtre avancé")
        adv_layout = QVBoxLayout(self.advFilterGroup)
        row1 = QHBoxLayout()
        adv_layout.addLayout(row1)
        self.filterCharCombo = QComboBox()
        self.filterOpCombo = QComboBox()
        self.filterOpCombo.addItems(["=", "≠", ">", "≥", "<", "≤", "in [a,b]"])
        row1.addWidget(self.filterCharCombo)
        row1.addWidget(self.filterOpCombo)
        row2 = QHBoxLayout()
        adv_layout.addLayout(row2)
        self.filterVal1Edit = QLineEdit()
        self.filterVal1Edit.setPlaceholderText("valeur / borne min")
        self.filterVal2Edit = QLineEdit()
        self.filterVal2Edit.setPlaceholderText("borne max")
        self.filterVal2Edit.setVisible(False)
        row2.addWidget(self.filterVal1Edit)
        row2.addWidget(self.filterVal2Edit)
        row3 = QHBoxLayout()
        adv_layout.addLayout(row3)
        self.filterApplyBtn = QPushButton("Appliquer")
        self.filterClearBtn = QPushButton("Effacer")
        row3.addWidget(self.filterApplyBtn)
        row3.addWidget(self.filterClearBtn)
        self.filterInfoLabel = QLabel("")
        self.filterInfoLabel.setStyleSheet("color:#777; font-size:11px;")
        self.filterInfoLabel.setVisible(False)
        adv_layout.addWidget(self.filterInfoLabel)
        left_layout.addWidget(self.advFilterGroup)

        # State + signals for advanced filter
        self._adv_filter_active = False
        self._adv_filtered = []  # list[(id, name)]
        self.filterOpCombo.currentTextChanged.connect(self._on_filter_op_changed)
        self.filterApplyBtn.clicked.connect(self._apply_advanced_filter)
        self.filterClearBtn.clicked.connect(self._clear_advanced_filter)
        self.aircraft_search = QLineEdit()
        self.aircraft_search.setPlaceholderText("Rechercher…")
        self.aircraft_search.textChanged.connect(self.refresh_aircrafts)
        left_layout.addWidget(self.aircraft_search)
        self.aircraft_list = QListWidget()
        self.aircraft_list.currentRowChanged.connect(self._aircraft_selected)
        left_layout.addWidget(self.aircraft_list)
        btn_layout = QHBoxLayout()
        left_layout.addLayout(btn_layout)
        self.btn_add_aircraft = QPushButton("➕")
        self.btn_add_aircraft.clicked.connect(self.add_aircraft)
        self.btn_rename_aircraft = QPushButton("✏️")
        self.btn_rename_aircraft.clicked.connect(self.rename_aircraft)
        self.btn_notes_aircraft = QPushButton("🗒️")
        self.btn_notes_aircraft.clicked.connect(self.edit_notes)
        self.btn_del_aircraft = QPushButton("❌")
        self.btn_del_aircraft.clicked.connect(self.delete_aircraft)
        for b in [self.btn_add_aircraft, self.btn_rename_aircraft, self.btn_notes_aircraft, self.btn_del_aircraft]:
            btn_layout.addWidget(b)

        # center column - table values
        center_layout = QVBoxLayout()
        body.addLayout(center_layout)

        # Center search bar (above the table)
        center_search_row = QHBoxLayout()
        self.centerSearchEdit = QLineEdit()
        self.centerSearchEdit.setPlaceholderText("Rechercher une caractéristique...")
        self.centerSearchClearBtn = QPushButton("Effacer")
        center_search_row.addWidget(self.centerSearchEdit)
        center_search_row.addWidget(self.centerSearchClearBtn)
        center_layout.addLayout(center_search_row)

        # Status label (empty by default)
        self.centerSearchStatus = QLabel("")
        self.centerSearchStatus.setStyleSheet("color: #888; font-size: 11px;")
        center_layout.addWidget(self.centerSearchStatus)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Caractéristique", "Valeur", "Unité"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        center_layout.addWidget(self.table)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table_btns = QHBoxLayout()
        center_layout.addLayout(table_btns)
        self.btn_add_value = QPushButton("➕")
        self.btn_add_value.clicked.connect(self.add_value_row)
        self.btn_del_value = QPushButton("❌")
        self.btn_del_value.clicked.connect(self.remove_value_row)
        table_btns.addWidget(self.btn_add_value)
        table_btns.addWidget(self.btn_del_value)

        # Connections for center search
        self.centerSearchEdit.textChanged.connect(self._apply_center_search_filter)
        self.centerSearchClearBtn.clicked.connect(self._clear_center_search_filter)

        # Ctrl+F shortcut to focus the center search
        self.centerSearchShortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.centerSearchShortcut.activated.connect(self._focus_center_search)

        # right column - characteristic list
        right_layout = QVBoxLayout()
        body.addLayout(right_layout)
        self.char_search = QLineEdit()
        self.char_search.setPlaceholderText("Rechercher…")
        self.char_search.textChanged.connect(self.refresh_characteristics)
        right_layout.addWidget(self.char_search)
        self.char_list = QListWidget()
        right_layout.addWidget(self.char_list)
        char_btns = QHBoxLayout()
        right_layout.addLayout(char_btns)
        self.btn_rename_char = QPushButton("✏️")
        self.btn_rename_char.clicked.connect(self.rename_characteristic)
        self.btn_unit_char = QPushButton("🧪")
        self.btn_unit_char.clicked.connect(self.update_char_unit)
        self.btn_del_char = QPushButton("❌")
        self.btn_del_char.clicked.connect(self.delete_characteristic)
        for b in [self.btn_rename_char, self.btn_unit_char, self.btn_del_char]:
            char_btns.addWidget(b)

    def _setup_toolbar(self):
        refresh_act = QAction("🔄 Actualiser", self)
        refresh_act.triggered.connect(self.refresh_all)
        self.toolbar.addAction(refresh_act)
        export_act = QAction("📦 Exporter", self)
        export_act.triggered.connect(self.export_json)
        self.toolbar.addAction(export_act)
        import_act = QAction("⏳ Importer", self)
        import_act.triggered.connect(self.import_json)
        self.toolbar.addAction(import_act)
        if DEBUG:
            demo_act = QAction("⚙️ Remplir exemples", self)
            demo_act.triggered.connect(self.fill_examples)
            self.toolbar.addAction(demo_act)

    # refreshing
    def refresh_all(self):
        self.refresh_aircrafts()
        self.refresh_characteristics()
        self.load_values()

    def refresh_aircrafts(self):
        search_text = (self.aircraft_search.text() or "").strip().lower()
        self.aircraft_list.clear()

        # Base list: advanced subset or full list
        if self._adv_filter_active:
            items = list(self._adv_filtered)
        else:
            items = [(a.id, a.name) for a in self.repo.list_aircrafts(None)]

        # Apply simple search on top of base list
        if search_text:
            items = [(i, n) for (i, n) in items if search_text in (n or "").lower()]

        # Show message when advanced filter active and no results
        if self._adv_filter_active and not items:
            self.filterInfoLabel.setText("Aucun avion ne correspond au filtre")
            self.filterInfoLabel.setVisible(True)
        elif not self._adv_filter_active:
            self.filterInfoLabel.setVisible(False)

        # Build lightweight objects for compatibility with existing code
        self.aircrafts = [type("_A", (), {"id": aid, "name": name, "notes": None})() for (aid, name) in items]
        for _, name in items:
            self.aircraft_list.addItem(name)
        if self.current_aircraft_id:
            for i, a in enumerate(self.aircrafts):
                if a.id == self.current_aircraft_id:
                    self.aircraft_list.setCurrentRow(i)
                    break

    def refresh_characteristics(self):
        filter_text = self.char_search.text().strip() or None
        self.char_list.clear()
        self.chars = self.repo.list_characteristics(filter_text)
        for c in self.chars:
            self.char_list.addItem(c.name)
        # Keep the advanced filter characteristic combo in sync with global list
        all_chars = self.repo.list_characteristics()
        prev = self.filterCharCombo.currentText() if hasattr(self, "filterCharCombo") else ""
        self.filterCharCombo.blockSignals(True)
        self.filterCharCombo.clear()
        for ch in all_chars:
            self.filterCharCombo.addItem(ch.name)
        if prev:
            idx = self.filterCharCombo.findText(prev)
            if idx >= 0:
                self.filterCharCombo.setCurrentIndex(idx)
        self.filterCharCombo.blockSignals(False)

    # handlers
    def _aircraft_selected(self, row: int):
        if row < 0 or row >= len(getattr(self, "aircrafts", [])):
            self.current_aircraft_id = None
        else:
            self.current_aircraft_id = self.aircrafts[row].id
        self.load_values()

    def load_values(self):
        self.table.setRowCount(0)
        if not self.current_aircraft_id:
            return
        values = self.repo.get_values_for_aircraft(self.current_aircraft_id)
        for v in values:
            self._add_value_row(v["characteristic_id"], v["name"], v["value"], v["unit"])
        # Re-apply center search filter after table repopulation
        if hasattr(self, "centerSearchEdit"):
            self._apply_center_search_filter()

    def _add_value_row(self, char_id: int | None = None, name: str = "", value: str = "", unit: str | None = None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # Use NoWheelComboBox to avoid accidental wheel-driven changes
        # when the popup is not open (UX safeguard for the characteristics column)
        combo = NoWheelComboBox()
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        combo_items = [(c.id, c.name) for c in self.repo.list_characteristics()]
        for cid, cname in combo_items:
            combo.addItem(cname, cid)
        # Add the on-demand creation entry. When there are no existing
        # characteristics, the combo would otherwise have this as the only
        # item and selecting it would not emit currentIndexChanged.
        combo.addItem("<Nouvelle…>", -1)
        if char_id:
            idx = combo.findData(char_id)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        else:
            # Ensure no default selection so choosing "<Nouvelle…>"
            # triggers the signal even when it's the only option.
            combo.setCurrentIndex(-1)
        combo.currentIndexChanged.connect(lambda _: self._combo_changed(combo))
        combo_container = QWidget()
        combo_container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )
        combo_layout = QHBoxLayout(combo_container)
        combo_layout.setContentsMargins(0, 0, 0, 0)
        combo_layout.setSpacing(0)
        combo_layout.addWidget(combo)
        combo_container.setProperty("_value_combo", combo)
        self.table.setCellWidget(row, 0, combo_container)
        val_item = QLineEdit(value)
        val_item.editingFinished.connect(lambda v=val_item, c=combo: self._value_changed(v, c))
        self.table.setCellWidget(row, 1, val_item)
        unit_item = QTableWidgetItem(unit or "")
        unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 2, unit_item)

    def add_value_row(self):
        if not self.current_aircraft_id:
            return
        self._add_value_row()
        # Keep current filter applied when adding a row
        if hasattr(self, "centerSearchEdit"):
            self._apply_center_search_filter()

    def remove_value_row(self):
        rows = {index.row() for index in self.table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            combo = self._combo_from_cell(self.table.cellWidget(row, 0))
            if combo is None:
                continue
            char_id = combo.currentData()
            if self.current_aircraft_id and char_id not in (None, -1):
                self.repo.remove_aircraft_value(self.current_aircraft_id, char_id)
            self.table.removeRow(row)
        # Re-apply current filter after deletions
        if hasattr(self, "centerSearchEdit"):
            self._apply_center_search_filter()

    def _combo_changed(self, combo: QComboBox):
        char_id = combo.currentData()
        if char_id == -1:
            dlg = NewCharacteristicDialog(self)
            if dlg.exec_() == dlg.Accepted:
                try:
                    new_id = self.repo.create_characteristic(dlg.name, dlg.unit)
                    self.refresh_characteristics()
                    combo.clear()
                    for c in self.repo.list_characteristics():
                        combo.addItem(c.name, c.id)
                    combo.addItem("<Nouvelle…>", -1)
                    combo.setCurrentIndex(combo.findData(new_id))
                    # Update the unit cell immediately for this row
                    row = -1
                    for r in range(self.table.rowCount()):
                        if self._combo_from_cell(self.table.cellWidget(r, 0)) is combo:
                            row = r
                            break
                    if row != -1:
                        item = self.table.item(row, 2)
                        if item is not None:
                            item.setText(dlg.unit or "")
                except DuplicateNameError:
                    QMessageBox.warning(self, "Erreur", "Nom déjà utilisé")
        else:
            # Robustly find the row containing this combo to avoid invalid
            # coordinates with the table viewport.
            row = -1
            for r in range(self.table.rowCount()):
                if self._combo_from_cell(self.table.cellWidget(r, 0)) is combo:
                    row = r
                    break
            if row == -1:
                return
            unit = self.repo.get_characteristic(char_id).unit
            item = self.table.item(row, 2)
            if item is not None:
                item.setText(unit or "")
            value_widget = self.table.cellWidget(row, 1)
            if value_widget is not None:
                self._value_changed(value_widget, combo)

    def _value_changed(self, line: QLineEdit, combo: QComboBox):
        if not self.current_aircraft_id:
            return
        char_id = combo.currentData()
        # Ignore placeholder selection or no selection
        if char_id in (None, -1):
            return
        text = line.text().strip()
        if not text:
            return
        try:
            self.repo.set_aircraft_value(self.current_aircraft_id, int(char_id), text)
        except Exception as exc:  # pragma: no cover - UI error display
            QMessageBox.warning(self, "Erreur", str(exc))

    # Center search helpers
    def _focus_center_search(self):
        self.centerSearchEdit.setFocus(Qt.TabFocusReason)
        self.centerSearchEdit.selectAll()

    def _apply_center_search_filter(self):
        pattern = (self.centerSearchEdit.text() or "").strip().lower()
        table = self.table
        any_visible = False
        for row in range(table.rowCount()):
            name = ""
            w = table.cellWidget(row, 0)
            combo = self._combo_from_cell(w)
            if combo is not None:
                name = (combo.currentText() or "")
            else:
                item = table.item(row, 0)
                if item is not None:
                    name = item.text() or ""
            name = name.strip().lower()
            match = (pattern in name) if pattern else True
            table.setRowHidden(row, not match)
            if match:
                any_visible = True
        self.centerSearchStatus.setText("" if any_visible else "Aucune caractéristique ne correspond")

    def _clear_center_search_filter(self):
        self.centerSearchEdit.clear()
        self._apply_center_search_filter()

    # Advanced filter: UI handlers
    def _on_filter_op_changed(self, op: str) -> None:
        self.filterVal2Edit.setVisible(op == "in [a,b]")

    def _combo_from_cell(self, widget: QWidget | None) -> QComboBox | None:
        if isinstance(widget, QComboBox):
            return widget
        if widget is None:
            return None
        combo = widget.property("_value_combo")
        if isinstance(combo, QComboBox):
            return combo
        return widget.findChild(QComboBox)

    def _apply_advanced_filter(self) -> None:
        char_name = (self.filterCharCombo.currentText() or "").strip()
        op = self.filterOpCombo.currentText().strip()
        v1 = (self.filterVal1Edit.text() or "").strip()
        v2 = (self.filterVal2Edit.text() or "").strip() if self.filterVal2Edit.isVisible() else None

        if not char_name:
            QMessageBox.warning(self, "Filtre avancé", "Veuillez sélectionner une caractéristique.")
            return
        if op == "in [a,b]" and (not v1 or not v2):
            QMessageBox.warning(self, "Filtre avancé", "Veuillez renseigner les deux bornes de la plage.")
            return
        try:
            pairs = self.repo.filter_aircrafts_by_characteristic(char_name, op, v1, v2)
        except Exception as exc:
            QMessageBox.warning(self, "Filtre avancé", str(exc))
            return

        self._adv_filter_active = True
        self._adv_filtered = pairs
        self.filterInfoLabel.setVisible(False)
        # Apply simple search on the subset by refreshing the list
        self.refresh_aircrafts()

    def _clear_advanced_filter(self) -> None:
        self.filterOpCombo.setCurrentText("=")
        self.filterVal1Edit.clear()
        self.filterVal2Edit.clear()
        self.filterVal2Edit.setVisible(False)
        self.filterInfoLabel.clear()
        self.filterInfoLabel.setVisible(False)
        self._adv_filter_active = False
        self._adv_filtered = []
        self.refresh_aircrafts()

    def add_aircraft(self):
        dlg = AddAircraftDialog(self)
        if dlg.exec_() == dlg.Accepted:
            try:
                self.repo.create_aircraft(dlg.name, dlg.notes)
                self.refresh_aircrafts()
            except DuplicateNameError:
                QMessageBox.warning(self, "Erreur", "Nom déjà utilisé")

    def rename_aircraft(self):
        if self.current_aircraft_id is None:
            return
        current = self.repo.get_aircraft(self.current_aircraft_id)
        dlg = RenameDialog("Renommer l'avion", "Nom", current.name, self)
        if dlg.exec_() == dlg.Accepted:
            try:
                self.repo.rename_aircraft(self.current_aircraft_id, dlg.text)
                self.refresh_aircrafts()
            except DuplicateNameError:
                QMessageBox.warning(self, "Erreur", "Nom déjà utilisé")

    def edit_notes(self):
        if self.current_aircraft_id is None:
            return
        current = self.repo.get_aircraft(self.current_aircraft_id)
        dlg = EditNotesDialog(current.notes, self)
        if dlg.exec_() == dlg.Accepted:
            self.repo.update_notes(self.current_aircraft_id, dlg.notes)

    def delete_aircraft(self):
        if self.current_aircraft_id is None:
            return
        if (
            QMessageBox.question(
                self,
                "Confirmation",
                "Supprimer cet avion ?",
            )
            == QMessageBox.Yes
        ):
            self.repo.delete_aircraft(self.current_aircraft_id)
            self.current_aircraft_id = None
            self.refresh_aircrafts()
            self.load_values()

    def rename_characteristic(self):
        row = self.char_list.currentRow()
        if row < 0:
            return
        char = self.chars[row]
        dlg = RenameDialog("Renommer la caractéristique", "Nom", char.name, self)
        if dlg.exec_() == dlg.Accepted:
            try:
                self.repo.rename_characteristic(char.id, dlg.text)
                self.refresh_characteristics()
                self.load_values()
            except DuplicateNameError:
                QMessageBox.warning(self, "Erreur", "Nom déjà utilisé")

    def update_char_unit(self):
        row = self.char_list.currentRow()
        if row < 0:
            return
        char = self.chars[row]
        dlg = RenameDialog("Modifier l'unité", "Unité", char.unit or "", self)
        if dlg.exec_() == dlg.Accepted:
            self.repo.update_unit(char.id, dlg.text or None)
            self.refresh_characteristics()
            self.load_values()

    def delete_characteristic(self):
        row = self.char_list.currentRow()
        if row < 0:
            return
        char = self.chars[row]
        if (
            QMessageBox.question(
                self,
                "Confirmation",
                "Supprimer cette caractéristique ?",
            )
            == QMessageBox.Yes
        ):
            self.repo.delete_characteristic(char.id)
            self.refresh_characteristics()
            self.load_values()

    def export_json(self):
        path = export_dir() / "database_export.json"
        self.repo.export_json(path)
        QMessageBox.information(self, "Export", f"Exporté vers {path}")

    def fill_examples(self):
        a1 = self.repo.create_aircraft("Demo 1", None)
        a2 = self.repo.create_aircraft("Demo 2", None)
        c1 = self.repo.create_characteristic("Envergure", "m")
        c2 = self.repo.create_characteristic("Longueur", "m")
        self.repo.set_aircraft_value(a1, c1, "30")
        self.repo.set_aircraft_value(a1, c2, "20")
        self.repo.set_aircraft_value(a2, c1, "28")
        self.refresh_all()

    # Remplacement: import JSON via boite native + QSettings
    def import_json(self):
        """
        Ouvre la boite native Windows pour selectionner un .json,
        importe via le repository et rafraichit l'UI.
        """
        try:
            settings = QSettings("AircraftDesigner", "DatabaseWidget")
            default_dir = settings.value("last_import_dir", os.path.expanduser("~/Documents"))

            options = QFileDialog.Options()  # ne pas utiliser DontUseNativeDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Importer JSON",
                default_dir,
                "Fichiers JSON (*.json);;Tous les fichiers (*.*)",
                options=options,
            )
            if not file_path:
                return

            settings.setValue("last_import_dir", os.path.dirname(file_path))

            # Utiliser le repository existant
            self.repo.import_json(Path(file_path))

            if hasattr(self, "refresh_all"):
                self.refresh_all()

            QMessageBox.information(self, "Import", f"Import effectue depuis :\n{file_path}")
        except json.JSONDecodeError as exc:
            QMessageBox.warning(self, "Erreur", f"Fichier JSON invalide :\n{exc}")
        except Exception as exc:  # pragma: no cover - UI error display
            QMessageBox.warning(self, "Erreur", f"Import echoue :\n{exc}")
