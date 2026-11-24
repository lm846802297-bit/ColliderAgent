"""Exact checks for a one-variable rational master-integral basis change.

This module accepts constructed SymPy matrices, not expression strings. It
does not run an IBP solver; use a separately measured backend for that claim.
"""
from time import perf_counter_ns
from statistics import median

import sympy as sp


def _cancel(m):
    return sp.Matrix(m).applyfunc(sp.cancel)


def _require_equal(a, b, label):
    a, b = sp.Matrix(a), sp.Matrix(b)
    if a.shape != b.shape or any(sp.cancel(x) != 0 for x in a - b):
        raise ValueError(label)


def _order_at_infinity(expr, x):
    # The coefficient is of a one-form: dx = -dt/t**2 for t = 1/x.
    if not expr:
        return 0
    a, b = sp.fraction(sp.cancel(expr))
    return max(0, int(sp.degree(a, x) - sp.degree(b, x) + 2))


def audit_basis(matrix, transform, coordinate, epsilon, reference):
    """Check f'=A f, g=T f. Reference must be supplied by an independent route.

    Metrics treat all symbols other than the selected one as coefficients
    at generic parameter values. The infinity pole is basis dependent.
    Neither a polynomial in epsilon nor a short DE proves epsilon form.
    """
    A, T, B_ref = map(sp.Matrix, (matrix, transform, reference))
    x, e = coordinate, epsilon
    if not isinstance(x, sp.Symbol) or not isinstance(e, sp.Symbol) or x == e:
        raise ValueError("coordinate and epsilon must be distinct symbols")
    if not A.rows or not (A.rows == A.cols and A.shape == T.shape == B_ref.shape):
        raise ValueError("matrices must be nonempty, square and of the same shape")
    if not all(v.is_rational_function(x, e) for v in list(A)+list(T)+list(B_ref)):
        raise ValueError("this gate only handles rational dependence")
    det = sp.factor(T.det())
    if det == 0:
        raise ValueError("singular basis change")
    inverse = _cancel(T.inv())
    _require_equal(T * inverse, sp.eye(A.rows), "inverse identity failed")
    B = _cancel((T.diff(x) + T*A) * inverse)
    _require_equal(B, B_ref, "independent differential equation differs")
    _require_equal(B*T - T.diff(x), T*A, "back-substitution differs")
    poles = []
    x_poles = {}
    order = 0
    for i in B:
        num, den = sp.fraction(i)
        for factor, power in sp.Poly(den, x).factor_list()[1]:
            fid = str(sp.factor(factor.monic().as_expr()))
            x_poles[fid] = max(x_poles.get(fid, 0), int(power))
        if den.has(e):
            poles.append(str(sp.factor(den)))
        elif i:
            order = max(order, int(sp.degree(num, e)))
    pure = not poles and all(
        not v or (sp.cancel(v/e).subs(e, 0) not in (sp.zoo, sp.oo, -sp.oo, sp.nan)
                  and not sp.cancel(v/e).has(e))
        for v in B
    )
    return B, {
        "determinant": str(det), "reference_match": True,
        "epsilon_denominators": sorted(set(poles)),
        "finite_kinematic_poles_generic": dict(sorted(x_poles.items())),
        "max_epsilon_degree_if_polynomial": None if poles else order,
        "epsilon_factorized": pure,
        "zero_epsilon_nonzero_entries_if_regular": None if poles else
            sum(v.subs(e, 0) != 0 for v in B),
        "apparent_infinity_pole_order": max(_order_at_infinity(v, x) for v in B),
        "nonzero_entries": sum(v != 0 for v in B),
        "symbolic_operation_count": sum(int(sp.count_ops(v)) for v in B),
    }


def compare_basis_reports(baseline, candidate):
    """Conservative structural recommendation, independent of replay speed."""
    reasons = []
    if set(candidate["epsilon_denominators"]) - set(baseline["epsilon_denominators"]):
        reasons.append("new epsilon denominator")
    existing = baseline["finite_kinematic_poles_generic"]
    if any(order > existing.get(pole, 0)
           for pole, order in candidate["finite_kinematic_poles_generic"].items()):
        reasons.append("new or higher finite kinematic pole at generic parameters")
    if candidate["apparent_infinity_pole_order"] > baseline["apparent_infinity_pole_order"]:
        reasons.append("higher apparent one-form pole order at infinity")
    if reasons:
        return {"recommendation": "KEEP_BASELINE", "reasons": reasons}
    return {"recommendation": "ELIGIBLE_FOR_BENCHMARK", "reasons": []}


def time_exact_replay(matrices, ordered_points, repetitions=7, timer=perf_counter_ns):
    """Measure exact evaluation of already-derived DEs, never native IBP time."""
    matrices, points = tuple(matrices), tuple(ordered_points)
    if len(matrices) < 2 or not points or not 1 <= repetitions <= 100:
        raise ValueError("two or more matrices, a point grid, and 1–100 rounds required")
    samples = [[] for _ in matrices]

    def replay(A):
        for point in points:
            evaluated = A.subs(point, simultaneous=True)
            if not all(v.is_finite is True for v in evaluated):
                raise ValueError("benchmark grid is singular or incompletely specified")

    for A in matrices:
        replay(A)  # same warm-up count for each arm
    for r in range(repetitions):
        for i in (range(len(matrices)) if r % 2 == 0 else range(len(matrices)-1, -1, -1)):
            start = timer()
            replay(matrices[i])
            samples[i].append(timer()-start)
    return {
        "scope": "exact pre-reduced DE evaluation only; no native IBP",
        "points_per_round": len(points), "rounds": repetitions,
        "samples_ns": samples, "median_ns": [median(s) for s in samples],
    }
