# Repository instructions — Collider-Agent

These instructions are mandatory for agents and contributors. They complement the root README, the paper-reproduction guide, the individual Skills under `src/skills/`, and the research-result archival policy.

## 1. Minimal preflight

Before a substantive task:

1. Read this file and the root [README](README.md) or [Chinese README](README_zh.md).
2. Identify whether the task is a standalone model, simulation, analysis, plotting task, or a multi-stage/incremental pipeline.
3. Read the exact relevant Skill before invoking a subagent or Magnus blueprint. For a full pipeline, read `src/skills/pheno-pipeline-orchestrator/SKILL.md` and the Skills for each stage actually used.
4. For paper reproduction, read the selected `paper-reproduction/<arXiv-ID>/README.md`, the clean `prompt_figure_N.md`, and its annotated `_with_comments` companion only when debugging or authoring prompts.
5. Inspect existing `progress/run_manifest.yaml`, parent-run records, and generated files before starting. Never assume a prior run completed merely because a directory exists.

Do not claim that Magnus, FeynRules, MadGraph, Pythia, Delphes, or MadAnalysis ran unless the corresponding execution actually occurred and its result was inspected.

## 2. Run identity and incremental execution

- Give every run a short, unique, descriptive `run_label`. Record timestamp, task, exact source revision, and step statuses in `progress/run_manifest.yaml`.
- An incremental run must use a new label and include a `parent` link to the previous run. Never overwrite earlier progress, scripts, cards, event files, or execution summaries.
- Generate a new script/card/configuration for each changed parameter set. Do not rely on inherited MadGraph `run_card.dat` or parameter-card defaults when the task specifies values.
- Reuse unchanged compiled models/processes and upstream artifacts when scientifically justified, but execute every affected downstream step. Record exactly what was reused and why.
- Keep each stage's progress files under `progress/<run_label>/`; update the manifest after each step, including failures and retries.
- A run directory, Magnus job, or successful remote execution is not a permanent research archive.

## 3. Model construction and validation

For a FeynRules/UFO model:

1. Map every term in the requested Lagrangian to the actual model implementation, including fields, indices, representations, charges, parameters, and coupling definitions.
2. State field and parameter conventions, mass basis, mixing matrices, gauge-fixing assumptions, and simplifications.
3. Check Hermiticity, kinetic-term normalization, mass diagonalization, particle/antiparticle definitions, parameter dimensions, and UFO consistency as applicable.
4. For gauge theories, check gauge invariance and the treatment of Goldstone/ghost sectors where relevant. A model file compiling or passing a structural validator does not prove the physics model is complete.
5. Compare generated vertices and relevant Feynman rules with the Lagrangian or an independent analytic derivation. Do not silently omit terms that are difficult to implement.

Keep model-generation checks separate from cross-section validation and detector-level validation.

## 4. MadGraph, shower, and detector simulation

For every production run, record at least:

- process definition and multiparticle definitions;
- collider type, beam energies, and centre-of-mass energy;
- model/UFO identity and exact model parameters;
- PDF set and version, renormalization/factorization scales and scale choices;
- generation cuts, matching/merging settings, decay-chain definitions, and widths;
- requested/generated event counts, random seeds, event weights, cross section, and statistical uncertainty;
- MadGraph, Pythia8, Delphes, LHAPDF, and relevant card/tool versions.

Preserve exact MG5 scripts, parameter/run cards, process definitions, banners, logs, and run metadata needed to reproduce the result.

When Pythia8 or Delphes is used, record shower tune, hadronization/decay settings, detector card, pile-up assumptions, object definitions, and event losses. Do not compare parton-level, hadron-level, and reconstructed-level distributions as if they were the same observable.

Respect the format/analysis-level mapping in the MadAnalysis Skill: LHE is parton level, HepMC is hadron level, and LHCO/ROOT is reconstructed level. Do not pass an event file to a mismatched analysis level.

The current MadGraph simulator may delete and replace an existing output directory when downloading a result. Always use a fresh, run-specific output path unless replacement is explicitly intended and the old artifact has been safely preserved. The MadAnalysis cloud runner appends its own `submit analysis_output`; follow the Skill and do not insert a duplicate `submit` command.

## 5. Analysis and statistical integrity

- Preserve the exact analysis script, object definitions, cuts, cut order, histogram binning, normalization, luminosity, and input event-sample identity.
- Record cutflow counts and weighted yields at every stage. Distinguish generated events, selected events, weighted yields, cross sections, efficiencies, and expected counts.
- Check event-weight handling, filter efficiencies, branching ratios, k-factors, luminosity units, and normalization conventions. Do not multiply or divide by a correction factor twice.
- Include statistical uncertainties and, where relevant, systematic uncertainties and nuisance assumptions. State whether the analysis is parton, hadron, or detector/reconstruction level.
- A visually similar plot is not sufficient reproduction. Compare numerical axes, bins, cuts, normalization, benchmark parameters, and data points/curves against the source figure.
- Do not call a contour a confidence region or exclusion unless the likelihood/statistical construction, degrees of freedom, and threshold convention are specified and validated.

