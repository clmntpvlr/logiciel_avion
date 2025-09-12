"""Main widget for Database module."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt
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
    QToolBar,
    QAction,
    QMessageBox,
    QAbstractItemView,
)

from .repository import DatabaseRepository, DuplicateNameError, NotFoundError
from .dialogs import (
    AddAircraftDialog,
    RenameDialog,
    EditNotesDialog,
    NewCharacteristicDialog,
    ImportJsonDialog,
)
from ...utils.paths import export_dir

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
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Caractéristique", "Valeur", "Unité"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        center_layout.addWidget(self.table)
        table_btns = QHBoxLayout()
        center_layout.addLayout(table_btns)
        self.btn_add_value = QPushButton("➕")
        self.btn_add_value.clicked.connect(self.add_value_row)
        self.btn_del_value = QPushButton("❌")
        self.btn_del_value.clicked.connect(self.remove_value_row)
        table_btns.addWidget(self.btn_add_value)
        table_btns.addWidget(self.btn_del_value)

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
        filter_text = self.aircraft_search.text().strip() or None
        self.aircraft_list.clear()
        self.aircrafts = self.repo.list_aircrafts(filter_text)
        for a in self.aircrafts:
            self.aircraft_list.addItem(a.name)
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

    def _add_value_row(self, char_id: int | None = None, name: str = "", value: str = "", unit: str | None = None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        combo = QComboBox()
        combo_items = [(c.id, c.name) for c in self.repo.list_characteristics()]
        for cid, cname in combo_items:
            combo.addItem(cname, cid)
        combo.addItem("<Nouvelle…>", -1)
        if char_id:
            idx = combo.findData(char_id)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        combo.currentIndexChanged.connect(lambda _: self._combo_changed(combo))
        self.table.setCellWidget(row, 0, combo)
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

    def remove_value_row(self):
        rows = {index.row() for index in self.table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            combo = self.table.cellWidget(row, 0)
            char_id = combo.currentData()
            if self.current_aircraft_id and char_id:
                self.repo.remove_aircraft_value(self.current_aircraft_id, char_id)
            self.table.removeRow(row)

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
                except DuplicateNameError:
                    QMessageBox.warning(self, "Erreur", "Nom déjà utilisé")
        else:
            row = self.table.indexAt(combo.pos()).row()
            unit = self.repo.get_characteristic(char_id).unit
            self.table.item(row, 2).setText(unit or "")
            value_widget = self.table.cellWidget(row, 1)
            self._value_changed(value_widget, combo)

    def _value_changed(self, line: QLineEdit, combo: QComboBox):
        if not self.current_aircraft_id:
            return
        char_id = combo.currentData()
        if char_id and line.text().strip():
            self.repo.set_aircraft_value(self.current_aircraft_id, char_id, line.text())

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

    def import_json(self):
        dlg = ImportJsonDialog(self)
        if dlg.exec_() == dlg.Accepted:
            try:
                self.repo.import_json(dlg.path)
                self.refresh_all()
            except Exception as exc:  # pragma: no cover - UI error display
                QMessageBox.warning(self, "Erreur", str(exc))

    def fill_examples(self):
        a1 = self.repo.create_aircraft("Demo 1", None)
        a2 = self.repo.create_aircraft("Demo 2", None)
        c1 = self.repo.create_characteristic("Envergure", "m")
        c2 = self.repo.create_characteristic("Longueur", "m")
        self.repo.set_aircraft_value(a1, c1, "30")
        self.repo.set_aircraft_value(a1, c2, "20")
        self.repo.set_aircraft_value(a2, c1, "28")
        self.refresh_all()
