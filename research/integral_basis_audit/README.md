# Reusable master-integral basis audit

**Use it for:** proposed basis changes with a pinned, exact differential equation and an independent reference. A candidate that uses fewer arithmetic operations does not automatically replace the baseline. This feature is opt-in and does not run or install an IBP backend.

The [agent skill](../../src/skills/integral-basis-audit/SKILL.md) documents integration and separate speed gates; the [task brief](task_briefs/20261124-integral-basis-gate.md) freezes the pilot scope.

### Public smoke fixture

- [Petit Rosàs and Torres Bobadilla, arXiv:2611.26688v1](https://arxiv.org/html/2611.26688v1), End Matter Eq. (3) and Fig. 3b, with [ancillary PL1 definitions](https://arxiv.org/src/2611.26688v1/anc). D1, D2, D8 form the equal-internal-mass sunrise at the variable invariant s24; D7 would instead give the equal-mass pseudothreshold. The arXiv file is inspected as data; it does not supply our candidate transformation.
- [Laporta and Remiddi, hep-ph/0406160v3](https://arxiv.org/pdf/hep-ph/0406160v3), Eqs. (2.1)–(2.10). Euclidean z=-s24/me², me=1, d=2−2ε. Maintain constant H=1/(d−4)² to encode the tadpole source in their measure. This fixture does not reconstruct the 232-master d=4−2ε five-point basis or the radiative jet-function system.
- Fixed-rule control: (S,S1,H), lowest-dot masters. One AI-proposed alternative, frozen before measurements: (S,Q S',H) with Q=z(z+1)(z+9), det(T)=3(z+1)(z+9). Both use the same input (Eq. 2.8). The reference is separately reconstructed from the second-order Eq. 2.9; an additional numerical simplex integral tests the physical equation without solving either system.
- Both forms are ε-regular and quadratic in ε, not ε-factorized. The alternative lowers nonzero entries from 5 to 4 and SymPy operation count from 49 to 36, but worsens the largest apparent 1-form pole at infinity from order 1 to 3. This is a change of representation, not a new physical singularity. The conservative policy therefore keeps the baseline. The maximum absolute d=2 equation residual on three spacelike points is below 5e−13.
- The timed evaluation is five identical exact rational substitutions, interleaved over seven warmed rounds. It times already-derived equation coefficients, not IBP generation/elimination or the proposer. This is one AI proposal, not a blinded performance study. Native IBP time, end-to-end speedup, automated basis search and ε-form construction are not evaluated.

### Reproduce

```bash
python -m unittest discover -s python-agent/tests -p 'test_integral_basis_gate.py' -v
python scripts/sunrise_basis_smoke.py --quadrature
python scripts/sunrise_basis_smoke.py --timing
```

Local Linux/Python 3.12.14/SymPy 1.14.0; optional independent quadrature used SciPy 1.17.0. The `sunrise_verified.json` file has deterministic checks, pointwise original numerical results and source hashes. The separately archived timing observation is environment-dependent and should not be compared across hosts or described as native IBP. For the next benchmark, execute both choices using a common actual IBP deck and frozen solver, with a known held-out target and a separate wall/peak-memory comparison.
