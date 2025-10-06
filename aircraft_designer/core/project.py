from aircraft_designer.utils.paths import projects_dir

PROJECTS_DIR = projects_dir()


class Project:
    """Represente un projet utilisateur."""

    def __init__(self, name: str):
        self.name = name
        self.path = PROJECTS_DIR / name

    def __repr__(self) -> str:
        return f"Project(name={self.name!r})"
