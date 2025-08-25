import importlib
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from core.project_manager import ProjectManager

MODULES_DIR = "modules"


class MainWindow(QMainWindow):
    """Main window managing project lifecycle and module loading."""

    def __init__(self) -> None:
        super().__init__()
        self.project_manager = ProjectManager()
        self.module_tabs = QTabWidget()
        self.setCentralWidget(self.module_tabs)
        self._create_actions()
        self._create_menus()
        self.setWindowTitle("Modular PyQt5 Application")

    # Menu and action setup -------------------------------------------------
    def _create_actions(self) -> None:
        self.new_project_act = QAction("New Project", self)
        self.new_project_act.triggered.connect(self.create_project)
        self.open_project_act = QAction("Open Project", self)
        self.open_project_act.triggered.connect(self.open_project)

    def _create_menus(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.new_project_act)
        file_menu.addAction(self.open_project_act)

    # Project handling ------------------------------------------------------
    def create_project(self) -> None:
        name, ok = QInputDialog.getText(self, "Create Project", "Project name:")
        if ok and name:
            path = self.project_manager.create_project(name)
            self._load_project(path)

    def open_project(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Open Project", self.project_manager.projects_dir
        )
        if path:
            self._load_project(path)

    def _load_project(self, path: str) -> None:
        try:
            self.project_manager.open_project(path)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Error", str(exc))
            return
        self.setWindowTitle(
            f"Modular PyQt5 Application - {self.project_manager.current_project_name}"
        )
        self._load_modules()

    # Module loading --------------------------------------------------------
    def _load_modules(self) -> None:
        self.module_tabs.clear()
        for module_name in self.project_manager.get_project_modules():
            widget = self._import_module_widget(module_name)
            if widget:
                self.module_tabs.addTab(widget, module_name)

    def _import_module_widget(self, module_name: str):
        try:
            module = importlib.import_module(f"{MODULES_DIR}.{module_name}")
        except Exception as exc:  # pragma: no cover - debug information
            print(f"Failed to import module {module_name}: {exc}")
            return None
        if hasattr(module, "ModuleWidget"):
            return module.ModuleWidget()
        return None
