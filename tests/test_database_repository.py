import json
from pathlib import Path
import sys
import pathlib

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from aircraft_designer.modules.database.repository import DatabaseRepository, DuplicateNameError


def test_crud_and_values(tmp_path: Path):
    repo = DatabaseRepository(tmp_path / "db.sqlite")
    a1 = repo.create_aircraft("Avion A", None)
    c1 = repo.create_characteristic("Masse", "kg")
    repo.set_aircraft_value(a1, c1, "100")
    vals = repo.get_values_for_aircraft(a1)
    assert vals[0]["value"] == "100"
    repo.rename_aircraft(a1, "Avion B")
    assert repo.get_aircraft(a1).name == "Avion B"
    with pytest.raises(DuplicateNameError):
        repo.create_aircraft("Avion B")
    repo.delete_characteristic(c1)
    assert repo.get_values_for_aircraft(a1) == []


def test_export_import(tmp_path: Path):
    repo = DatabaseRepository(tmp_path / "db.sqlite")
    a = repo.create_aircraft("Test", None)
    c = repo.create_characteristic("Longueur", "m")
    repo.set_aircraft_value(a, c, "20")
    export_file = tmp_path / "export.json"
    repo.export_json(export_file)
    repo2 = DatabaseRepository(tmp_path / "db2.sqlite")
    repo2.import_json(export_file)
    aircrafts = repo2.list_aircrafts()
    assert len(aircrafts) == 1
    assert repo2.get_values_for_aircraft(aircrafts[0].id)[0]["value"] == "20"
