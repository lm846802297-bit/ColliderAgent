---
name: integral-basis-audit
description: Validate and compare master-integral bases for a one-variable rational differential equation, including proposed AI bases, without conflating coefficient replay with native IBP reduction.
---

# Integral basis audit

Use for an analytic integral sector with a pinned IBP input or an independently published differential equation. Do not invoke the event-generation stack. This is opt-in; existing workflows do not switch basis automatically.

1. Pin the family, propagator order, dimension and sign conventions, units, invariant and parameter domain, source IBP deck or published system, and allowed transformation space. Record the fixed rule, AI proposer and candidate budget before evaluation. Provide the same inputs and independent acceptance thresholds to all arms.
2. Feed constructed SymPy matrices into `python-agent/tools/integral_basis_gate.py`. For `F' = A F, G = T F`, the gate computes `(T' + T A) T^-1`, checks the inverse and exact comparison against a separately derived equation for `G`. Do not pass a second copy of that expression as the reference. Preserve an explicit constant or subtopology master when turning an inhomogeneous equation into a matrix.
3. Check both ε denominators and kinematic poles, including the one-form at infinity. An algebraically valid basis can be a poor default. Record `KEEP_BASELINE` when a candidate introduces a new finite pole or worsens the apparent infinity order. An ε-polynomial is not an ε-form. This first implementation accepts only a one-variable rational transformation at generic parameter values; elliptic period normalization, branch handling and multivariate flatness are out of scope.
4. Report native IBP wall time separately, and only after both arms execute the same pinned solver, input identities, target deck, limits and resources. Record model/search time separately from backend time, repeat interleaved on the same host and preserve failures. A benchmark of already reduced coefficient evaluation cannot establish an IBP reduction speedup. If the solver is absent, record `NOT_RUN`; no automatic remote execution.
5. Check the bundled public rehearsal before applying the utility to a research calculation:

```bash
python -m unittest discover -s python-agent/tests -p 'test_integral_basis_gate.py' -v
python scripts/sunrise_basis_smoke.py --quadrature --timing
```

The latter uses SymPy and optionally SciPy for independent d=2 numerical quadrature. See [fixture and limits](../../../research/integral_basis_audit/README.md). Keep actual project amplitudes/results in their project repositories; this fixture validates the reusable tool.
