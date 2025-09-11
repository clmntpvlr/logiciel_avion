"""Structures de données pour le module Cahier des charges."""

from dataclasses import dataclass, field, asdict
from typing import Dict


@dataclass
class CahierClassique:
    """Section classique du cahier des charges."""

    mission: str = ""
    performances: str = ""
    handling: str = ""
    manufacturing: str = ""
    certifiability: str = ""
    upgradability: str = ""
    maintainability: str = ""
    accessibility: str = ""
    aesthetic: str = ""
    client: str = ""


@dataclass
class CahierConcept:
    """Section nouveau concept du cahier des charges."""

    inspiration: str = ""
    public_cible: str = ""
    innovations: str = ""
    contraintes: str = ""
    fonctionnalites_cles: str = ""
    croquis_ou_notes: str = ""


@dataclass
class CahierDesChargesModel:
    """Modèle principal du cahier des charges."""

    version: str = "1.0"
    last_modified_utc: str = ""
    mode: str = "classique"
    classique: CahierClassique = field(default_factory=CahierClassique)
    concept: CahierConcept = field(default_factory=CahierConcept)

    def to_dict(self) -> Dict[str, Dict[str, str] | str]:
        """Convertit le modèle en dictionnaire."""
        return {
            "version": self.version,
            "last_modified_utc": self.last_modified_utc,
            "mode": self.mode,
            "classique": asdict(self.classique),
            "concept": asdict(self.concept),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, str] | str]) -> "CahierDesChargesModel":
        """Crée une instance à partir d'un dictionnaire."""
        classique = CahierClassique(**data.get("classique", {}))
        concept = CahierConcept(**data.get("concept", {}))
        return cls(
            version=data.get("version", "1.0"),
            last_modified_utc=data.get("last_modified_utc", ""),
            mode=data.get("mode", "classique"),
            classique=classique,
            concept=concept,
        )
