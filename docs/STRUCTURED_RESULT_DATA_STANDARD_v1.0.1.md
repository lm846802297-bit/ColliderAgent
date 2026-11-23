# ColliderAgent RCRPS v1.0.1 domain extension

**Status:** Project-specific extension to the centrally adopted RCRPS v1.0.1.  
**Central source commit:** 142267bc803c90aa681110293b66b73947bbcaa1

The common record types, shared fields, 14-field source-control contract, status semantics, and JSON Schema requirements are defined by the [central Structured Research Result Data Standard v1.0.1](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/STRUCTURED_RESULT_DATA_STANDARD_v1.0.1.md). This file defines only the ColliderAgent-specific extensions and run conventions. It is not a second copy of the central standard.

The local schema, validator, pinned validation dependency, and regression suite are maintained under docs/schemas. The v1.0.1 schema accepts historical v1.0.0 records under their original requirements; new substantial runs use v1.0.1.

## 1. Progress records and final run records

- progress/run_manifest.yaml remains the incremental orchestration record. It tracks run labels, parent runs, timestamps, and the status of individual pipeline stages.
- For every substantial numerical, simulation, scan, or validation run, the execution-summarizer produces final run_manifest.json, result_summary.json, and validation_report.json in the run's result directory.
- The final run_manifest.json must contain the full 14-field execution.source_control object from the central standard. Capture it before creating output files and preserve the exact source.commit_sha used by the run.
- Do not overwrite previous run records or outputs. An incremental run uses a new run label and links its parent.

## 2. Collider-specific extensions.collider_mc

Record the following collider-specific information under extensions.collider_mc, keeping the central RCRPS common fields at the top level:

- Model/UFO name, version, and file fingerprints; process definition and multiparticle definitions.
- Collider type, beam energies, centre-of-mass energy, PDF set/version, and renormalization/factorization scales.
- Generation cuts, matching/merging settings, decay chains, width scheme, and random seeds.
- Actual versions of MadGraph, Pythia8, Delphes, MadAnalysis5, FeynRules, LHAPDF, and other tools used.
- Requested, generated, and selected event counts; event weights; cross sections; and statistical uncertainties.
- Pythia shower tune, hadronization/decay settings, Delphes detector card, pile-up assumptions, reconstructed-object definitions, cutflows, and systematic uncertainties.
- The data level of each event output: LHE as parton level, HepMC as hadron level, and LHCO/ROOT as reconstructed or detector-analysis level, with the exact mapping stated for any other format.

## 3. Native data and analysis conventions

- Use CSV for cutflows, histogram tables, cross-section scans, and other directly inspectable tabular outputs.
- Preserve event-level outputs in their native LHE, HepMC, ROOT, or Parquet formats. Record event counts, weight conventions, byte sizes, and SHA-256.
- Keep generated events, showered events, detector/reconstruction-level events, selected samples, and derived histograms distinguishable.
- Record object definitions, cut order, luminosity, normalization, filter efficiencies, k-factors, branching fractions, and statistical/systematic uncertainties when they affect the result.

## 4. Validation and status separation

Use the central Research Quality Gate task profile appropriate to the work. Keep these ColliderAgent-specific validation states distinct:

- tool or blueprint execution;
- FeynRules model and UFO validation;
- MadGraph event-generation validation;
- Pythia shower and Delphes detector validation;
- MadAnalysis cutflow/histogram validation;
- numerical/statistical validation;
- scientific paper-reproduction status.

A successful tool call or schema check does not validate the physics model, event generation, detector response, analysis, or reproduced scientific claim.

## 5. Validation commands

Install the pinned dependency and run the local regression suite:

    python -m pip install -r docs/schemas/requirements-result-validation.txt
    python -m unittest discover -s docs/schemas/tests -v
    python -m compileall -q docs/schemas

Validate the records that actually exist for a run:

    python docs/schemas/validate_result_records.py --schema docs/schemas/research-result-record-v1.0.1.schema.json --repo-root . results/<run_label>/run_manifest.json results/<run_label>/result_summary.json results/<run_label>/validation_report.json

The validator checks strict JSON parsing, schema validity, referenced file paths and hashes, CSV dimensions/units, and v1.0.1 source-control semantics. A passing validator establishes only those structural and integrity properties; it does not establish physical correctness.

## 6. Historical v1.0.0 records

The v1.0.0 standard and schema are retained only for historical compatibility. Do not rewrite legacy event outputs or invent missing provenance fields. New substantial runs use central RCRPS v1.0.1 plus this collider-specific extension.
