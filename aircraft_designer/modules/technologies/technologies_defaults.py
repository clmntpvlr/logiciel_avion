"""Valeurs par défaut pour le module Technologies."""

from __future__ import annotations

from uuid import uuid4
from typing import Dict, List


def _category(name: str, options: List[str]) -> Dict:
    return {
        "id": str(uuid4()),
        "name": name,
        "options": [{"id": str(uuid4()), "label": opt} for opt in options],
        "selected_option_ids": [],
        "justification": "",
    }


def get_default_payload() -> Dict:
    """Retourne la structure par défaut du module."""
    return {
        "version": 1,
        "categories": [
            _category(
                "Matériaux",
                [
                    "Aluminium",
                    "Composites (CFRP/GFRP)",
                    "Titane",
                    "Acier",
                    "Hybrides métal/composite",
                    "Bois technique",
                ],
            ),
            _category(
                "Procédés",
                [
                    "Usinage",
                    "Formage",
                    "Assemblage riveté",
                    "Collage structural",
                    "Soudage",
                    "Impression 3D métal",
                    "Impression 3D polymère",
                    "Drapage prepreg",
                    "RTM/infusion",
                ],
            ),
            _category(
                "Propulsion/Énergie",
                [
                    "Turboréacteurs",
                    "Turbopropulseurs",
                    "Pistons",
                    "Électrique batterie",
                    "Hybride-électrique",
                    "Hydrogène (pile/combustion)",
                ],
            ),
            _category(
                "Avionique",
                [
                    "FBW (fly-by-wire)",
                    "EFIS",
                    "FMS",
                    "Autopilot cat. A/B",
                    "Datalink",
                    "Health Monitoring",
                ],
            ),
        ],
    }
