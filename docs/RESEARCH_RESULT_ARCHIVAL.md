# ColliderAgent research-result archival extension

**Status:** Project-specific extension to the central Calculation-result Archival Policy.  
**Central source commit:** 142267bc803c90aa681110293b66b73947bbcaa1

The shared requirements for native-file archival, extract-before-upload, run provenance, checksums, remote verification, and the separation of archival from scientific validation are defined by the [central Calculation-result Archival Policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/CALCULATION_RESULT_ARCHIVAL_POLICY.md). This document defines the ColliderAgent-specific result locations, event-data handling, and HEP run metadata.

## 1. Canonical result location

- ColliderAgent is primarily the reproducible pipeline and Agent-tool repository. When a paper-specific result belongs to another research project, archive the authoritative scientific result in that project's repository and record its immutable repository path, commit, and PR in the execution summary.
- When a reproduction is deliberately maintained here, use paper-reproduction/<arXiv-ID>/results/<run_label>/.
- Keep prompts and original paper assets separate from generated results. Preserve a unique run label and parent relationship for every incremental run.
- Keep model sources, UFO directories, scripts/cards, raw event samples, processed analysis tables, plots, progress records, and final summaries distinguishable.

## 2. Collider-native outputs

Retain the native files needed to inspect and reproduce the executed stages, as applicable:

- FeynRules model sources and generated UFO files;
- exact MadGraph process definitions, scripts, parameter cards, run cards, banners, and logs;
- native event data such as LHE, HepMC, ROOT, or Parquet;
- Pythia8 settings, Delphes detector cards, MadAnalysis scripts, and analysis code;
- cross-section tables, cutflows, weighted yields, histograms, plots, and post-processing outputs;
- progress records, final RCRPS records, execution summaries, and checksum manifests.

Keep raw event data, showered event data, detector/reconstruction-level data, processed tables, and plots separate. Record every event selection, filtering, normalization, histogramming, and other transformation.

## 3. Large Monte Carlo and restricted outputs

- Commit reasonably sized essential outputs directly when licensing and repository limits permit.
- Use Git LFS or approved durable, versioned storage for large event samples and detector-level binary outputs.
- For externally stored outputs, commit a manifest with exact filenames, format, byte size, event/record count, immutable URI or release/version, source run label, and SHA-256.
- Do not rely on a Magnus workspace or expiring Actions artifact as the only copy of a result. Do not commit credentials, private data, or event files that cannot be redistributed.

## 4. Collider run metadata

The existing progress/run_manifest.yaml remains the incremental orchestration and progress record. For each substantial completed run, also produce the final RCRPS v1.0.1 records under the run's result directory:

- run_manifest.json: actual source checkout, inputs, parameters, environment, commands, outputs, provenance, and archive state;
- result_summary.json: physical/numerical results, units, uncertainties, scope, and scientific status;
- validation_report.json: only checks actually executed, with methods, observed values, thresholds, and evidence.

The JSON run manifest must contain the complete 14-field execution.source_control object required by central RCRPS v1.0.1. Capture it at run start, before generating files, and preserve the actual source.commit_sha used by the run. The progress YAML does not replace the final JSON run manifest.

The collider-specific fields are defined in the local [RCRPS v1.0.1 ColliderAgent extension](STRUCTURED_RESULT_DATA_STANDARD_v1.0.1.md).

## 5. Archive status and scientific status

The execution summary must use one truthful archive status:

- local only;
- committed to PR branch;
- merged and verified on main.

After pushing, retrieve the remote files and compare paths, sizes, counts, and SHA-256. Do not claim that a Magnus job, upload command, or successful process exit constitutes a permanent GitHub archive.

Keep archive status separate from execution, model validation, event-generation validation, detector/analysis validation, numerical validation, and scientific reproduction. A complete event sample or matching checksum does not establish a physical conclusion.
