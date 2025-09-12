"""Data models for the Stat module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid


@dataclass
class Selection:
    """Aircraft selection definition."""

    selection_id: str
    name: str
    aircraft_ids: List[str] = field(default_factory=list)


@dataclass
class StatsState:
    """Persistent state for the Stat module."""

    selections: Dict[str, Selection] = field(default_factory=dict)
    last_active_selection: Optional[str] = None
    last_analysis: Optional[Dict[str, object]] = None


class SelectionsStore:
    """CRUD operations on in-memory selections."""

    def __init__(self, state: StatsState) -> None:
        self.state = state

    def add(self, name: str, aircraft_ids: Optional[List[str]] = None) -> Selection:
        """Create a new selection and make it active."""
        selection_id = str(uuid.uuid4())
        selection = Selection(
            selection_id=selection_id,
            name=name,
            aircraft_ids=aircraft_ids or [],
        )
        self.state.selections[selection_id] = selection
        self.state.last_active_selection = selection_id
        return selection

    def rename(self, selection_id: str, new_name: str) -> None:
        """Rename an existing selection."""
        if selection_id in self.state.selections:
            self.state.selections[selection_id].name = new_name

    def delete(self, selection_id: str) -> None:
        """Remove a selection."""
        if selection_id in self.state.selections:
            del self.state.selections[selection_id]
            if self.state.last_active_selection == selection_id:
                self.state.last_active_selection = next(
                    iter(self.state.selections), None
                )

    def duplicate(self, selection_id: str) -> Optional[Selection]:
        """Duplicate a selection."""
        original = self.state.selections.get(selection_id)
        if not original:
            return None
        return self.add(f"{original.name} Copy", list(original.aircraft_ids))

    def get(self, selection_id: str) -> Optional[Selection]:
        """Return selection by id."""
        return self.state.selections.get(selection_id)

    def set_active(self, selection_id: str) -> None:
        """Mark a selection as active."""
        if selection_id in self.state.selections:
            self.state.last_active_selection = selection_id

    def active(self) -> Optional[Selection]:
        """Return active selection."""
        if self.state.last_active_selection:
            return self.state.selections.get(self.state.last_active_selection)
        return None
