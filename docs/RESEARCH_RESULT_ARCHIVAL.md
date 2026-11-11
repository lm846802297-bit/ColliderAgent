# Research-result archival and reproducibility policy

**Status:** Mandatory for completed paper-reproduction and collider-phenomenology runs maintained in this repository.

Collider-Agent can generate models, Monte Carlo events, analysis outputs, plots, and execution reports through local tools or the Magnus platform. A file remaining in a temporary working directory or cloud workspace is not a durable research archive. This policy complements the root README, the paper-reproduction examples, and the execution-summary/orchestrator Skills.

## 1. Decide where the canonical result belongs

- Collider-Agent is primarily the reproducible pipeline/tool repository. A paper-specific result should be archived in the research repository that owns the scientific study whenever one exists; record the repository path and immutable commit/PR in the execution summary.
- If a reproduction is deliberately maintained as an example in this repository, put the completed run under `paper-reproduction/<arXiv-ID>/results/<run_label>/`. Keep prompts and original paper assets separate from generated results. Do not overwrite a previous run; use a new run label or versioned directory.
- Keep executable scripts, model files, analysis code, configuration, progress records, and outputs distinguishable. The generated execution summary must point to the exact files used for the result.

## 2. Commit native result files directly

- Commit the essential, directly usable outputs in their native formats: generated `.fr`/UFO sources where needed, MadGraph scripts and cards, analysis scripts, cross-section tables, cutflow tables, CSV/JSON/JSONL/TXT outputs, plots, and the exact run manifest.
- **Do not create a new ZIP/TAR archive as a substitute for committing the extracted result files.** Reviewers must be able to inspect the data files directly.
- If an input was provided as an archive, extract the files required for the run and commit those extracted files when redistribution is permitted. Record the original archive filename, source/version, size, SHA-256, extraction command, and hashes of the extracted files.
- Preserve tool-native formats when they are the actual data product (for example a MadGraph-generated compressed LHE file); document the producing tool and command. Do not wrap ordinary outputs in an extra ZIP/TAR.
- Keep raw simulation output, processed analysis tables, and plots clearly separated. Record any filtering, event selection, normalization, histogramming, or other post-processing.

## 3. Large Monte Carlo and binary outputs

- Commit reasonably sized essential outputs directly when licensing and repository limits permit.
- Large event samples, detector-level files, or binary outputs that exceed ordinary GitHub limits should use Git LFS or a durable, versioned storage location approved for the project. Do not silently omit them and do not rely on an expiring Magnus workspace or GitHub Actions artifact as the only copy.
- Commit a manifest for every externally stored output, listing the exact filename, format, byte size, event/record count where relevant, immutable URI or release/version identifier, source run label, and SHA-256 checksum. Prefer separate native files over newly created archive bundles.
- Never commit Magnus API keys, tokens, credentials, private data, or non-redistributable event/data files. Store only permitted files and provide authorized retrieval instructions plus checksums for restricted data.

## 4. Required run provenance

For each substantial run, retain `progress/run_manifest.yaml` and/or an equivalent run record with:

- run label, timestamp, task description, and parent run for incremental runs;
- exact Collider-Agent source commit and the relevant prompt/analysis-script revisions;
- model parameters, process definition, collider energy, PDF set, generation cuts, event count, detector/analysis settings, and random seeds;
- Magnus/local execution mode and relevant versions of MadGraph5, Pythia8, Delphes, MadAnalysis5, FeynRules, Python, and other tools actually used;
- exact commands or blueprint/CLI execution instructions;
- output paths, formats, byte sizes, event/row counts, and SHA-256 checksums;
- failed steps, warnings, retries, discarded runs, post-processing, and validation status.

The execution summary must identify the generated files and map the user's physics specification to the actual scripts and parameters. A run manifest or summary is not a substitute for the underlying data files.

## 5. Verification before claiming archival completion

1. Check that required outputs exist and are non-empty; verify event counts, table dimensions, units, finite values, and the run-specific validation criteria.
2. Curate the essential deliverables into the canonical research repository or the designated `paper-reproduction/<arXiv-ID>/results/<run_label>/` directory.
3. Commit through a focused branch and pull request. Include the run manifest, execution summary, source/scripts, essential native outputs, provenance, and checksums.
4. After pushing, retrieve the committed files from GitHub and compare paths, sizes, counts, and SHA-256 checksums with the local submission. Verify the merged main-branch paths after merge.
5. In the execution summary, state the archive status explicitly: `local only`, `committed to PR branch`, or `merged and verified on main`. Never claim a result is archived on GitHub merely because a pipeline or upload command completed.
6. Keep archival status separate from physics validation. A successful simulation, a complete event sample, a green CI run, or matching hashes does not by itself validate the model or establish the physical conclusion.

This policy applies to every future paper reproduction and collider-phenomenology result maintained in this repository.
