"""JSON persistence for constraint analysis state."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .io_schemas import STATE_FORMAT_V1


def _state_path(project_id: str) -> Path:
    return Path("projects") / project_id / "constraint_analysis" / "state.json"


def load_state(project_id: str) -> Dict[str, Any]:
    path = _state_path(project_id)
    if not path.is_file():
        return STATE_FORMAT_V1.copy()
    with path.open("r", encoding="utf8") as fh:
        return json.load(fh)


def save_state(project_id: str, state: Dict[str, Any]) -> None:
    path = _state_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.utcnow().isoformat()
    state.setdefault("timestamps", {})
    state["timestamps"]["updated"] = now
    if "created" not in state["timestamps"]:
        state["timestamps"]["created"] = now
    with path.open("w", encoding="utf8") as fh:
        json.dump(state, fh, indent=2)


__all__ = ["load_state", "save_state"]
