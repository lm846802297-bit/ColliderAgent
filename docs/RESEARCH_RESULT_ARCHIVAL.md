# ColliderAgent research-result archival extension

**Status:** Project-specific extension to the central Calculation-result Archival Policy.  
**Central source commit:** 14155487afc075d301fa7f6cf452c7bff137e869

The shared requirements for native-file archival, extract-before-upload, run provenance, checksums, remote verification, and the separation of archival from scientific validation are defined by the [central Calculation-result Archival Policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/14155487afc075d301fa7f6cf452c7bff137e869/docs/CALCULATION_RESULT_ARCHIVAL_POLICY.md). This document defines the ColliderAgent-specific result locations, event-data handling, and HEP run metadata.

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

## 3. Three-tier storage for Monte Carlo and restricted outputs

Choose storage by data role, size, access pattern, durability, licensing, and project budget. Do not migrate historical files merely to normalize storage.

- **Ordinary Git:** retain model sources, scripts/cards, manifests, provenance, validation reports, small/medium CSV/JSON outputs, cutflows, histograms, and reasonably sized native event samples that remain practical to inspect and clone.
- **Git LFS:** use prospectively for large binary event samples or detector-level outputs that must be versioned with the project and are still practical to retrieve as part of its working set. Keep the LFS pointer in Git and record the object SHA-256/OID, byte size, format, source run label, and referencing commit. Verify the actual downloaded bytes; a pointer alone does not prove availability.
- **External object storage:** use for bulk LHE/HepMC/ROOT/Parquet samples, extensive scans, or long-term datasets whose volume or access pattern makes Git/LFS unsuitable. Use immutable object/version IDs and a repository-side manifest with exact URI/version, filename, byte size, event/record count, format, source run label, SHA-256, retrieval instructions, and retention responsibility.

For every LFS or external object, verify retrieval after upload and compare exact bytes against the recorded SHA-256. Never use an expiring Magnus workspace, temporary runner directory, or Actions artifact as the sole permanent copy. Do not commit credentials, private data, or event files that cannot be redistributed. Do not introduce Git LFS or external storage without a concrete data-volume or retention need.

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
