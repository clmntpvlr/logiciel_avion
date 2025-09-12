"""Path utilities for aircraft_designer."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Ensure that *path* exists."""
    path.mkdir(parents=True, exist_ok=True)


def get_project_stats_dir(project_root: Path) -> Path:
    """Return the stats directory for *project_root* and ensure it exists."""
    stats_dir = project_root / "stats"
    ensure_dir(stats_dir)
    return stats_dir
