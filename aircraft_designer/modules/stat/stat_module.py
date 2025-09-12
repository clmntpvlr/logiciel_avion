"""Module registration for the Stat module."""

from __future__ import annotations

from ...core.module_loader import ModuleBase
from ...core.project import Project
from ..database.repository import DatabaseRepository

from .stat_controller import StatController
from .stat_view import StatView


class DatabaseAdapter:
    """Adapter around the database repository to match expected interface."""

    def __init__(self) -> None:
        self.repo = DatabaseRepository()

    def list_aircraft(self) -> list[dict]:
        aircrafts = []
        for a in self.repo.list_aircrafts():
            vals = self.repo.get_values_for_aircraft(a.id)
            characteristics = {}
            for v in vals:
                try:
                    characteristics[v["name"]] = float(v["value"])
                except (TypeError, ValueError):
                    continue
            aircrafts.append(
                {"id": str(a.id), "name": a.name, "characteristics": characteristics}
            )
        return aircrafts

    def list_characteristic_keys(self) -> list[str]:
        return [c.name for c in self.repo.list_characteristics()]

    def get_aircraft_by_ids(self, ids: list[str]) -> list[dict]:
        ids_int = {int(i) for i in ids}
        aircrafts = []
        for a in self.repo.list_aircrafts():
            if a.id in ids_int:
                vals = self.repo.get_values_for_aircraft(a.id)
                characteristics = {}
                for v in vals:
                    try:
                        characteristics[v["name"]] = float(v["value"])
                    except (TypeError, ValueError):
                        continue
                aircrafts.append(
                    {"id": str(a.id), "name": a.name, "characteristics": characteristics}
                )
        return aircrafts


class StatModule(ModuleBase):
    """Entry point for the Stat module."""

    module_name = "Stat"

    def __init__(self, project: Project) -> None:
        super().__init__(project)
        self.db = DatabaseAdapter()

    def get_widget(self):  # noqa: ANN201 - Qt API
        view = StatView()
        controller = StatController(project_root=self.project.path, view=view, db=self.db)
        view.controller = controller
        return view
