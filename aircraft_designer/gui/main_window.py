from PyQt5.QtWidgets import QMainWindow, QTabWidget

from ..core.module_loader import load_modules


class MainWindow(QMainWindow):
    """Fenêtre principale affichant les modules."""

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle(f"Aircraft Designer - {project.name}")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.modules = load_modules(project)
        for module in self.modules:
            widget = module.get_widget()
            self.tabs.addTab(widget, module.__class__.__name__)
