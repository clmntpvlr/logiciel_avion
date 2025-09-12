"""Persistence helpers for the Stat module."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from ...core import paths
from .stat_models import Selection, StatsState


def load_state(project_root: Path) -> StatsState:
    """Load StatsState from stats.json."""
    stats_dir = paths.get_project_stats_dir(project_root)
    stats_file = stats_dir / "stats.json"
    if not stats_file.exists():
        return StatsState()
    data = json.loads(stats_file.read_text(encoding="utf-8"))
    selections_data: Dict[str, dict] = data.get("selections", {})
    selections = {
        sid: Selection(
            selection_id=sid,
            name=sel.get("name", ""),
            aircraft_ids=sel.get("aircraft_ids", []),
        )
        for sid, sel in selections_data.items()
    }
    return StatsState(
        selections=selections,
        last_active_selection=data.get("last_active_selection"),
        last_analysis=data.get("last_analysis"),
    )


def save_state(project_root: Path, state: StatsState) -> None:
    """Save StatsState to stats.json."""
    stats_dir = paths.get_project_stats_dir(project_root)
    stats_file = stats_dir / "stats.json"
    serialised = {
        "selections": {
            sid: {"name": sel.name, "aircraft_ids": sel.aircraft_ids}
            for sid, sel in state.selections.items()
        },
        "last_active_selection": state.last_active_selection,
        "last_analysis": state.last_analysis,
    }
    stats_file.write_text(
        json.dumps(serialised, indent=2, ensure_ascii=False), encoding="utf-8"
    )
