"""Repository layer handling SQLite persistence."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

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

    # --- helpers (parsing) -----------------------------------------------
    @staticmethod
    def is_float_like(s: str) -> bool:
        """Return True if the string can be parsed as float.

        Accepts comma as decimal separator as a convenience.
        """
        if s is None:
            return False
        if isinstance(s, (int, float)):
            return True
        if not isinstance(s, str):
            return False
        txt = s.strip()
        if not txt:
            return False
        txt = txt.replace(",", ".")
        try:
            float(txt)
            return True
        except Exception:
            return False

    @staticmethod
    def to_float_or_none(s: Optional[str]) -> Optional[float]:
        """Parse string to float or return None if not possible."""
        if s is None:
            return None
        if isinstance(s, (int, float)):
            return float(s)
        if not isinstance(s, str):
            return None
        txt = s.strip().replace(",", ".")
        if not txt:
            return None
        try:
            return float(txt)
        except Exception:
            return None

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

    def filter_aircrafts_by_characteristic(
        self,
        char_name: str,
        operator: str,
        value1: str,
        value2: Optional[str] = None,
    ) -> List[Tuple[int, str]]:
        """
        Retourne [(id, name), ...] pour les avions dont la valeur de la
        caractéristique `char_name` satisfait `operator` parmi
        {"=", "≠", ">", "≥", "<", "≤", "in [a,b]"}.

        Règles:
          - Résoudre la caractéristique par LOWER(name)=LOWER(?)
          - Joindre aircraft_characteristic et aircraft.
          - Opérateurs numériques: parser value1 (et value2 si plage). Si échec -> ValidationError.
            Ignorer les lignes dont la valeur DB n'est pas numérisable.
          - Egalité/inegalité: si les deux côtés sont numérisables -> comparer en float;
            sinon comparer en texte (lower/trim).
          - Exclure les avions sans valeur pour la caractéristique.
        """
        allowed_ops = {"=", "≠", ">", "≥", "<", "≤", "in [a,b]"}
        op = (operator or "").strip()
        if op not in allowed_ops:
            raise ValidationError(f"Opérateur invalide: {operator!r}")
        name_clean = (char_name or "").strip()
        if not name_clean:
            raise ValidationError("La caractéristique est requise")

        # Resolve characteristic id (case-insensitive)
        row = self.conn.execute(
            "SELECT id FROM characteristic WHERE lower(name)=lower(?)",
            (name_clean,),
        ).fetchone()
        if not row:
            # unknown characteristic -> empty result
            return []
        char_id = int(row["id"]) if isinstance(row, sqlite3.Row) else int(row[0])

        # Fetch candidate rows: only aircraft having a value for this characteristic
        rows = self.conn.execute(
            """
            SELECT a.id AS aircraft_id, a.name AS aircraft_name, ac.value AS value
            FROM aircraft_characteristic ac
            JOIN aircraft a ON a.id = ac.aircraft_id
            WHERE ac.characteristic_id = ?
            """,
            (char_id,),
        ).fetchall()

        # Prepare comparison inputs
        results: List[Tuple[int, str]] = []

        # Numeric operators must have numeric inputs
        numeric_ops = {">", "≥", "<", "≤", "in [a,b]"}
        if op in numeric_ops:
            v1 = self.to_float_or_none(value1)
            if v1 is None:
                raise ValidationError("Valeur numérique requise pour l'opérateur choisi")
            v2 = None
            if op == "in [a,b]":
                v2 = self.to_float_or_none(value2)
                if v2 is None:
                    raise ValidationError("Deux valeurs numériques sont requises pour la plage")
                # Ensure min <= max (inclusive interval)
                lo, hi = (v1, v2) if v1 <= v2 else (v2, v1)
            # Evaluate
            for r in rows:
                raw = r["value"] if isinstance(r, sqlite3.Row) else r[2]
                fv = self.to_float_or_none(raw)
                if fv is None:
                    # ignore non-numeric database values for numeric ops
                    continue
                ok = False
                if op == ">":
                    ok = fv > v1
                elif op == "≥":
                    ok = fv >= v1
                elif op == "<":
                    ok = fv < v1
                elif op == "≤":
                    ok = fv <= v1
                elif op == "in [a,b]":
                    ok = (lo <= fv <= hi)
                if ok:
                    aid = int(r["aircraft_id"]) if isinstance(r, sqlite3.Row) else int(r[0])
                    aname = r["aircraft_name"] if isinstance(r, sqlite3.Row) else r[1]
                    results.append((aid, aname))
        else:
            # Equality/Inequality with mixed numeric/text rules
            # Prepare reference values
            ref_num = self.to_float_or_none(value1)
            ref_txt = (value1 or "").strip().lower()
            for r in rows:
                raw = r["value"] if isinstance(r, sqlite3.Row) else r[2]
                if raw is None:
                    continue
                db_num = self.to_float_or_none(raw)
                match: bool
                if ref_num is not None and db_num is not None:
                    # numeric comparison
                    if op == "=":
                        match = (db_num == ref_num)
                    else:  # "≠"
                        match = (db_num != ref_num)
                else:
                    # case-insensitive textual comparison on trimmed value
                    txt = str(raw).strip().lower()
                    if op == "=":
                        match = (txt == ref_txt)
                    else:
                        match = (txt != ref_txt)
                if match:
                    aid = int(r["aircraft_id"]) if isinstance(r, sqlite3.Row) else int(r[0])
                    aname = r["aircraft_name"] if isinstance(r, sqlite3.Row) else r[1]
                    results.append((aid, aname))

        # Sort by aircraft name A->Z and ensure unique ids (join guarantees uniqueness)
        results.sort(key=lambda x: (x[1] or ""))
        return results

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
        """Import data from JSON.

        Supports two formats:
        1) The native export format with keys: aircraft/characteristic/values.
        2) A "single-aircraft" record (e.g. Jane's-like files) with free
           nested fields. In this case, characteristics are created
           automatically using heuristics on field names and units.
        """
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and (
            "aircraft" in data or "characteristic" in data or "values" in data
        ):
            self._import_database_format(data)
        else:
            # Fallback: try to interpret as a single-aircraft record
            self._import_single_aircraft_record(data)

        self.conn.commit()

    # --- helpers ---------------------------------------------------------
    def _import_database_format(self, data: dict) -> None:
        name_to_aircraft = {a.name.lower(): a for a in self.list_aircrafts()}
        name_to_char = {c.name.lower(): c for c in self.list_characteristics()}
        for a in data.get("aircraft", []):
            name = (a.get("name") or "").strip()
            if not name:
                continue
            key = name.lower()
            if key not in name_to_aircraft:
                new_id = self.create_aircraft(name, a.get("notes"))
                name_to_aircraft[key] = self.get_aircraft(new_id)
        for c in data.get("characteristic", []):
            name = (c.get("name") or "").strip()
            if not name:
                continue
            key = name.lower()
            if key not in name_to_char:
                new_id = self.create_characteristic(name, c.get("unit"))
                name_to_char[key] = self.get_characteristic(new_id)
            else:
                # update unit if missing
                if c.get("unit") and not name_to_char[key].unit:
                    self.update_unit(name_to_char[key].id, c.get("unit"))
        for v in data.get("values", []):
            a = name_to_aircraft.get((v.get("aircraft") or "").lower())
            c = name_to_char.get((v.get("characteristic") or "").lower())
            if a and c:
                self.set_aircraft_value(a.id, c.id, v.get("value"))

    def _import_single_aircraft_record(self, data: dict) -> None:
        """Import a single-aircraft JSON by creating characteristics on the fly.

        This flattens nested fields, infers units from suffixes and creates
        human-readable names. Examples: `envergure_m` -> ("Envergure", "m").
        """
        if not isinstance(data, dict):
            raise ValidationError("Format JSON non supporté (objet attendu)")

        # Determine aircraft name
        raw_name = (
            data.get("nom")
            or data.get("name")
            or data.get("modele")
            or data.get("model")
            or data.get("designation")
            or "Avion importé"
        )
        name = str(raw_name).strip() or "Avion importé"

        # Ensure aircraft exists or create it
        existing = {a.name.lower(): a for a in self.list_aircrafts()}
        key = name.lower()
        if key in existing:
            aircraft = existing[key]
        else:
            try:
                a_id = self.create_aircraft(name)
                aircraft = self.get_aircraft(a_id)
            except DuplicateNameError:
                # Append a suffix to create a unique name
                suffix = 1
                candidate = name
                while candidate.lower() in existing:
                    suffix += 1
                    candidate = f"{name} ({suffix})"
                a_id = self.create_aircraft(candidate)
                aircraft = self.get_aircraft(a_id)

        # Prepare characteristics map
        chars = {c.name.lower(): c for c in self.list_characteristics()}

        # Flatten fields and import scalar values
        for flat_key, value in self._flatten_dict(data).items():
            # Skip the primary name fields themselves
            if flat_key in {"nom", "name", "modele", "model", "designation"}:
                continue
            label, unit = self._label_and_unit_from_key(flat_key)
            if label.lower() not in chars:
                new_id = self.create_characteristic(label, unit)
                chars[label.lower()] = self.get_characteristic(new_id)
            else:
                # If our inferred unit is not empty and existing unit missing
                if unit and not chars[label.lower()].unit:
                    self.update_unit(chars[label.lower()].id, unit)

            # Keep only simple scalar values
            if isinstance(value, (int, float)):
                val_str = str(value)
            elif isinstance(value, str):
                val_str = value
            else:
                # ignore lists/dicts/None
                continue

            self.set_aircraft_value(aircraft.id, chars[label.lower()].id, val_str)

    # Small utilities ------------------------------------------------------
    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = ".") -> dict[str, object]:
        items: dict[str, object] = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items

    def _label_and_unit_from_key(self, key: str) -> tuple[str, str | None]:
        """Infer a human label and unit from a flattened key.

        Heuristics: use the last path element, detect unit suffixes like
        _m, _kg, _kmh, _ms, _h, _l. Replace underscores with spaces and
        title-case. Add a small mapping for common fields in French.
        """
        last = key.split(".")[-1]

        # Custom pretty mapping
        pretty_map = {
            "envergure_m": ("Envergure", "m"),
            "longueur_m": ("Longueur", "m"),
            "hauteur_m": ("Hauteur", "m"),
            "surface_ailes_m2": ("Surface ailes", "m²"),
            "max_decollage_kg": ("Masse maximale au décollage", "kg"),
            "a_vide_kg": ("Masse à vide", "kg"),
            "bagages_max_kg": ("Bagages max", "kg"),
            "carburant_max_kg": ("Carburant max", "kg"),
            "capacite_l": ("Capacité carburant", "l"),
            "vitesse_croisiere_kmh": ("Vitesse de croisière", "km/h"),
            "vitesse_max_kmh": ("Vitesse maximale", "km/h"),
            "vitesse_niveau_max_kmh": ("Vitesse niveau max", "km/h"),
            "vitesse_decrochage_kmh": ("Vitesse de décrochage", "km/h"),
            "taux_monte_ms": ("Taux de montée", "m/s"),
            "distance_decollage_m": ("Distance décollage", "m"),
            "distance_decollage_roulage_m": ("Décollage (roulage)", "m"),
            "distance_decollage_obstacle_15m_m": ("Décollage (15 m)", "m"),
            "distance_atterrissage_roulage_m": ("Atterrissage (roulage)", "m"),
            "autonomie_km": ("Autonomie", "km"),
            "endurance_h": ("Endurance", "h"),
            "cockpit_largeur_m": ("Largeur cockpit", "m"),
        }
        if last in pretty_map:
            return pretty_map[last]

        unit = None
        # Suffix-based unit detection
        if last.endswith("_kmh"):
            unit = "km/h"
            base = last[: -len("_kmh")]
        elif last.endswith("_ms"):
            unit = "m/s"
            base = last[: -len("_ms")]
        elif last.endswith("_m2"):
            unit = "m²"
            base = last[: -len("_m2")]
        elif last.endswith("_m"):
            unit = "m"
            base = last[: -len("_m")]
        elif last.endswith("_kg"):
            unit = "kg"
            base = last[: -len("_kg")]
        elif last.endswith("_l"):
            unit = "l"
            base = last[: -len("_l")]
        elif last.endswith("_h"):
            unit = "h"
            base = last[: -len("_h")]
        else:
            base = last

        # Build a readable label
        label = base.replace("_", " ").strip().capitalize()
        return label, unit
