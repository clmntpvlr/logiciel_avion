"""Global module registry."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Type

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from PyQt5.QtWidgets import QWidget
else:  # pragma: no cover - fallback dummy
    class QWidget:  # type: ignore
        pass


def get_registered_modules() -> List[Tuple[str, Type['QWidget']]]:
    """Return list of available global modules."""
    from .database import DatabaseWidget  # imported lazily to avoid Qt dependency in tests
    return [(DatabaseWidget.module_name, DatabaseWidget)]
