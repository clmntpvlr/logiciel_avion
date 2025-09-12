"""Controller connecting the Stat view, data and persistence."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, List

import pandas as pd
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QInputDialog, QListWidgetItem

from ...core import paths
from .stat_io import load_state, save_state
from .stat_models import Selection, SelectionsStore
from .stat_plots import plot_box, plot_hist, plot_scatter, save_current_figure
from .stat_view import StatView


class StatController:
    """Main controller for the Stat module."""

    def __init__(self, project_root: Path, view: StatView, db: Any) -> None:
        self.project_root = project_root
        self.view = view
        self.db = db
        self.state = load_state(project_root)
        self.store = SelectionsStore(self.state)
        if not self.state.selections:
            self.store.add("Default")

        self.aircraft_data = self._load_aircraft()
        self.characteristic_keys = self._load_characteristic_keys()

        self._setup_table()
        self._populate_feature_list()
        self._populate_selection_list()
        self._connect_signals()
        save_state(self.project_root, self.state)

    # ------------------------------------------------------------------ helpers
    def _load_aircraft(self) -> List[dict]:
        try:
            aircraft = self.db.list_aircraft()
            return aircraft or self.demo_fake_aircraft()
        except Exception:
            return self.demo_fake_aircraft()

    def _load_characteristic_keys(self) -> List[str]:
        try:
            keys = self.db.list_characteristic_keys()
            if keys:
                return list(keys)
        except Exception:
            pass
        keys: set[str] = set()
        for a in self.aircraft_data:
            keys.update(a.get("characteristics", {}).keys())
        return sorted(keys)

    def _setup_table(self) -> None:
        self.aircraft_model = QStandardItemModel()
        headers = ["Inclure", "Nom"] + self.characteristic_keys
        self.aircraft_model.setHorizontalHeaderLabels(headers)
        for a in self.aircraft_data:
            row: List[QStandardItem] = []
            include_item = QStandardItem()
            include_item.setCheckable(True)
            include_item.setData(a["id"], Qt.UserRole)
            row.append(include_item)
            row.append(QStandardItem(a["name"]))
            for key in self.characteristic_keys:
                value = a["characteristics"].get(key, "")
                row.append(QStandardItem(str(value)))
            self.aircraft_model.appendRow(row)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.aircraft_model)
        self.proxy_model.setFilterKeyColumn(1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.view.aircraft_table.setModel(self.proxy_model)
        self.view.aircraft_table.resizeColumnsToContents()

    def _populate_feature_list(self) -> None:
        self.view.feature_list.clear()
        for key in self.characteristic_keys:
            item = QListWidgetItem(key)
            item.setData(Qt.UserRole, key)
            self.view.feature_list.addItem(item)

    def _populate_selection_list(self) -> None:
        self.view.selection_list.clear()
        for sid, sel in self.state.selections.items():
            item = QListWidgetItem(sel.name)
            item.setData(Qt.UserRole, sid)
            self.view.selection_list.addItem(item)
            if sid == self.state.last_active_selection:
                self.view.selection_list.setCurrentItem(item)
        if (
            self.view.selection_list.currentItem() is None
            and self.view.selection_list.count()
        ):
            self.view.selection_list.setCurrentRow(0)
        self._update_checkboxes()

    def _connect_signals(self) -> None:
        v = self.view
        v.new_btn.clicked.connect(self.new_selection)
        v.rename_btn.clicked.connect(self.rename_selection)
        v.delete_btn.clicked.connect(self.delete_selection)
        v.duplicate_btn.clicked.connect(self.duplicate_selection)
        v.selection_list.currentItemChanged.connect(self.on_selection_changed)
        v.add_btn.clicked.connect(self.add_to_selection)
        v.generate_btn.clicked.connect(self.generate_analysis)
        v.export_excel_btn.clicked.connect(self.export_excel)
        v.export_png_btn.clicked.connect(self.export_png)
        v.filter_edit.textChanged.connect(self.filter_table)

    # ----------------------------------------------------------------- selections
    def new_selection(self) -> None:
        name, ok = QInputDialog.getText(self.view, "Nouvelle sélection", "Nom :")
        if ok and name:
            self.store.add(name)
            self._populate_selection_list()
            save_state(self.project_root, self.state)

    def rename_selection(self) -> None:
        item = self.view.selection_list.currentItem()
        if not item:
            return
        sid = item.data(Qt.UserRole)
        sel = self.store.get(sid)
        if not sel:
            return
        name, ok = QInputDialog.getText(
            self.view, "Renommer la sélection", "Nom :", text=sel.name
        )
        if ok and name:
            self.store.rename(sid, name)
            item.setText(name)
            save_state(self.project_root, self.state)

    def delete_selection(self) -> None:
        item = self.view.selection_list.currentItem()
        if not item:
            return
        sid = item.data(Qt.UserRole)
        self.store.delete(sid)
        self._populate_selection_list()
        save_state(self.project_root, self.state)

    def duplicate_selection(self) -> None:
        item = self.view.selection_list.currentItem()
        if not item:
            return
        sid = item.data(Qt.UserRole)
        self.store.duplicate(sid)
        self._populate_selection_list()
        save_state(self.project_root, self.state)

    def on_selection_changed(self) -> None:
        item = self.view.selection_list.currentItem()
        if not item:
            return
        sid = item.data(Qt.UserRole)
        self.store.set_active(sid)
        self._update_checkboxes()
        save_state(self.project_root, self.state)

    def _update_checkboxes(self) -> None:
        sel = self.store.active()
        ids = set(sel.aircraft_ids) if sel else set()
        for row in range(self.aircraft_model.rowCount()):
            item = self.aircraft_model.item(row, 0)
            aid = item.data(Qt.UserRole)
            item.setCheckState(Qt.Checked if aid in ids else Qt.Unchecked)

    def _selected_aircraft_ids(self) -> List[str]:
        ids: List[str] = []
        for row in range(self.aircraft_model.rowCount()):
            item = self.aircraft_model.item(row, 0)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids

    def add_to_selection(self) -> None:
        sel = self.store.active()
        if not sel:
            return
        selected_ids = self._selected_aircraft_ids()
        mode = self.view.add_mode_combo.currentText()
        if mode == "Remplacer":
            sel.aircraft_ids = selected_ids
        else:
            for aid in selected_ids:
                if aid not in sel.aircraft_ids:
                    sel.aircraft_ids.append(aid)
        save_state(self.project_root, self.state)
        self._update_checkboxes()

    # --------------------------------------------------------------------- filter
    def filter_table(self, text: str) -> None:
        self.proxy_model.setFilterFixedString(text)

    # --------------------------------------------------------------------- data
    def _get_dataframe_for_selection(self, selection: Selection) -> pd.DataFrame:
        aircraft = [a for a in self.aircraft_data if a["id"] in selection.aircraft_ids]
        rows: List[dict] = []
        for a in aircraft:
            row = {"id": a["id"], "name": a["name"]}
            row.update(a.get("characteristics", {}))
            rows.append(row)
        df = pd.DataFrame(rows)
        return df

    # ------------------------------------------------------------------ analysis
    def generate_analysis(self) -> None:
        sel = self.store.active()
        if not sel:
            return
        df = self._get_dataframe_for_selection(sel)
        if df.empty:
            return
        features = [i.text() for i in self.view.feature_list.selectedItems()]
        if not features:
            return
        analysis = self.view.analysis_combo.currentText()
        fig = self.view.figure
        result_df = pd.DataFrame()

        if analysis == "describe":
            result_df = df[features].describe().transpose()
            fig.clear()
        elif analysis == "hist":
            bins = self.view.bins_spin.value()
            log = self.view.log_check.isChecked()
            plot_hist(df, features[0], bins=bins, log=log, fig=fig)
            result_df = df[features[0]].describe()
        elif analysis == "box":
            plot_box(df, features, fig=fig)
            result_df = df[features].describe().transpose()
        elif analysis == "scatter":
            if len(features) >= 2:
                logx = self.view.logx_check.isChecked()
                logy = self.view.logy_check.isChecked()
                plot_scatter(
                    df, features[0], features[1], logx=logx, logy=logy, fig=fig
                )
                result_df = df[features].describe().transpose()
            else:
                self.view.results_text.setPlainText(
                    "Sélectionnez au moins deux caractéristiques."
                )
                fig.clear()
                self.view.canvas.draw()
                return
        self.view.canvas.draw()
        self.view.results_text.setPlainText(result_df.to_string())

        self.state.last_analysis = {
            "type": analysis,
            "features": features,
            "params": {
                "bins": self.view.bins_spin.value(),
                "log": self.view.log_check.isChecked(),
                "logx": self.view.logx_check.isChecked(),
                "logy": self.view.logy_check.isChecked(),
            },
        }
        save_state(self.project_root, self.state)

    # ------------------------------------------------------------------- exports
    def export_excel(self) -> None:
        sel = self.store.active()
        if not sel:
            return
        df = self._get_dataframe_for_selection(sel)
        if df.empty:
            return
        stats_dir = paths.get_project_stats_dir(self.project_root)
        excel_path = stats_dir / "export.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
            df.describe().to_excel(writer, sheet_name="Describe")
            meta = pd.DataFrame(
                {
                    "timestamp": [datetime.datetime.now().isoformat()],
                    "project": [self.project_root.name],
                    "selection": [sel.name],
                }
            )
            meta.to_excel(writer, sheet_name="Meta", index=False)

    def export_png(self) -> None:
        if not self.state.last_analysis:
            return
        stats_dir = paths.get_project_stats_dir(self.project_root)
        plots_dir = stats_dir / "plots"
        paths.ensure_dir(plots_dir)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_type = self.state.last_analysis.get("type", "plot")
        features = "_".join(self.state.last_analysis.get("features", [])) or "data"
        file_name = f"{ts}_{analysis_type}_{features}.png"
        path = plots_dir / file_name
        save_current_figure(self.view.figure, path)

    # -------------------------------------------------------------------- demo
    @staticmethod
    def demo_fake_aircraft() -> List[dict]:
        """Return a small dataset when the database service is unavailable."""
        return [
            {
                "id": "A01",
                "name": "Falcon",
                "characteristics": {"mass": 5000, "wingspan": 15, "mtow": 8000},
            },
            {
                "id": "A02",
                "name": "Eagle",
                "characteristics": {"mass": 6000, "wingspan": 18, "mtow": 9000},
            },
            {
                "id": "A03",
                "name": "Hawk",
                "characteristics": {"mass": 5500, "wingspan": 16, "mtow": 8500},
            },
        ]
