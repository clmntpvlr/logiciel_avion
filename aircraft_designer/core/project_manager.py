from typing import List

from .project import Project, PROJECTS_DIR


def list_projects() -> List[str]:
    """Retourne la liste des noms de projets existants."""
    if not PROJECTS_DIR.exists():
        return []
    return [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()]


def create_project(name: str) -> Project:
    """Crée un projet et retourne son instance."""
    path = PROJECTS_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return Project(name)


def load_project(name: str) -> Project:
    """Charge un projet existant."""
    path = PROJECTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Le projet '{name}' n'existe pas")
    return Project(name)
