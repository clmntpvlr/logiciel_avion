"""Core calculations for constraint analysis without margins."""
from __future__ import annotations

from typing import Dict, List

import numpy as np

from ...utils.atmosphere import (
    ISAProperties,
    ft_to_m,
    isa_properties,
    kts_to_mps,
)


def _landing_ws_max(inputs: Dict) -> float:
    """Compute max W/S from landing distance requirement.

    Uses a simplified Raymer relationship: S_landing ≈ 0.3 * V_ref^2 / g.
    """
    env = inputs["environment"]
    mass = inputs["mass_aero"]
    req = inputs["requirements"]

    props: ISAProperties = isa_properties(env["alt_aerodrome_m"], env["isa_delta_T_C"])
    rho = props.rho
    g = 9.80665
    v_ref = (req["LDG_m"] * g / 0.3) ** 0.5
    ws_max = 0.5 * rho * v_ref**2 * mass["CLmax_LDG"]
    return ws_max


def compute_constraints(inputs: Dict, sweep: Dict) -> Dict:
    """Compute constraint curves and envelope."""
    env = inputs["environment"]
    mass = inputs["mass_aero"]
    prop = inputs["propulsion"]
    req = inputs["requirements"]
    assum = inputs["assumptions"]

    ws_values = np.arange(
        sweep["ws_min"], sweep["ws_max"] + 0.0001, sweep["ws_step"]
    )

    props_sl = isa_properties(env["alt_aerodrome_m"], env["isa_delta_T_C"])
    sigma = props_sl.sigma
    rho_sl = props_sl.rho

    ws_max_landing = _landing_ws_max(inputs)

    k = 1.0 / (np.pi * mass["oswald_e"] * mass["AR"])

    curves: Dict[str, List[List[float]]] = {
        "takeoff": [],
        "climb": [],
        "cruise": [],
        "turn": [],
        "ceiling": [],
    }

    for ws in ws_values:
        # Takeoff (Raymer-like approximation)
        k_bfl = req["BFL_m"] / 37.5
        tw_to = ws / (sigma * mass["CLmax_TO"] * k_bfl)
        curves["takeoff"].append([float(ws), float(tw_to)])

        # Climb requirement
        v = assum["V_min_power_mps"] * 1.2
        q = 0.5 * rho_sl * v**2
        cd = mass["Cd0"] + k * (ws / q) ** 2
        d_w = cd / (ws / q)
        roc = req["ROC_init_mps"]
        if req.get("climb_gradient_percent", 0) > 0:
            roc = max(roc, v * req["climb_gradient_percent"] / 100.0)
        tw_climb = d_w + roc / v
        curves["climb"].append([float(ws), float(tw_climb)])

        # Cruise
        vc = kts_to_mps(req["cruise_speed_kts"])
        rho_c = isa_properties(ft_to_m(req["cruise_alt_ft"])).rho
        q = 0.5 * rho_c * vc**2
        tw_cruise = mass["Cd0"] * q / ws + k * ws / q
        curves["cruise"].append([float(ws), float(tw_cruise)])

        # Turn (sustained)
        n = req["turn_n"]
        vt = vc
        q = 0.5 * rho_sl * vt**2
        cl = n * ws / q
        cd = mass["Cd0"] + k * cl**2
        d_w = cd / cl
        tw_turn = d_w
        curves["turn"].append([float(ws), float(tw_turn)])

        # Ceiling
        vceil = assum["V_min_power_mps"] * 1.2
        rho_ceiling = isa_properties(ft_to_m(req["ceiling_ft"])).rho
        q = 0.5 * rho_ceiling * vceil**2
        cl = ws / q
        cd = mass["Cd0"] + k * cl**2
        d_w = cd / cl
        tw_ceiling = d_w + req["roc_at_ceiling_mps"] / vceil
        curves["ceiling"].append([float(ws), float(tw_ceiling)])

    envelope: List[List[float]] = []
    for i, ws in enumerate(ws_values):
        if ws > ws_max_landing:
            continue
        tw_min = min(curves[name][i][1] for name in curves)
        envelope.append([float(ws), float(tw_min)])

    if envelope:
        rec = min(envelope, key=lambda p: p[1])
        recommendation = {
            "ws": float(rec[0]),
            "tw": float(rec[1]),
            "notes": "sans marges",
        }
    else:
        recommendation = {"ws": 0.0, "tw": 0.0, "notes": "sans marges"}

    return {
        "curves": curves,
        "ws_max_landing": float(ws_max_landing),
        "envelope": envelope,
        "recommendation": recommendation,
    }


__all__ = ["compute_constraints"]
