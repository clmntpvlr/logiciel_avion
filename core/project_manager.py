import json
import os
from typing import Dict, List, Optional


class ProjectManager:
    """Handle creation and loading of projects."""

    def __init__(self, projects_dir: str = "projects") -> None:
        self.projects_dir = projects_dir
        os.makedirs(self.projects_dir, exist_ok=True)
        self.current_project_path: Optional[str] = None
        self.current_project_data: Optional[Dict] = None

    @property
    def current_project_name(self) -> Optional[str]:
        if self.current_project_data:
            return self.current_project_data.get("name")
        return None

    def create_project(self, name: str) -> str:
        """Create a new project folder with a basic configuration file."""
        path = os.path.join(self.projects_dir, name)
        os.makedirs(path, exist_ok=True)
        config_path = os.path.join(path, "project.json")
        if not os.path.exists(config_path):
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({"name": name, "modules": []}, f, indent=4)
        return path

    def open_project(self, path_or_name: str) -> Dict:
        """Open an existing project and load its configuration."""
        path = path_or_name
        if not os.path.isabs(path):
            path = os.path.join(self.projects_dir, path_or_name)
        config_path = os.path.join(path, "project.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No project configuration found in {path}")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.current_project_path = path
        self.current_project_data = data
        return data

    def get_project_modules(self) -> List[str]:
        """Return module names associated with the currently opened project."""
        if self.current_project_data:
            return self.current_project_data.get("modules", [])
        return []

    def list_available_modules(self, modules_dir: str = "modules") -> List[str]:
        """List module names found in the modules directory."""
        if not os.path.exists(modules_dir):
            return []
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(modules_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]

    def save_project(self) -> None:
        """Persist current project configuration to disk."""
        if not (self.current_project_path and self.current_project_data):
            return
        config_path = os.path.join(self.current_project_path, "project.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.current_project_data, f, indent=4)
