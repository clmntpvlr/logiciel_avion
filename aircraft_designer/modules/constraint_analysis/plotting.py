"""Plotting utilities for constraint analysis."""
from __future__ import annotations

from typing import Dict, List

from matplotlib.axes import Axes


COLORS = {
    "takeoff": "tab:blue",
    "climb": "tab:orange",
    "cruise": "tab:green",
    "turn": "tab:red",
    "ceiling": "tab:purple",
    "envelope": "black",
}


def plot_curves(ax: Axes, curves: Dict[str, List[List[float]]], ws_max: float) -> None:
    ax.clear()
    for name, data in curves.items():
        xs = [p[0] for p in data]
        ys = [p[1] for p in data]
        ax.plot(xs, ys, label=name.capitalize(), color=COLORS.get(name, "gray"))
    ax.axvline(ws_max, color="gray", linestyle="--", label="LDG max W/S")
    ax.set_xlabel("W/S [N/m²]")
    ax.set_ylabel("T/W")
    ax.legend()


def plot_envelope(ax: Axes, envelope: List[List[float]]) -> None:
    if not envelope:
        return
    xs = [p[0] for p in envelope]
    ys = [p[1] for p in envelope]
    ax.fill_between(xs, ys, [max(ys) * 1.5] * len(xs), color="gray", alpha=0.3)
    ax.plot(xs, ys, color=COLORS["envelope"], linewidth=2, label="Envelope")
