"""Module Database providing global aircraft data management."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for hints only
    from .database_widget import DatabaseWidget as DatabaseWidget
else:  # pragma: no cover - lazy loader
    class _LazyWidget:
        _cls = None

        def _load(self):  # pragma: no cover - helper
            if self._cls is None:
                from .database_widget import DatabaseWidget as DW  # type: ignore
                self._cls = DW
            return self._cls

        def __call__(self, *args, **kwargs):
            return self._load()(*args, **kwargs)

        def __getattr__(self, item):
            return getattr(self._load(), item)

    DatabaseWidget = _LazyWidget()  # type: ignore

__all__ = ["DatabaseWidget", "register_module"]


def register_module(app):
    """Return widget class for registration."""
    return DatabaseWidget
