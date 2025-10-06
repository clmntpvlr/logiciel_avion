# aircraft_designer/main.py
import sys
from PyQt5.QtWidgets import QApplication, QDialog

# ⚠️ IMPORTS ABSOLUS (plus de "from .gui ...")
from aircraft_designer.gui.project_selector import ProjectSelector
from aircraft_designer.gui.main_window import MainWindow


def main():
    """
    Point d'entrée unique de l'application.
    1) Ouvre le sélecteur de projet
    2) Si un projet est choisi, lance MainWindow(project)
    """
    app = QApplication(sys.argv)

    selector = ProjectSelector()
    if selector.exec_() == QDialog.Accepted and getattr(selector, "selected_project", None):
        window = MainWindow(selector.selected_project)  # <-- on passe bien 'project'
        window.show()
        sys.exit(app.exec_())
    else:
        # Rien sélectionné → on ferme proprement
        sys.exit(0)


if __name__ == "__main__":
    main()
