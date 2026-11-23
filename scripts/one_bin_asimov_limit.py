#!/usr/bin/env python3
"""Synthetic one-bin asymptotic CLs reference and opt-in pyhf parity check."""
from __future__ import annotations

import argparse
import json
import math
from importlib import metadata

BACKGROUND, SIGNAL = 100.0, 20.0
LEVEL = 0.05
REFERENCE_UPPER = 10.0
NATIVE_LOWER = 0.05  # Positive to avoid the degenerate q_mu,A = 0 endpoint.
POINTS = (0.25, 0.50, 1.0, 1.5, 2.0)
PYHF_VERSION = "0.7.6"
CLS_ATOL = 5e-7
LIMIT_ATOL = 5e-6


def workspace_spec() -> dict:
    return {
        "version": "1.0.0",
        "channels": [{"name": "count", "samples": [
            {"name": "signal", "data": [SIGNAL],
             "modifiers": [{"name": "mu", "type": "normfactor", "data": None}]},
            {"name": "background", "data": [BACKGROUND], "modifiers": []},
        ]}],
        "observations": [{"name": "count", "data": [BACKGROUND]}],
        "measurements": [{"name": "expected", "config": {
            "poi": "mu", "parameters": [{"name": "mu", "inits": [1.0],
                                         "bounds": [[0.0, REFERENCE_UPPER]]}],
        }}],
    }


def q_mu(mu: float, background: float, signal: float) -> float:
    if (not all(math.isfinite(x) for x in (mu, background, signal))
            or mu < 0.0 or background <= 0.0 or signal <= 0.0):
        raise ValueError("Require finite mu >= 0, background > 0 and signal > 0")
    x = mu * signal / background
    if not math.isfinite(x):
        raise ValueError("Signal to background ratio overflow")
    # x-log(1+x) suffers relative cancellation at very small x.
    delta = (x * x * (1 / 2 + x * (-1 / 3 + x * (1 / 4 + x * (-1 / 5 + x / 6))))
             if x < 1e-4 else x - math.log1p(x))
    value = 2 * (background * delta)
    if not math.isfinite(value):
        raise ValueError("Likelihood-ratio overflow")
    return value


def cls(mu: float, background: float, signal: float) -> float:
    return math.erfc(math.sqrt(q_mu(mu, background, signal) / 2))


def bisect_limit(background: float, signal: float, level: float,
                 upper: float) -> tuple[float, float]:
    if not 0.0 < level < 1.0 or cls(upper, background, signal) >= level:
        raise ValueError("The finite interval [0, upper] must strictly bracket CLs = level")
    low = 0.0
    for _ in range(128):
        middle = low + (upper - low) / 2
        if middle in (low, upper) or upper - low <= 1e-12:
            return low, upper
        if cls(middle, background, signal) > level:
            low = middle
        else:
            upper = middle
    raise RuntimeError("Reference bisection did not converge")


def reference() -> dict:
    li, hi = bisect_limit(BACKGROUND, SIGNAL, LEVEL, REFERENCE_UPPER)
    mu = (li + hi) / 2
    return {
        "status": "COMPUTED_STDLIB_REFERENCE",
        "mu95": mu,
        "bracket": [{"mu": a, "cls": cls(a, BACKGROUND, SIGNAL)} for a in (li, hi)],
        "cls_at_mu95": cls(mu, BACKGROUND, SIGNAL),
        "points": [{"mu": a, "q_mu": q_mu(a, BACKGROUND, SIGNAL),
                    "cls": cls(a, BACKGROUND, SIGNAL)} for a in POINTS],
    }


