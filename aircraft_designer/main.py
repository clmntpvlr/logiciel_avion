import sys
from PyQt5.QtWidgets import QApplication, QDialog

from .gui.project_selector import ProjectSelector
from .gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    selector = ProjectSelector()
    if selector.exec_() == QDialog.Accepted and selector.selected_project:
        window = MainWindow(selector.selected_project)
        window.show()
        app.exec_()


if __name__ == "__main__":
    main()
