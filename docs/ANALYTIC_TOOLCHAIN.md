# Analytic toolchain capability preflight

ColliderAgent's FeynRules model validation and UFO/CalcHEP exports use their own
Wolfram/Magnus runners. They do not verify FeynCalc amplitude algebra, FeynArts
diagram generation, or the FeynArts-to-FeynCalc conversion interface. Keep
analytic checks, numerical/simulation cross-validation, and statistical limits
as separate evidence. A model that loads is not a validated amplitude, and a
cross section alone does not establish an exclusion.

## Choose and check an analytic profile

| Profile | Minimum local component smoke check |
| --- | --- |
| `wolfram` | Start a local Wolfram kernel and evaluate a fixed exact arithmetic expression |
| `feyncalc` | Kernel plus loading FeynCalc and locating its `DiracSimplify` symbol |
| `feynarts` | Kernel plus loading FeynArts and locating its `CreateTopologies` symbol |
| `feynarts-feyncalc` | The two package load checks in separate sessions, not interoperability |

Pick the profile the task actually needs; neither MadGraph nor the two
analytic packages are mandatory for every calculation. Run the preflight on
the actual intended compute environment, not on a different workstation:

```sh
python scripts/check_analytic_toolchain.py --backend local --profile feynarts-feyncalc
```

Default mode is discovery only. PATH visibility is not evidence that the
kernel starts, that it is licensed/available, or that packages load. If the
selected backend is `magnus`, this new analytic route reports a blocked
adapter and does not consult local PATH or dispatch an existing blueprint.
The existing FeynRules/MadGraph routes are unchanged.
Other toolchains, including dark-matter/recast packages, should add their
own task-specific capability checks and validation evidence, not inherit a
pass from this Wolfram profile. The existing CalcHEP/micrOmegas routes are
separate and are not checked by this command.

On an already authorized machine with a trusted installed Wolfram launcher
and packages, explicitly opt in to the fixed native smoke test:

```sh
python scripts/check_analytic_toolchain.py --backend local --profile feynarts-feyncalc --native
```

This launches the local kernel with fixed code, waits at most 45 seconds per
component, and stops on the first blocker. It does not accept a user-supplied
Wolfram script, install packages, activate licenses, or dispatch external
jobs. Wolfram's local startup configuration still applies. Use only an
approved installation and package paths; do not publish startup logs or
license information. Standalone FeynArts is checked under its own context.
A patched/add-on-only FeynArts installation may not pass this particular
standalone check; it needs a recorded, dedicated conversion check, not a
readiness override.

The JSON distinguishes `UNVERIFIED`, `BLOCKED`, and
`COMPONENTS_SMOKE_PASSED`, with per-component native statuses and an
independent `scientific_validation` status. Exit 0 means the requested
discovery or native smoke completed; **check the JSON mode and status**, not
just the process exit. A missing launcher/adapter, timeout, malformed native
receipt, or failed check exits 2. No physics result is claimed by any status.

## Before claiming scientific reproduction

For a real analytical run, record the exact Wolfram kernel and FeynCalc /
FeynArts package versions and hashes, model and source revision, domain
conventions (including gauge, representation, momentum and dimensions),
executed command, native amplitudes or diagrams, and checks with their scope.
If combining FeynArts with FeynCalc, pin the compatible interface and
validate conversion on one known amplitude; isolated package load checks
do not check model normalization or name collisions. Keep project-specific
models, calculations, data, and scientific acceptance evidence in their
project repository. See the [compute policy](../RESEARCH_COMPUTE_POLICY.md)
and the upstream [WolframScript documentation](https://reference.wolfram.com/language/ref/program/wolframscript.html)
and [FeynCalc FeynArts interface notes](https://feyncalc.github.io/FeynCalcBook/Extra/FeynArts.html).
