"""Simple ISA atmosphere utilities and unit conversions."""
from __future__ import annotations

from dataclasses import dataclass
import math

# Constants
G0 = 9.80665  # m/s^2
R = 287.05287  # J/(kg*K)
T0 = 288.15  # K
P0 = 101325.0  # Pa
RHO0 = 1.225  # kg/m3
LAPSERATE = -0.0065  # K/m (up to 11 km)


@dataclass
class ISAProperties:
    T: float
    p: float
    rho: float
    a: float
    sigma: float


def isa_properties(alt_m: float, isa_delta_T_C: float = 0.0) -> ISAProperties:
    """Return ISA properties at given altitude."""
    T = T0 + LAPSERATE * alt_m + isa_delta_T_C
    if alt_m < 11000:
        p = P0 * (T / T0) ** (-G0 / (LAPSERATE * R))
    else:
        p = P0 * math.exp(-G0 * (alt_m - 11000) / (R * T)) * (
            T / T0
        ) ** (-G0 / (LAPSERATE * R))
    rho = p / (R * T)
    a = math.sqrt(1.4 * R * T)
    sigma = rho / RHO0
    return ISAProperties(T=T, p=p, rho=rho, a=a, sigma=sigma)


# Conversion helpers

def kts_to_mps(kts: float) -> float:
    return kts * 0.514444


def mps_to_kts(mps: float) -> float:
    return mps / 0.514444


def ft_to_m(ft: float) -> float:
    return ft * 0.3048


def m_to_ft(m: float) -> float:
    return m / 0.3048


def kg_to_newton(kg: float) -> float:
    return kg * G0


def newton_to_kg(N: float) -> float:
    return N / G0

__all__ = [
    "isa_properties",
    "kts_to_mps",
    "mps_to_kts",
    "ft_to_m",
    "m_to_ft",
    "kg_to_newton",
    "newton_to_kg",
    "ISAProperties",
]