## 6. Paper-reproduction discipline

Each reproduction should have one identifiable target figure/observable, a clean prompt, explicit model and collider settings, and a defined acceptance criterion.

- Keep clean user-facing prompts separate from annotated developer prompts.
- Record the exact source-paper version, equation/table/figure, and any digitized or externally downloaded inputs.
- Distinguish exact reproduction, approximate reproduction, qualitative comparison, and failed reproduction.
- Record every deviation from the paper: software version, PDF set, cuts, detector card, event statistics, approximations, and missing private inputs.
- Do not tune parameters or normalize curves merely to make a plot look like the published figure. Explain discrepancies before proposing a physics or implementation change.

## 7. Agent orchestration and reporting

- Use the orchestrator for multi-stage and incremental tasks as defined in its Skill; standalone Skills remain appropriate for single-stage tasks.
- Delegate with explicit inputs, expected outputs, file paths, parameters, and acceptance checks. Inspect returned files rather than trusting a subagent's prose summary.
- The execution summary must map the user's physics specification to the actual model, MadGraph commands/cards, analysis cuts, and output files.
- The summary must include the archival/provenance section required by `execution-summarizer`, with one truthful status: `local only`, `committed to PR branch`, or `merged and verified on main`.
- Separate tool/blueprint success, model validation, event-generation validation, analysis validation, and scientific reproduction. One does not imply the others.

## 8. Secrets, archival, and Git workflow

- Never commit Magnus API keys, tokens, credentials, private data, licensed inputs that cannot be redistributed, or local environment files. Use the approved secret mechanism and record authorized retrieval instructions plus checksums for restricted inputs.
- Follow [docs/RESEARCH_RESULT_ARCHIVAL.md](docs/RESEARCH_RESULT_ARCHIVAL.md). Commit essential native outputs, scripts, cards, logs, summaries, and run manifests directly; do not create a new ZIP/TAR as a substitute for extracted outputs.
- For large event samples or binary detector outputs, use Git LFS or durable versioned storage with a committed manifest containing exact filenames, immutable locations, sizes, event counts, provenance, and SHA-256.
- After pushing, retrieve remote files and verify paths, sizes, counts, and hashes. Do not claim GitHub archival based only on a successful Magnus job or upload command.
- Use focused branches and PRs. Do not rewrite shared history or force-push over another contributor's work. State the exact checks run against the PR HEAD SHA.

## 9. Completion report

Report the run label and parent (if any), exact source and parameter configuration, each executed stage, outputs and event counts, cross sections and uncertainties, analysis cuts and yields, tests and validation evidence, deviations from the source paper, unresolved limitations, and exact GitHub archival status.

Never describe a simulation as a scientific reproduction merely because it ran successfully. Never describe a reproduced figure as a validated physical conclusion unless the derivation, inputs, statistical interpretation, and independent checks support it.

## CI is optional; research work must not wait for CI

Continuous integration (CI) is optional supporting infrastructure. It is not a prerequisite, acceptance gate, or merge condition for research work.

- Do not require a CI run to start, continue, or complete a calculation; perform numerical or scientific validation; prepare or archive results; commit or push research files; open or update a pull request; mark a pull request ready for review; or merge a pull request.
- If the calculation can be run directly on an available local machine or an approved compute runner, proceed. Do not pause research solely because GitHub Actions is queued, unavailable, disabled, blocked by account/billing limits, or failing for infrastructure reasons.
- GitHub Actions may still be used when useful as an optional compute, dispatch, or artifact-handoff mechanism. A workflow that actually executes a research calculation is an execution run: record its exact source commit, inputs, settings, environment, logs, and outputs. Its use does not make a separate CI status check mandatory.
- This policy does not waive scientific or numerical validation. Perform the checks appropriate to the claim—such as analytic identities, dimensional and unit checks, limiting cases, independent implementations, convergence, uncertainty estimates, provenance, and output-integrity checks—locally or on an approved runner, and record exactly what was performed. CI neither substitutes for these checks nor adds a mandatory gate.
- If CI is run, report its exact commit SHA and actual result. If it is not run, queued, blocked, cancelled, or failed, record that status truthfully and distinguish infrastructure failure from a scientific or numerical failure. Never describe an unrun check as passed.
- Base review and merge decisions on the actual diff, reproducibility, scientific evidence, scope, and the checks that are genuinely relevant to the change—not on whether a CI badge is green. Do not configure CI status checks as required branch-protection gates under this repository policy. Do not change repository protection settings without explicit authorization.
- CI becomes mandatory for a particular task only when the author explicitly requests it for that task.