def compare_native(independent: dict, point_pairs: list[tuple[float, float]],
                   limits: tuple[float, float]) -> dict:
    values = [x for pair in point_pairs for x in pair]
    if (len(point_pairs) != len(independent["points"]) or len(limits) != 2
            or any(len(pair) != 2 for pair in point_pairs)
            or any(not math.isfinite(x) or not 0 <= x <= 1 for x in values)
            or any(not math.isfinite(x) or not 0 < x <= REFERENCE_UPPER for x in limits)):
        return {"status": "FAIL", "reason": "INVALID_NATIVE_OUTPUT"}
    c_res = max(abs(value - row["cls"])
                for pair, row in zip(point_pairs, independent["points"]) for value in pair)
    m_res = max(abs(value - independent["mu95"]) for value in limits)
    return {
        "status": "PASS" if c_res <= CLS_ATOL and m_res <= LIMIT_ATOL else "FAIL",
        "mu95_asimov_observation": limits[0],
        "mu95_median_expected": limits[1],
        "max_cls_abs_residual": c_res,
        "max_mu95_abs_residual": m_res,
        "points": [{"mu": a, "cls_asimov_observation": x, "cls_median_expected": y}
                   for a, (x, y) in zip(POINTS, point_pairs)],
    }


def native_replay(independent: dict) -> dict:
    try:
        installed = metadata.version("pyhf")
    except metadata.PackageNotFoundError:
        return {"status": "NOT_RUN", "reason": "PYHF_NOT_INSTALLED"}
    if installed != PYHF_VERSION:
        return {"status": "NOT_RUN", "reason": "PYHF_VERSION_NOT_PINNED",
                "detected_pyhf_version": installed}

    try:
        import pyhf
        from pyhf.infer.intervals.upper_limits import toms748_scan

        if pyhf.__version__ != PYHF_VERSION:
            return {"status": "NOT_RUN", "reason": "IMPORTED_VERSION_MISMATCH"}
        pyhf.set_backend("numpy", precision="64b")
        workspace = pyhf.Workspace(workspace_spec())
        model = workspace.model(measurement_name="expected")
        data = workspace.data(model)
        if list(model.config.par_order) != ["mu"] or model.config.auxdata or data != [BACKGROUND]:
            return {"status": "FAIL", "reason": "NOT_THE_NO_NUISANCE_ASIMOV_FIXTURE"}
        kwargs = {"calctype": "asymptotics", "test_stat": "qtilde"}

        def values_at(mu: float) -> tuple[float, list[float]]:
            obs, exp = pyhf.infer.hypotest(mu, data, model, return_expected_set=True, **kwargs)
            return float(obs), [float(x) for x in exp]

        low_obs, low_exp = values_at(NATIVE_LOWER)
        high_obs, high_exp = values_at(REFERENCE_UPPER)
        if not (len(low_exp) == len(high_exp) == 5
                and all(math.isfinite(x) and LEVEL < x <= 1 for x in [low_obs] + low_exp)
                and all(math.isfinite(x) and 0 <= x < LEVEL for x in [high_obs] + high_exp)):
            return {"status": "FAIL", "reason": "NATIVE_SCAN_NOT_BRACKETED"}
        point_pairs = [(obs, exp[2]) for obs, exp in map(values_at, POINTS)]
        observed, expected = toms748_scan(
            data, model, NATIVE_LOWER, REFERENCE_UPPER, level=LEVEL,
            atol=2e-12, rtol=1e-8, **kwargs,
        )
        out = compare_native(independent, point_pairs, (float(observed), float(expected[2])))
        out.update(pyhf_version=installed, backend="numpy-64b", test_stat="qtilde",
                   calculator="asymptotics", poi_bounds=[0.0, REFERENCE_UPPER],
                   scan_bounds=[NATIVE_LOWER, REFERENCE_UPPER],
                   cls_abs_tolerance=CLS_ATOL, mu95_abs_tolerance=LIMIT_ATOL)
        return out
    except Exception as exc:
        return {"status": "FAIL", "reason": "NATIVE_REPLAY_ERROR",
                "error_type": type(exc).__name__}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true",
                        help="Run only in an approved environment with exact pyhf already installed.")
    args = parser.parse_args(argv)
    independent = reference()
    native = (native_replay(independent) if args.native
              else {"status": "NOT_RUN", "reason": "NATIVE_NOT_REQUESTED"})
    print(json.dumps({
        "schema": "collideragent-one-bin-asimov-limit-v1",
        "scope": "SYNTHETIC_BACKEND_PARITY_NOT_AN_EXPERIMENTAL_LIMIT",
        "level": LEVEL, "workspace": workspace_spec(),
        "independent_reference": independent, "native_pyhf": native,
    }, indent=2, allow_nan=False))
    return 0 if not args.native or native["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
