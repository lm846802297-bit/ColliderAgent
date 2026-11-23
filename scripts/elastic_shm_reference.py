#!/usr/bin/env python3
"""Standard elastic recoil unit map and synthetic truncated SHM interface check."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass

C_KM_S = 299792.458
KEV_TO_GEV = 1e-6
ETA_ATOL = 2e-11
NORM_ATOL = 2e-9


@dataclass(frozen=True)
class Halo:
    v0: float
    escape: float
    boost: float

    def __post_init__(self):
        if (not all(map(math.isfinite, (self.v0, self.escape, self.boost)))
                or not (self.v0 > 0 and self.escape > 0 and 0 <= self.boost < self.escape)):
            raise ValueError("Require positive finite v0, escape and 0 <= boost < escape")


def elastic_vmin_km_s(recoil_kev: float, target_gev: float, dm_gev: float) -> float:
    if (not all(map(math.isfinite, (recoil_kev, target_gev, dm_gev)))
            or recoil_kev < 0 or target_gev <= 0 or dm_gev <= 0):
        raise ValueError("Require nonnegative recoil and positive finite masses")
    reduced_mass = dm_gev / (1 + dm_gev / target_gev)
    return C_KM_S * math.sqrt(target_gev * KEV_TO_GEV * recoil_kev / 2) / reduced_mass


def _threshold(vmin: float) -> float:
    if not math.isfinite(vmin) or vmin < 0:
        raise ValueError("Require nonnegative finite vmin in km/s")
    return vmin


def _normalization(z: float) -> float:
    return math.erf(z) - 2 * z * math.exp(-z * z) / math.sqrt(math.pi)


def eta_analytic(vmin: float, halo: Halo) -> float:
    vmin = _threshold(vmin)
    v0, escape, boost = halo.v0, halo.escape, halo.boost
    x, y, z = vmin / v0, boost / v0, escape / v0
    if vmin >= escape + boost:
        return 0.0
    norm = _normalization(z)
    edge = math.exp(-z * z) / math.sqrt(math.pi)
    if boost == 0:
        return 2 * (math.exp(-x * x) - math.exp(-z * z)) / (math.sqrt(math.pi) * norm * v0)
    if vmin < escape - boost:
        term = math.erf(x + y) - math.erf(x - y) - 4 * y * edge
    else:
        term = math.erfc(x - y) - math.erfc(z) - 2 * (z + y - x) * edge
    return max(term, 0.0) / (2 * norm * boost)


def _simpson(f, low: float, high: float, n: int) -> float:
    if n <= 0 or n % 2:
        raise ValueError("Simpson requires a positive even panel count")
    if low >= high:
        return 0.0
    step = (high - low) / n
    middle = math.fsum((4 if i % 2 else 2) * f(low + i * step) for i in range(1, n))
    return step * (f(low) + middle + f(high)) / 3


def eta_galactic_shell(vmin: float, halo: Halo, panels: int = 512) -> tuple[float, float]:
    """Return eta and the raw numerical Galactic radial normalization."""
    vmin = _threshold(vmin)
    v0, escape, boost = halo.v0, halo.escape, halo.boost
    weight = lambda u: math.exp(-(u / v0) ** 2)
    norm = _simpson(lambda u: u * u * weight(u), 0, escape, panels)
    if vmin >= escape + boost:
        return 0.0, norm
    if boost == 0:
        return _simpson(lambda u: u * weight(u), vmin, escape, panels) / norm, norm

    def contributes(u: float) -> float:
        # Average 1/w over the allowed Galactic-shell angles. With w the lab
        # speed, d(cos theta)=w*dw/(u*boost); the factor of w cancels 1/w.
        lab_width = max(0.0, u + boost - max(abs(u - boost), vmin))
        return u * weight(u) * lab_width / (2 * boost)

    corners = sorted({0.0, escape, *(v for v in (boost, abs(boost - vmin), boost + vmin)
                                       if 0 < v < escape)})
    integral = math.fsum(_simpson(contributes, a, b, panels)
                         for a, b in zip(corners, corners[1:]))
    return integral / norm, norm


def run_benchmark() -> dict:
    rows = []
    max_norm_residual = 0.0
    for halo in (Halo(220.0, 544.0, 232.0), Halo(220.0, 544.0, 0.0)):
        join, cutoff = halo.escape - halo.boost, halo.escape + halo.boost
        points = sorted({0.0, 100.0, 250.0, join - 1e-3, join, join + 1e-3,
                         (join + cutoff) / 2, cutoff - 1.0, cutoff, cutoff + 1.0})
        for threshold in points:
            closed = eta_analytic(threshold, halo)
            coarse, _ = eta_galactic_shell(threshold, halo, 256)
            fine, radial = eta_galactic_shell(threshold, halo)
            norm_analytic = math.sqrt(math.pi) * halo.v0**3 * _normalization(halo.escape / halo.v0) / 4
            max_norm_residual = max(max_norm_residual, abs(radial / norm_analytic - 1))
            rows.append({"boost_km_s": halo.boost, "vmin_km_s": threshold,
                         "analytic_s_per_km": closed, "galactic_shell_s_per_km": fine,
                         "absolute_residual_s_per_km": abs(closed - fine),
                         "refinement_s_per_km": abs(fine - coarse)})
    correct_vmin = elastic_vmin_km_s(8.0, 122.0, 50.0)
    wrong_vmin = elastic_vmin_km_s(8.0 * 1e6, 122.0, 50.0)
    halo = Halo(220.0, 544.0, 232.0)
    unit_check = eta_analytic(correct_vmin, halo) > 0 and eta_analytic(wrong_vmin, halo) == 0
    worst = max(row["absolute_residual_s_per_km"] for row in rows)
    refinement = max(row["refinement_s_per_km"] for row in rows)
    ok = (worst <= ETA_ATOL and refinement <= ETA_ATOL and max_norm_residual <= NORM_ATOL
          and unit_check and math.isclose(wrong_vmin / correct_vmin, 1000, rel_tol=1e-15))
    return {
        "schema": "collideragent-elastic-shm-reference-v1",
        "scope": "SYNTHETIC_HALO_AND_ELASTIC_KINEMATICS_ONLY",
        "reference_status": "PASS" if ok else "FAIL",
        "native_ddcalc": "NOT_RUN",
        "halo_parameters_km_s": {"v0": 220.0, "escape": 544.0, "boost": [232.0, 0.0]},
        "radial_panels_per_segment": [256, 512],
        "eta_abs_tolerance_s_per_km": ETA_ATOL,
        "normalization_rel_tolerance": NORM_ATOL,
        "max_eta_abs_residual_s_per_km": worst,
        "max_eta_refinement_s_per_km": refinement,
        "max_normalization_relative_residual": max_norm_residual,
        "unit_control": {"recoil_kev": 8.0, "target_gev": 122.0, "dm_gev": 50.0,
                         "correct_vmin_km_s": correct_vmin,
                         "omitted_kev_to_gev_vmin_km_s": wrong_vmin,
                         "wrong_units_remove_support": unit_check},
        "points": rows,
    }


def main() -> int:
    result = run_benchmark()
    print(json.dumps(result, allow_nan=False, indent=2))
    return 0 if result["reference_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
