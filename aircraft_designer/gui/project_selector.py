from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from ..core import project_manager


class ProjectSelector(QDialog):
    """Fenêtre de création ou sélection d'un projet."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélection du projet")
        self.selected_project = None

        self.list_widget = QListWidget()
        self.list_widget.addItems(project_manager.list_projects())

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du nouveau projet")

        open_btn = QPushButton("Ouvrir")
        create_btn = QPushButton("Créer")

        open_btn.clicked.connect(self.open_project)
        create_btn.clicked.connect(self.create_project)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.name_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(create_btn)
        layout.addLayout(btn_layout)

    def open_project(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un projet existant.")
            return
        self.selected_project = project_manager.load_project(item.text())
        self.accept()

    def create_project(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Erreur", "Entrez un nom de projet.")
            return
        self.selected_project = project_manager.create_project(name)
        self.accept()
