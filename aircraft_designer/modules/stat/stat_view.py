"""Qt widgets for the Stat module."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLineEdit,
    QTableView,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QTextEdit,
    QLabel,
    QListWidgetItem,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class StatView(QWidget):
    """Main widget for the Stat module."""

    module_name = "Stat"

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)

        # Left column: selections
        left = QVBoxLayout()
        self.selection_list = QListWidget()
        left.addWidget(self.selection_list)

        self.new_btn = QPushButton("Nouveau")
        self.rename_btn = QPushButton("Renommer")
        self.delete_btn = QPushButton("Supprimer")
        self.duplicate_btn = QPushButton("Dupliquer")
        left.addWidget(self.new_btn)
        left.addWidget(self.rename_btn)
        left.addWidget(self.delete_btn)
        left.addWidget(self.duplicate_btn)
        layout.addLayout(left)

        # Middle column: aircraft table
        middle = QVBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filtrer par nom…")
        middle.addWidget(self.filter_edit)

        self.aircraft_table = QTableView()
        middle.addWidget(self.aircraft_table)

        add_layout = QHBoxLayout()
        self.add_mode_combo = QComboBox()
        self.add_mode_combo.addItems(["Ajouter", "Remplacer"])
        self.add_btn = QPushButton("Valider sélection")
        add_layout.addWidget(self.add_mode_combo)
        add_layout.addWidget(self.add_btn)
        middle.addLayout(add_layout)
        layout.addLayout(middle)

        # Right column: analysis and plots
        right = QVBoxLayout()

        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QListWidget.MultiSelection)
        right.addWidget(self.feature_list)

        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(["describe", "hist", "box", "scatter"])
        right.addWidget(self.analysis_combo)

        hist_layout = QHBoxLayout()
        hist_layout.addWidget(QLabel("Bins"))
        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(1, 1000)
        self.bins_spin.setValue(10)
        hist_layout.addWidget(self.bins_spin)
        self.log_check = QCheckBox("Log")
        hist_layout.addWidget(self.log_check)
        right.addLayout(hist_layout)

        scatter_layout = QHBoxLayout()
        self.logx_check = QCheckBox("Log X")
        self.logy_check = QCheckBox("Log Y")
        scatter_layout.addWidget(self.logx_check)
        scatter_layout.addWidget(self.logy_check)
        right.addLayout(scatter_layout)

        self.generate_btn = QPushButton("Générer résultats")
        self.export_excel_btn = QPushButton("Exporter Excel")
        self.export_png_btn = QPushButton("Exporter PNG")
        right.addWidget(self.generate_btn)
        right.addWidget(self.export_excel_btn)
        right.addWidget(self.export_png_btn)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        right.addWidget(self.results_text)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        right.addWidget(self.canvas)

        layout.addLayout(right)
        self.setLayout(layout)
