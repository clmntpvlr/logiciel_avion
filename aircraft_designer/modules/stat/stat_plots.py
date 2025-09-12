"""Plotting utilities for the Stat module."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


def plot_hist(
    df: pd.DataFrame,
    feature: str,
    bins: int = 10,
    log: bool = False,
    fig: plt.Figure | None = None,
) -> plt.Figure:
    """Plot a histogram for *feature*."""
    fig = fig or plt.figure()
    fig.clear()
    ax = fig.add_subplot(111)
    df[feature].plot.hist(ax=ax, bins=bins, log=log)
    ax.set_xlabel(feature)
    ax.set_ylabel("Count")
    ax.set_title(f"Histogram of {feature}")
    return fig


def plot_box(
    df: pd.DataFrame, features: Iterable[str], fig: plt.Figure | None = None
) -> plt.Figure:
    """Plot a boxplot for *features*."""
    fig = fig or plt.figure()
    fig.clear()
    ax = fig.add_subplot(111)
    df[list(features)].plot.box(ax=ax)
    ax.set_title("Boxplot")
    return fig


def plot_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    logx: bool = False,
    logy: bool = False,
    fig: plt.Figure | None = None,
) -> plt.Figure:
    """Plot a scatter plot between *x* and *y*."""
    fig = fig or plt.figure()
    fig.clear()
    ax = fig.add_subplot(111)
    ax.scatter(df[x], df[y])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs {x}")
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    return fig


def save_current_figure(fig: plt.Figure, path: Path) -> None:
    """Save *fig* to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
