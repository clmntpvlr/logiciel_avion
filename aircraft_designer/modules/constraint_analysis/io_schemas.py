"""Schemas and default values for Constraint Analysis module."""
from __future__ import annotations

DEFAULT_INPUTS: dict = {
    "environment": {
        "alt_aerodrome_m": 0,
        "isa_delta_T_C": 0,
        "runway_TOG_m": 1500,
        "runway_LDG_m": 1200,
        "slope_percent": 0,
        "headwind_kts": 0,
    },
    "mass_aero": {
        "W0_kg": None,
        "S_m2": None,
        "AR": 8.5,
        "oswald_e": 0.8,
        "Cd0": 0.025,
        "CLmax_TO": 1.8,
        "CLmax_LDG": 2.2,
    },
    "propulsion": {
        "type": "turboprop",
        "T_max_N": None,
        "P_max_W": 900_000,
        "eta_prop": 0.80,
    },
    "requirements": {
        "BFL_m": 1500,
        "LDG_m": 1200,
        "ROC_init_mps": 6.0,
        "climb_gradient_percent": 0,
        "cruise_alt_ft": 15000,
        "cruise_speed_kts": 240,
        "turn_n": 2.5,
        "ceiling_ft": 25000,
        "roc_at_ceiling_mps": 0.5,
    },
    "assumptions": {
        "V_min_power_mps": 20.0,
    },
}

DEFAULT_SWEEP: dict = {
    "ws_min": 50.0,
    "ws_max": 1200.0,
    "ws_step": 5.0,
    "units": "N/m2",
}

STATE_FORMAT_V1: dict = {
    "inputs": DEFAULT_INPUTS,
    "sweep": DEFAULT_SWEEP,
    "results": {
        "curves": {
            "takeoff": [],
            "climb": [],
            "cruise": [],
            "turn": [],
            "ceiling": [],
        },
        "ws_max_landing": 0.0,
        "envelope": [],
        "recommendation": {"ws": 0.0, "tw": 0.0, "notes": "sans marges"},
    },
    "timestamps": {"created": "", "updated": ""},
    "version": "v1",
}

__all__ = [
    "DEFAULT_INPUTS",
    "DEFAULT_SWEEP",
    "STATE_FORMAT_V1",
]
