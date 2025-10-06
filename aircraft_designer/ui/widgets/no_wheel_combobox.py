"""QComboBox variant that ignores mouse-wheel when popup is closed.

Rationale:
In editable tables, accidental mouse-wheel scrolling over a closed
QComboBox can unintentionally change the current selection. This widget
prevents such changes by ignoring wheel events unless the popup list is
visible. When the popup is open (via click or Alt+Down), scrolling works
as usual.
"""

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QWheelEvent


class NoWheelComboBox(QComboBox):
    """QComboBox that only reacts to wheel events when open.

    This prevents accidental value changes while navigating the UI.
    """

    def wheelEvent(self, event: QWheelEvent):  # type: ignore[override]
        # Allow the wheel only when the popup is visible; otherwise ignore.
        if self.view().isVisible():
            super().wheelEvent(event)
        else:
            event.ignore()

