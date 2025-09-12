"""PyQt5 interface for Constraint Analysis module."""
from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from .constraint_core import compute_constraints
from .io_schemas import DEFAULT_INPUTS, DEFAULT_SWEEP
from .plotting import plot_curves, plot_envelope


class ConstraintAnalysisModule(QWidget):
    """Minimal UI placeholder for the constraint analysis."""

    def __init__(self, project) -> None:  # noqa: ANN001 - Qt API
        super().__init__()
        self.project = project
        self.inputs = DEFAULT_INPUTS
        self.sweep = DEFAULT_SWEEP
        self.results: Optional[dict] = None

        self.tabs = QTabWidget()
        self.tab_inputs = QWidget()
        self.tab_plot = QWidget()
        self.tabs.addTab(self.tab_inputs, "Entrées")
        self.tabs.addTab(self.tab_plot, "Contraintes")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

        self._setup_inputs_tab()
        self._setup_plot_tab()

    def _setup_inputs_tab(self) -> None:
        layout = QVBoxLayout(self.tab_inputs)
        layout.addWidget(QLabel("Interface des entrées (stub)"))

    def _setup_plot_tab(self) -> None:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.tab_plot)
        layout.addWidget(self.canvas)

    def calculate(self) -> None:
        self.results = compute_constraints(self.inputs, self.sweep)
        ax = self.figure.gca()
        plot_curves(ax, self.results["curves"], self.results["ws_max_landing"])
        plot_envelope(ax, self.results["envelope"])
        self.canvas.draw_idle()
