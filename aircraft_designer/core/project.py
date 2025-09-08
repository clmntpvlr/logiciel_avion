from pathlib import Path

PROJECTS_DIR = Path(__file__).resolve().parent.parent / "projects"


class Project:
    """Représente un projet utilisateur."""

    def __init__(self, name: str):
        self.name = name
        self.path = PROJECTS_DIR / name

    def __repr__(self) -> str:
        return f"Project(name={self.name!r})"
