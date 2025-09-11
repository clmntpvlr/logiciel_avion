"""Test rapide de sauvegarde/chargement du cahier des charges."""

from pathlib import Path
import shutil
import sys

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from aircraft_designer.modules.cahier_des_charges.model import (
    CahierDesChargesModel,
)
from aircraft_designer.modules.cahier_des_charges.storage import (
    load_cahier_des_charges,
    save_cahier_des_charges,
)


def main() -> None:
    project_dir = Path(__file__).resolve().parent / "__test_project__"
    project_dir.mkdir(exist_ok=True)
    model = CahierDesChargesModel()
    model.classique.mission = "Test"
    save_cahier_des_charges(project_dir, model)
    loaded = load_cahier_des_charges(project_dir)
    assert loaded.classique.mission == "Test"
    print("Smoke test OK")
    shutil.rmtree(project_dir)


if __name__ == "__main__":
    main()
