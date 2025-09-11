from PyQt5.QtWidgets import QMainWindow, QTabWidget

from ..core.module_loader import load_modules
from ..modules.cahier_des_charges.widget import CahierDesChargesWidget
from ..modules.technologies.technologies_controller import TechnologiesController


class MainWindow(QMainWindow):
    """Fenêtre principale affichant les modules."""

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle(f"Aircraft Designer - {project.name}")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.modules = []
        for module in load_modules(project):
            widget = module.get_widget()
            if hasattr(widget, "load_from_project"):
                widget.load_from_project(project.path)
            self.tabs.addTab(
                widget,
                getattr(widget, "module_name", module.__class__.__name__),
            )
            self.modules.append(widget)
        tech_controller = TechnologiesController(project.path)
        self.tabs.addTab(tech_controller.widget, tech_controller.widget.module_name)
        self.modules.append(tech_controller.widget)

        cahier_widget = CahierDesChargesWidget()
        cahier_widget.load_from_project(project.path)
        self.tabs.addTab(cahier_widget, cahier_widget.module_name)
        self.modules.append(cahier_widget)
