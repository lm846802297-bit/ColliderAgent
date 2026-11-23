# Repository instructions — Collider-Agent

These instructions are mandatory for agents and contributors. The shared minimum requirements for research governance, compute execution, task handoff, scientific-change tracking, quality gates, document review, result archival, structured records, and Git integration are maintained centrally and pinned in [research/standards-lock.yaml](research/standards-lock.yaml). Start from the [Central Research Standards Index](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/CENTRAL_STANDARDS_INDEX.md). The local RESEARCH_COMPUTE_POLICY.md is only the ColliderAgent-specific Magnus and approved-runner adapter; it does not redefine the central primary-compute policy. The Agent/subagent architecture, FeynRules/UFO model checks, collider simulation, analysis, and paper-reproduction rules below remain project-specific and authoritative in this repository.


## 1. Minimal preflight

Before a substantive task:

1. Read this file, the root [README](README.md) or [Chinese README](README_zh.md), and [research/standards-lock.yaml](research/standards-lock.yaml).
2. Read the [Central Research Standards Index](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/CENTRAL_STANDARDS_INDEX.md). The pinned central standards are the authority for shared requirements; the local documents linked below define only ColliderAgent-specific extensions.
3. Before computational work, read [RESEARCH_COMPUTE_POLICY.md](RESEARCH_COMPUTE_POLICY.md) for the ColliderAgent-specific Magnus and approved-runner adapter.
4. For a substantial derivation, simulation, parameter scan, production-code change, scientific validation, or multi-agent handoff, prepare a concise Research Task Brief using the [central Task Handoff Standard](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/RESEARCH_TASK_HANDOFF_STANDARD.md) and [central task-brief template](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/templates/research-task-brief.md). A trivial editorial or maintenance change may omit a brief when the PR explains why it is not applicable.
5. Identify whether the task is a standalone model, simulation, analysis, plotting task, or a multi-stage/incremental pipeline.
6. Read the exact relevant Skill before invoking a subagent or Magnus blueprint. For a full pipeline, read src/skills/pheno-pipeline-orchestrator/SKILL.md and the Skills for each stage actually used.
7. For paper reproduction, read the selected paper-reproduction/<arXiv-ID>/README.md, the clean prompt_figure_N.md, and its annotated _with_comments companion only when debugging or authoring prompts.
8. Inspect existing progress/run_manifest.yaml, parent-run records, and generated files before starting. Never assume a prior run completed merely because a directory exists.
9. For numerical or simulation tasks, apply the task-appropriate profile in the [central Research Quality Gate](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/RESEARCH_QUALITY_GATE.md). Record PASS, FAIL, BLOCKED, NOT RUN, or justified N/A based on evidence actually obtained.

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
- The central [Calculation-result Archival Policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/CALCULATION_RESULT_ARCHIVAL_POLICY.md) governs shared archival requirements. The local archival document defines ColliderAgent result locations, native event formats, and Magnus-specific handoff.
- New substantial runs use central RCRPS v1.0.1 plus the local ColliderAgent extension in docs/STRUCTURED_RESULT_DATA_STANDARD_v1.0.1.md. Validate records with docs/schemas/validate_result_records.py and docs/schemas/research-result-record-v1.0.1.schema.json. Keep v1.0.0 only for historical compatibility.
- progress/run_manifest.yaml remains the incremental progress record; it does not replace the final RCRPS v1.0.1 JSON run_manifest, result_summary, and validation_report.
- For large event samples or binary detector outputs, use Git LFS or durable versioned storage with a committed manifest containing exact filenames, immutable locations, sizes, event counts, provenance, and SHA-256.
- After pushing, retrieve remote files and verify paths, sizes, counts, and hashes. Do not claim GitHub archival based only on a successful Magnus job or upload command.
- Use focused branches and PRs. Do not rewrite shared history or force-push over another contributor's work. Follow the [central Git merge policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/GIT_MERGE_POLICY.md) and the local GIT_MERGE_POLICY.md reproduction-archive extension. State the exact checks run against the PR HEAD SHA.

## 9. Completion report

Report the run label and parent (if any), exact source and parameter configuration, each executed stage, outputs and event counts, cross sections and uncertainties, analysis cuts and yields, tests and validation evidence, deviations from the source paper, unresolved limitations, and exact GitHub archival status.

Never describe a simulation as a scientific reproduction merely because it ran successfully. Never describe a reproduced figure as a validated physical conclusion unless the derivation, inputs, statistical interpretation, and independent checks support it.

## CI and independent verification

Follow the pinned central [Research Compute Policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/RESEARCH_COMPUTE_POLICY.md) and [Research Quality Gate](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/RESEARCH_QUALITY_GATE.md). GitHub Actions is optional supporting infrastructure and does not replace primary computation or scientific validation. Do not wait for CI when the required checks can be performed in the primary or another approved environment. Report the exact commit and checks actually run; never claim an unrun check passed.

## 10. Pull-request review and merge

Follow the pinned central [Git merge policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/GIT_MERGE_POLICY.md). The local GIT_MERGE_POLICY.md adds only ColliderAgent's paper-reproduction lifecycle and main-branch discoverability rules. Substantive model, simulation, analysis, reproduction, and validation work defaults to Create a merge commit under the central policy. Verify the integrated main state after merge.

## Research communication and task handoff

Follow the pinned central [Research Task Handoff Standard](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/RESEARCH_TASK_HANDOFF_STANDARD.md), [Research Governance Standard](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/RESEARCH_GOVERNANCE_STANDARD.md), and the research-reporting requirements in [Scientific Diff §11](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/scientific-diff-workflow.md#11-research-reporting-and-communication-standard). The central standards define shared task briefs, evidence requirements, and the Conclusion → Evidence → Results → Remaining work reporting structure.

For ColliderAgent reports, preserve the additional pipeline-specific mapping and stage-status requirements below. Do not conflate successful tool execution, model validation, event-generation validation, detector/analysis validation, and scientific reproduction.
### Collider pipeline reporting boundary

For an execution or reproduction report, retain the run label and parent run, exact source revision and parameter configuration, stages actually executed, outputs and event counts, cross sections and uncertainties, analysis cuts and yields, validation evidence, deviations from the source paper, and exact archival status. Keep tool/blueprint success, model validation, event-generation validation, analysis validation, and scientific reproduction as separate statuses. A completed stage remains a completed result even when a later stage is pending.
