#!/usr/bin/env python3
"""Exact analytic control for a massless QED tree interoperability benchmark."""
from __future__ import annotations

import json
from fractions import Fraction

METRIC = (1, -1, -1, -1)
POINTS = ((5, 0, -5), (5, 4, -3), (5, 5, 0), (5, 4, 3), (5, 0, 5), (10, 8, 6))


def dot(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(g * x * y for g, x, y in zip(METRIC, a, b))


def trace_tensor(a: tuple[int, ...], b: tuple[int, ...]) -> list[list[int]]:
    """Return Tr[a_slash gamma^mu b_slash gamma^nu] / 4."""
    ab = dot(a, b)
    return [[a[m] * b[n] + a[n] * b[m] - (METRIC[m] * ab if m == n else 0)
             for n in range(4)] for m in range(4)]


def reference_point(energy: int, transverse: int, longitudinal: int) -> dict:
    if energy <= 0 or transverse < 0 or transverse**2 + longitudinal**2 != energy**2:
        raise ValueError("Require on-shell massless COM momenta with positive energy")
    p1, p2 = (energy, 0, 0, energy), (energy, 0, 0, -energy)
    k1, k2 = (energy, transverse, 0, longitudinal), (energy, -transverse, 0, -longitudinal)
    q = (2 * energy, 0, 0, 0)
    s, t, u = dot(q, q), -2 * dot(p1, k1), -2 * dot(p1, k2)
    electron, muon = trace_tensor(p2, p1), trace_tensor(k1, k2)
    contraction = sum(METRIC[m] * METRIC[n] * electron[m][n] * muon[m][n]
                      for m in range(4) for n in range(4))
    # Each trace contributes 4 and the two incoming spin averages contribute 1/4.
    ward = [all(sum(METRIC[m] * q[m] * r[m][n] for m in range(4)) == 0
                for n in range(4)) for r in (electron, muon)]
    return {
        "p1": p1, "p2": p2, "k1": k1, "k2": k2,
        "s_GeV2": s, "t_over_s": Fraction(t, s), "u_over_s": Fraction(u, s),
        "cos_theta": Fraction(longitudinal, energy),
        "spin_averaged_M2_over_e4": Fraction(4 * contraction, s**2),
        "electron_ward_tensor_zero": ward[0], "muon_ward_tensor_zero": ward[1],
    }


def main() -> None:
    print(json.dumps({
        "schema": "collideragent-qed-tree-reference-v1",
        "scope": "PYTHON_EXACT_TRACE_REFERENCE_ONLY",
        "wolfram_interoperability": "NOT_RUN",
        "points": [reference_point(*p) for p in POINTS],
    }, default=str, indent=2))


if __name__ == "__main__":
    main()
