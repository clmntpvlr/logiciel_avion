import importlib
import inspect
from pathlib import Path
from typing import List, Type

from .project import Project

MODULES_DIR = Path(__file__).resolve().parent.parent / "modules"


class ModuleBase:
    """Classe de base pour tous les modules."""

    def __init__(self, project: Project):
        self.project = project

    def get_widget(self):
        """Retourne le widget principal du module."""
        raise NotImplementedError


def load_modules(project: Project) -> List[ModuleBase]:
    """Charge dynamiquement les modules disponibles."""
    modules: List[ModuleBase] = []
    if not MODULES_DIR.exists():
        return modules

    for path in MODULES_DIR.iterdir():
        module_file = path / "module.py"
        if not module_file.is_file():
            continue
        module_name = f"aircraft_designer.modules.{path.name}.module"
        mod = importlib.import_module(module_name)
        cls = _find_module_class(mod)
        if cls:
            modules.append(cls(project))
    return modules


def _find_module_class(module) -> Type[ModuleBase] | None:
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, ModuleBase) and obj is not ModuleBase:
            return obj
    return None
