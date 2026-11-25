# Independent canonical-basis acceptance in PhenoAgent

Start with the [task brief](TASK.md). The checker is an optional loop-amplitude
stage; it does not run MadGraph, change existing analysis routing, or claim an
experimental constraint. Install the isolated dependency with
`python -m pip install -r research/loop_basis/requirements.txt`.

## What PASS means

For the frozen, ordered source basis I with dI/dx = A_x I, the candidate
declares J = T I and supplies U = T^(-1). The verifier constructs the claimed
dlog target B_x = epsilon sum_a R_a (dW_a/dx)/W_a from rational constant
residues and the agreed alphabet. It checks T U = 1 and dT/dx + T A_x = B_x T
exactly in **every** direction. Multiplication on the right by U proves the
independently reconstructed connection (dT/dx + T A_x)U equals B_x without
expanding a matrix inverse. It then checks all directional commutators for
flatness (the exterior derivative of each dlog is zero).

Coefficient arithmetic is over Q(x,epsilon) or its single nonsquare quadratic
extension r^2 = D(x); r is differentiated by D'/2r. This proves a generic
identity, not invertibility at singular kinematics, branch choices for boundary
values, purity, the IBP reduction itself, or a full Feynman amplitude. A numerical
point agreement cannot pass the gate. No arbitrary Python/Wolfram expression
is executed, only the documented data grammar. Resource limits for proposals
use the benchmark deadline; direct CLI calls should use a resource-bounded
worker for external input.

## JSON contracts

- Source fields: `schema: "pheno-loop-source-v1"`; ordered unique `masters`;
  ordered `variables`; regulator symbol `epsilon`; `connections` keyed by all
  variable names; frozen `letters` mapping labels to nonzero kinematic expressions;
  optional `quadratic_root: {"name":"r","radicand":"..."}`.
- Proposal fields: `schema: "pheno-loop-proposal-v1"`; SHA-256 of exact source
  bytes in `source_sha256`; `transform`; `inverse`; `residues` keyed by frozen
  letter labels (omitted terms are zero). A candidate cannot amend the source,
  alphabet, direction set or conventions.
- Matrices are zero-based sparse triples `[row,column,value]`. Unlisted
  entries are zero. Values are JSON integers or strings using integer literals,
  variable names, parentheses and `+ - * / **` (literal integer powers, with
  absolute exponent at most 128). Use `"1/3"` not 0.333; use a declared root
  rather than `sqrt(...)`. Residues accept rational constants only.
- Compare transformation conventions: the CANON paper names the change with
  J = T_CANON^(-1) I; this checker calls its direct transform T = T_CANON^(-1).
  Inverting the matrix without also changing the convention is not equivalent.

```sh
python python-agent/tools/loop_basis_verify.py source.json candidate.json
python -m unittest discover -s python-agent/tests -p test_loop_basis_verify.py -v
```

## Fixed-rule / Agent comparison

Each operator-controlled search wrapper gets an identical copy of source.json
as its final argument, and emits individual complete proposal objects as JSONL
on stdout. Logs go on stderr. Invoke both via the same benchmark runner, e.g.:

```sh
python python-agent/tools/loop_basis_benchmark.py source.json new-run-dir \
  --fixed '["python","fixed_wrapper.py"]' \
  --agent '["python","agent_wrapper.py"]' \
  --budget-s 600 --seed 0 --expected-source-sha256 ACTUAL_SHA256
```

Use trusted wrappers, isolated working directories/environments, exact tool
and model revisions, fresh caches and the same search resources on each arm.
The runner does not itself sandbox executables or enforce API token budgets.
Freeze any additional reducer data and expose the exact same read-only
inputs on both sides, never the canonical answer or prior receipts. The
operator supplies the fixed strategy and real Agent wrapper; this package does
not ship or silently substitute a mock for either method.
Report planned repeated trials with alternating/randomized execution order and
timeouts as censored runs. The same verifier process checks each candidate;
wall time includes producer start, rejected candidates and accepted
verification. Compare elapsed values only when both arms pass. Each source,
candidate and verifier receipt is archived. `comparison.json` is a native
diagnostic timing log, not by itself a formal scientific performance claim.

## Exact 37-master double-box benchmark: blocked, not timed

[CANON §IV.1](https://arxiv.org/html/2611.33100v1#S4.SS1) specifies 37
masters, 24 sectors, five generic variables (including m²), and 21 active
letters with one square root. At author release commit
[6e5db3c](https://github.com/Alice-Shimada/CANON-release/tree/6e5db3c713d1602c0d79d01e0dcfef8e5acb5490/examples/double-box),
the three files are the final canonical integral expressions, alphabet and
logarithmic connection. The [release documentation](https://github.com/Alice-Shimada/CANON-release/blob/6e5db3c713d1602c0d79d01e0dcfef8e5acb5490/examples/README.md#ai4ut-examples)
explicitly says these exports contain no source-basis transform, reduction table
or intermediate result. They are appropriate for a held-out reference check,
not a blind search input. Feeding the canonical DE back as the input would
allow T = 1 and invalidate the comparison.

To unlock: obtain the ordered pre-canonical basis and its five exact
IBP-derived A_x (or regenerate them independently using the published
propagators and pin the reducer, derivatives, rules and source basis; the
regeneration is a separate untimed step). Freeze the 21-letter alphabet as
a shared verification contract, or report explicitly if the later experiment
changes to an alphabet-discovery task. Preserve normalization and scale
derivatives. Then smoke-test on the real matrices before registering tool
resources and multiple paired timing runs. No production reducer or Agent
timing was run here. Regression uses a hand-derived rational/quadratic
two-state example; a synthetic 37 by 37 fixture exercises five directions
but is not the paper family or a performance prediction.

Local evidence: Python 3.11+/SymPy 1.14 compatible syntax; the dedicated
unittest suite exercises exact PASS, sign errors, singular transforms,
a false candidate agreeing at three probes, wrong hash, missing direction,
bad root, nonconstant residues, forbidden syntax, nonflat connections,
noncommuting transform order, and first-PASS timing on replay stubs.
