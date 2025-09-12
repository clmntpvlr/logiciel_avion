"""Repository layer handling SQLite persistence."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

from .models import Aircraft, Characteristic, AircraftCharacteristic, validate_name
from ...utils.paths import db_path, ensure_dir
from ...utils.logging_setup import get_logger


class DatabaseError(Exception):
    pass


class ValidationError(DatabaseError):
    pass


class DuplicateNameError(DatabaseError):
    pass


class NotFoundError(DatabaseError):
    pass


class DatabaseRepository:
    """SQLite backed repository for aircraft data."""

    def __init__(self, path: str | Path | None = None):
        path = Path(path) if path else db_path()
        ensure_dir(path.parent)
        self.logger = get_logger(__name__)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    # schema
    def _create_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS characteristic (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              unit TEXT
            );
            CREATE TABLE IF NOT EXISTS aircraft (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              notes TEXT
            );
            CREATE TABLE IF NOT EXISTS aircraft_characteristic (
              aircraft_id INTEGER NOT NULL,
              characteristic_id INTEGER NOT NULL,
              value TEXT,
              PRIMARY KEY (aircraft_id, characteristic_id),
              FOREIGN KEY (aircraft_id) REFERENCES aircraft(id) ON DELETE CASCADE,
              FOREIGN KEY (characteristic_id) REFERENCES characteristic(id) ON DELETE CASCADE
            );
            """
        )
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_char_name_ci ON characteristic(lower(name))"
        )
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_aircraft_name_ci ON aircraft(lower(name))"
        )
        self.conn.commit()

    # aircraft CRUD
    def create_aircraft(self, name: str, notes: str | None = None) -> int:
        name = validate_name(name)
        try:
            cur = self.conn.execute(
                "INSERT INTO aircraft(name, notes) VALUES (?, ?)", (name, notes)
            )
            self.conn.commit()
            self.logger.info("Création avion %s", name)
            return cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise DuplicateNameError(str(exc)) from exc

    def rename_aircraft(self, aircraft_id: int, new_name: str) -> None:
        new_name = validate_name(new_name)
        try:
            cur = self.conn.execute(
                "UPDATE aircraft SET name=? WHERE id=?", (new_name, aircraft_id)
            )
            if cur.rowcount == 0:
                raise NotFoundError("Aircraft introuvable")
            self.conn.commit()
            self.logger.info("Renommage avion %s -> %s", aircraft_id, new_name)
        except sqlite3.IntegrityError as exc:
            raise DuplicateNameError(str(exc)) from exc

    def update_notes(self, aircraft_id: int, notes: str | None) -> None:
        cur = self.conn.execute(
            "UPDATE aircraft SET notes=? WHERE id=?", (notes, aircraft_id)
        )
        if cur.rowcount == 0:
            raise NotFoundError("Aircraft introuvable")
        self.conn.commit()
        self.logger.debug("Notes mises à jour pour avion %s", aircraft_id)

    def delete_aircraft(self, aircraft_id: int) -> None:
        self.conn.execute("DELETE FROM aircraft WHERE id=?", (aircraft_id,))
        self.conn.commit()
        self.logger.info("Suppression avion %s", aircraft_id)

    def list_aircrafts(self, filter_text: str | None = None) -> List[Aircraft]:
        sql = "SELECT id, name, notes FROM aircraft"
        params = []
        if filter_text:
            sql += " WHERE lower(name) LIKE ?"
            params.append(f"%{filter_text.lower()}%")
        sql += " ORDER BY name"
        rows = self.conn.execute(sql, params).fetchall()
        return [Aircraft(row["id"], row["name"], row["notes"]) for row in rows]

    def get_aircraft(self, aircraft_id: int) -> Aircraft:
        row = self.conn.execute(
            "SELECT id, name, notes FROM aircraft WHERE id=?", (aircraft_id,)
        ).fetchone()
        if not row:
            raise NotFoundError("Aircraft introuvable")
        return Aircraft(row["id"], row["name"], row["notes"])

    # characteristic CRUD
    def create_characteristic(self, name: str, unit: str | None = None) -> int:
        name = validate_name(name)
        try:
            cur = self.conn.execute(
                "INSERT INTO characteristic(name, unit) VALUES (?, ?)", (name, unit)
            )
            self.conn.commit()
            self.logger.info("Création caractéristique %s", name)
            return cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise DuplicateNameError(str(exc)) from exc

    def rename_characteristic(self, char_id: int, new_name: str) -> None:
        new_name = validate_name(new_name)
        try:
            cur = self.conn.execute(
                "UPDATE characteristic SET name=? WHERE id=?", (new_name, char_id)
            )
            if cur.rowcount == 0:
                raise NotFoundError("Caractéristique introuvable")
            self.conn.commit()
            self.logger.info("Renommage caractéristique %s -> %s", char_id, new_name)
        except sqlite3.IntegrityError as exc:
            raise DuplicateNameError(str(exc)) from exc

    def update_unit(self, char_id: int, unit: str | None) -> None:
        cur = self.conn.execute(
            "UPDATE characteristic SET unit=? WHERE id=?", (unit, char_id)
        )
        if cur.rowcount == 0:
            raise NotFoundError("Caractéristique introuvable")
        self.conn.commit()
        self.logger.debug("Mise à jour unité pour caractéristique %s", char_id)

    def delete_characteristic(self, char_id: int) -> None:
        self.conn.execute("DELETE FROM characteristic WHERE id=?", (char_id,))
        self.conn.commit()
        self.logger.info("Suppression caractéristique %s", char_id)

    def list_characteristics(self, filter_text: str | None = None) -> List[Characteristic]:
        sql = "SELECT id, name, unit FROM characteristic"
        params = []
        if filter_text:
            sql += " WHERE lower(name) LIKE ?"
            params.append(f"%{filter_text.lower()}%")
        sql += " ORDER BY name"
        rows = self.conn.execute(sql, params).fetchall()
        return [Characteristic(row["id"], row["name"], row["unit"]) for row in rows]

    def get_characteristic(self, char_id: int) -> Characteristic:
        row = self.conn.execute(
            "SELECT id, name, unit FROM characteristic WHERE id=?", (char_id,)
        ).fetchone()
        if not row:
            raise NotFoundError("Caractéristique introuvable")
        return Characteristic(row["id"], row["name"], row["unit"])

    # aircraft value management
    def set_aircraft_value(self, aircraft_id: int, char_id: int, value: str) -> None:
        self.conn.execute(
            """
            INSERT INTO aircraft_characteristic(aircraft_id, characteristic_id, value)
            VALUES(?, ?, ?)
            ON CONFLICT(aircraft_id, characteristic_id)
            DO UPDATE SET value=excluded.value
            """,
            (aircraft_id, char_id, value),
        )
        self.conn.commit()
        self.logger.debug("Valeur enregistrée %s/%s", aircraft_id, char_id)

    def remove_aircraft_value(self, aircraft_id: int, char_id: int) -> None:
        self.conn.execute(
            "DELETE FROM aircraft_characteristic WHERE aircraft_id=? AND characteristic_id=?",
            (aircraft_id, char_id),
        )
        self.conn.commit()
        self.logger.debug("Valeur supprimée %s/%s", aircraft_id, char_id)

    def get_values_for_aircraft(self, aircraft_id: int):
        rows = self.conn.execute(
            """
            SELECT ac.characteristic_id, c.name, c.unit, ac.value
            FROM aircraft_characteristic ac
            JOIN characteristic c ON c.id=ac.characteristic_id
            WHERE ac.aircraft_id=?
            ORDER BY c.name
            """,
            (aircraft_id,),
        ).fetchall()
        return [
            {
                "characteristic_id": r["characteristic_id"],
                "name": r["name"],
                "unit": r["unit"],
                "value": r["value"],
            }
            for r in rows
        ]

    # import/export
    def export_json(self, path: str | Path) -> Path:
        path = Path(path)
        ensure_dir(path.parent)
        data = {
            "aircraft": [a.__dict__ for a in self.list_aircrafts()],
            "characteristic": [c.__dict__ for c in self.list_characteristics()],
            "values": [],
        }
        for a in data["aircraft"]:
            vals = self.get_values_for_aircraft(a["id"])
            for v in vals:
                data["values"].append(
                    {
                        "aircraft": a["name"],
                        "characteristic": v["name"],
                        "value": v["value"],
                    }
                )
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path

    def import_json(self, path: str | Path) -> None:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        name_to_aircraft = {a.name.lower(): a for a in self.list_aircrafts()}
        name_to_char = {c.name.lower(): c for c in self.list_characteristics()}
        for a in data.get("aircraft", []):
            name = a.get("name", "")
            if name.lower() not in name_to_aircraft:
                new_id = self.create_aircraft(name, a.get("notes"))
                name_to_aircraft[name.lower()] = self.get_aircraft(new_id)
        for c in data.get("characteristic", []):
            name = c.get("name", "")
            if name.lower() not in name_to_char:
                new_id = self.create_characteristic(name, c.get("unit"))
                name_to_char[name.lower()] = self.get_characteristic(new_id)
            else:
                # update unit if missing
                if c.get("unit") and not name_to_char[name.lower()].unit:
                    self.update_unit(name_to_char[name.lower()].id, c.get("unit"))
        for v in data.get("values", []):
            a = name_to_aircraft.get(v.get("aircraft", "").lower())
            c = name_to_char.get(v.get("characteristic", "").lower())
            if a and c:
                self.set_aircraft_value(a.id, c.id, v.get("value"))

        self.conn.commit()
