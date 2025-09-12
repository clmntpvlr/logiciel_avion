"""Global module registry."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Tuple

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from PyQt5.QtWidgets import QWidget
else:  # pragma: no cover - fallback dummy
    class QWidget:  # type: ignore
        pass


def get_registered_modules() -> List[Tuple[str, Any]]:
    """Return list of available global modules."""
    from .database import DatabaseWidget  # imported lazily to avoid Qt dependency in tests
    from .stat.stat_module import StatModule
    from .conceptual_sketches.conceptual_sketches import (
        ConceptualSketchesModule,
    )

    return [
        (DatabaseWidget.module_name, DatabaseWidget),
        (StatModule.module_name, StatModule),
        (
            ConceptualSketchesModule.module_name,
            ConceptualSketchesModule,
        ),
    ]
