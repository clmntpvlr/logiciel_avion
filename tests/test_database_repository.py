import json
from pathlib import Path
import sys
import pathlib

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from aircraft_designer.modules.database.repository import (
    DatabaseRepository,
    DuplicateNameError,
    ValidationError,
)


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


def test_filter_aircrafts_by_characteristic(tmp_path: Path):
    repo = DatabaseRepository(tmp_path / "db.sqlite")
    # Setup characteristic and aircraft with values
    c_id = repo.create_characteristic("Masse à vide (kg)", "kg")
    a_id = repo.create_aircraft("A", None)
    b_id = repo.create_aircraft("B", None)
    c2_id = repo.create_aircraft("C", None)
    d_id = repo.create_aircraft("D", None)
    repo.set_aircraft_value(a_id, c_id, "430")
    repo.set_aircraft_value(b_id, c_id, "450")
    repo.set_aircraft_value(c2_id, c_id, "N/A")
    repo.set_aircraft_value(d_id, c_id, "445")

    # = "430" -> [A]
    res = repo.filter_aircrafts_by_characteristic("Masse à vide (kg)", "=", "430")
    assert [name for (_id, name) in res] == ["A"]

    # > "440" -> [B, D] sorted by name
    res = repo.filter_aircrafts_by_characteristic("Masse à vide (kg)", ">", "440")
    assert [name for (_id, name) in res] == ["B", "D"]

    # in [440,455] -> [B, D]
    res = repo.filter_aircrafts_by_characteristic("Masse à vide (kg)", "in [a,b]", "440", "455")
    assert [name for (_id, name) in res] == ["B", "D"]

    # ≤ "430" -> [A]
    res = repo.filter_aircrafts_by_characteristic("Masse à vide (kg)", "≤", "430")
    assert [name for (_id, name) in res] == ["A"]

    # = "n/a" (text, case-insensitive) -> [C]
    res = repo.filter_aircrafts_by_characteristic("Masse à vide (kg)", "=", "n/a")
    assert [name for (_id, name) in res] == ["C"]

    # > "abc" -> ValidationError
    with pytest.raises(ValidationError):
        repo.filter_aircrafts_by_characteristic("Masse à vide (kg)", ">", "abc")

    # Unknown characteristic -> empty list
    res = repo.filter_aircrafts_by_characteristic("Carac inconnue", "=", "0")
    assert res == []
