# Native pyhf one-bin backend benchmark

The synthetic background-Asimov one-bin likelihood (100 background
events, 20 nominal signal events, no nuisance parameters) passes the
pyhf 0.7.6 native benchmark. This verifies backend parity, not an
experimental exclusion or statistical coverage.

- Median expected 95% CLs signal strength: **1.0450250398230625**.
- Observed-on-Asimov signal strength: **1.0450250398230696**. No measured
  data are used.
- Maximum absolute residual: **5.94e-14** across the five CLs points
  for both variants, and **2.53e-13** across the two limits.
- [Exact native JSON](native_pyhf.json),
  [run manifest](run_manifest.json), [signed residuals](result_summary.json),
  [checks](validation_report.json), and [task brief](TASK_BRIEF.md).

The entrypoint and tests are byte-identical to the
[frozen source branch](https://github.com/lm846802297-bit/ColliderAgent/tree/1d9d2ea1a6c3cbcdae380ae49d8009ae55d50512).
The manifest records the actual governance checkout plus those two
additive input files at run time. The PyPI pyhf wheel was checked against
the [pinned public source](https://github.com/scikit-hep/pyhf/tree/b500270c6a7744d16b481dfda247c066ef3c2cb4).
No third-party wheel is redistributed here.

For replay use [the official wheel hashes](replay-wheels.txt) and the
recorded base environment versions, place the four verified wheels in an
isolated Python target (no user or system install), set PYTHONPATH to
that target, and run, from the repository root:

~~~sh
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python scripts/one_bin_asimov_limit.py --native
~~~

The archived bytes reproduced across three runs in the recorded environment.
On a different host check the declared numeric tolerances, not platform
byte equality. The manifest's archive status is the status when captured.
