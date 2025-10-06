"""Simple dataclasses for database module."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Aircraft:
    id: int
    name: str
    notes: str | None = None


@dataclass
class Characteristic:
    id: int
    name: str
    unit: str | None = None


@dataclass
class AircraftCharacteristic:
    aircraft_id: int
    characteristic_id: int
    value: str | None = None


def validate_name(name: str) -> str:
    """Strip and validate non empty name."""
    cleaned = (name or "").strip()
    if not cleaned:
        raise ValueError("Le nom ne peut pas être vide")
    return cleaned
