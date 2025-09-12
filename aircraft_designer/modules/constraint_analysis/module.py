"""Wrapper for module loader."""
from __future__ import annotations

from ...core.module_loader import ModuleBase
from ...core.project import Project

from .constraint_analysis_view import ConstraintAnalysisModule as _ConstraintWidget


class ConstraintAnalysisModule(ModuleBase):
    """Entry point for the constraint analysis module."""

    module_name = "Constraint Analysis"

    def __init__(self, project: Project) -> None:
        super().__init__(project)

    def get_widget(self):  # noqa: ANN201 - Qt API
        return _ConstraintWidget(self.project)


__all__ = ["ConstraintAnalysisModule"]
