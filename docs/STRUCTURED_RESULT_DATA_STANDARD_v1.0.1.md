# Structured Research Result Data Standard v1.0.1

**Status:** **Adopted on 2026-11-23** by the project owner; effective for new substantial numerical, simulation, scan, and computational-validation runs from this date. See the [central formal adoption record](https://github.com/lm846802297-bit/high-energy-theory-research/blob/main/docs/governance/RCRPS_V1.0.1_ADOPTION_RECORD.md).  
**Schema:** JSON Schema Draft 2020-12.  
**Purpose:** Standardize data structure, run provenance, and archival. This standard does not certify scientific correctness.

## 1. Standard result bundle

For a substantial run, use the following roles where applicable:

- `run_manifest.json`: exact source revision, inputs, configuration, environment, command, outputs, checksums, and archive status.
- `result_summary.json`: benchmark, physical scope, observables with units, interpretation, and references to pointwise data.
- `validation_report.json`: actual analytic, numerical, convergence, independent, and integrity checks.
- Native `*.csv`, ROOT, HDF5, or Parquet files: pointwise arrays, spectra, scans, response grids, event/cutflow tables.
- `SHA256SUMS.txt`: hashes for archived data.
- `README.md`: human-readable conclusions and reproduction instructions.

Do not force every task to create every file. A substantial execution needs a machine-readable run manifest; a completed numerical result needs a result summary. Keep large arrays in native tabular/binary files rather than embedding them in JSON.

## 2. JSON record roles

The local `research-result-record-v1.0.1.schema.json` validates three record types:

- **run_manifest:** records what actually ran, including the commit SHA used at execution time, script path/fingerprint, input provenance (for repository-local inputs, a repository-relative path, byte count, and SHA-256; when input bytes are unavailable, an immutable URI plus version), physical/numerical configuration, software/hardware environment, exact command, output inventory, validation status, and archival status. The schema requires the entry-script SHA-256 and explicit runtime, dependency, and hardware records.
- **result_summary:** records what was calculated, the benchmark, scope, observables as numeric values plus separate unit fields, scientific status, interpretation, and data-file references.
- **validation_report:** records each check by ID, category, status, method, observed value, threshold, unit, and evidence path.

Use numeric JSON values rather than unit-bearing strings. Use `null` plus an explicit `not_computed` status for quantities not evaluated; never substitute zero. Do not encode NaN or Infinity.

## 3. Source-control provenance (v1.0.1)

Every new v1.0.1 `run_manifest` must contain `execution.source_control`. All 14 properties below are required. The exact checked-out commit remains `source.commit_sha`; do not duplicate it as `checked_out_sha`.

| Property | Meaning |
|---|---|
| `event` | Exact execution event, e.g. `pull_request`, `pull_request_target`, `push`, `workflow_dispatch`, `schedule`, `workflow_run`, `merge_group`, or `local` |
| `checkout_mode` | `pull_request_merge`, `pull_request_head`, `pull_request_base`, `branch_commit`, `detached_commit`, or `unknown` |
| `checkout_ref` | Fully qualified Git ref under `refs/`, valid under Git ref-name rules, or null when detached or unavailable |
| `pr_number` | Pull-request number, or null for non-PR events |
| `pr_url` | Canonical pull-request URL, or null for non-PR events |
| `pr_head_sha` | Exact PR source-head SHA, or null for non-PR events |
| `base_sha` | Exact PR target-base SHA, or null for non-PR events |
| `tested_merge_sha` | Synthetic merge SHA only when that merge commit was actually checked out and tested; otherwise null |
| `head_ref` | Valid PR source branch name, or null for non-PR events |
| `base_ref` | Valid PR target branch name, or null for non-PR events |
| `workflow_run_id` | Workflow run identifier, or null when no workflow run exists |
| `workflow_run_attempt` | Positive workflow attempt number, or null when no workflow run exists |
| `working_tree_state` | `clean`, `dirty`, or `unknown` |
| `dirty_paths` | Unique repository-relative POSIX paths modified/untracked in a dirty working tree; empty for a clean tree |

### Pull-request events

For `pull_request` and `pull_request_target`, PR number, URL, head/base SHAs, and head/base refs must be non-null. `source.commit_sha` records the exact checked-out commit; `checkout_mode` describes its PR role, while `checkout_ref` separately records the exact Git ref when available:

- `pull_request_merge`: `tested_merge_sha` must equal `source.commit_sha`.
- `pull_request_head`: `source.commit_sha` must equal `pr_head_sha`; `tested_merge_sha` is null.
- `pull_request_base`: `source.commit_sha` must equal `base_sha`; `tested_merge_sha` is null. This covers a `pull_request_target` workflow that executes the base branch.
- `unknown`: record the actual `source.commit_sha`, but set `tested_merge_sha` to null; do not claim a merge checkout without evidence.

When `checkout_ref` is known, it must agree with the checkout mode:
- `pull_request_merge`: `refs/pull/{pr_number}/merge`;
- `pull_request_head`: `refs/pull/{pr_number}/head` or `refs/heads/{head_ref}`;
- `pull_request_base`: `refs/heads/{base_ref}`;
- `unknown`: any valid fully qualified ref may be recorded.

A null `checkout_ref` remains valid when the exact ref is unavailable or the checkout is detached.

`head_ref`, `base_ref`, and `checkout_ref` have distinct meanings. In particular, a synthetic ref such as `refs/pull/104/merge` is a checkout ref, not the contributor's `head_ref`. Every non-null `checkout_ref` must be a fully qualified Git ref under `refs/` and pass Git ref-name syntax checks. `head_ref` and `base_ref` must be valid literal Git branch names.

Example PR merge fragment (illustrative values):

```json
{
  "source": {"commit_sha": "<tested-merge-sha>"},
  "execution": {
    "source_control": {
      "event": "pull_request",
      "checkout_mode": "pull_request_merge",
      "checkout_ref": "refs/pull/104/merge",
      "pr_number": 104,
      "pr_url": "https://github.com/example/research/pull/104",
      "pr_head_sha": "<pr-head-sha>",
      "base_sha": "<target-base-sha>",
      "tested_merge_sha": "<tested-merge-sha>",
      "head_ref": "feature/example",
      "base_ref": "main",
      "workflow_run_id": 123456,
      "workflow_run_attempt": 1,
      "working_tree_state": "clean",
      "dirty_paths": []
    }
  }
}
```

### Non-pull-request events

For every non-PR event, all seven PR-specific properties (`pr_number`, `pr_url`, `pr_head_sha`, `base_sha`, `tested_merge_sha`, `head_ref`, and `base_ref`) must be present and explicitly `null`. Do not omit them or insert placeholder SHAs.

Use `branch_commit`, `detached_commit`, or `unknown` as appropriate. A non-null `checkout_ref` must be a valid fully qualified Git ref under `refs/`. For non-PR events, `branch_commit` requires a `refs/heads/...` ref, while `detached_commit` requires `checkout_ref` to be null. `unknown` may record a ref if it is known. `source.commit_sha` still records the exact commit used. For a local execution without a workflow, both `workflow_run_id` and `workflow_run_attempt` are null; otherwise they must both be present. The legacy optional `source.workflow_run_id` is retained for v1.0.0 compatibility; if it appears in a v1.0.1 manifest, it must exactly match `execution.source_control.workflow_run_id` including JSON type. New v1.0.1 producers should omit the legacy duplicate and use the canonical execution field.

Example local fragment:

```json
{
  "source": {"commit_sha": "<actual-commit-sha>"},
  "execution": {
    "source_control": {
      "event": "local",
      "checkout_mode": "branch_commit",
      "checkout_ref": "refs/heads/main",
      "pr_number": null,
      "pr_url": null,
      "pr_head_sha": null,
      "base_sha": null,
      "tested_merge_sha": null,
      "head_ref": null,
      "base_ref": null,
      "workflow_run_id": null,
      "workflow_run_attempt": null,
      "working_tree_state": "clean",
      "dirty_paths": []
    }
  }
}
```

A clean tree requires an empty `dirty_paths`; a dirty tree requires at least one path. Paths must be normalized, unique, repository-relative POSIX paths without NUL bytes, absolute paths, or parent traversal. If dirty source files affect the run, archive and fingerprint the exact changed content or a reproducible patch/snapshot; path names alone do not reproduce dirty source.

The v1.0.1 schema is a validation superset: it accepts v1.0.0 records under their existing requirements, while requiring `execution.source_control` only for v1.0.1 `run_manifest` records. `result_summary` and `validation_report` do not gain source-control fields. The v1.0.0 schema remains unchanged, and historical records are not rewritten.

## 4. CSV and numeric arrays

Use a header row with stable column names and explicit units (for example `r_km`, `omega_MeV`, `ER_keV`). Use long/tidy format: one row per grid point or sample, with polarization, isotope, channel, coupling, or process as separate dimensions. Keep numeric columns numeric; preserve useful precision; distinguish missing data from physical zero; record row count, columns, units, byte size, and SHA-256 in the manifest. Do not silently resample, reorder, round, or change units.

## 5. Separate statuses

Keep execution, validation, scientific maturity, and archival status separate:

- execution: `not_started`, `running`, `succeeded`, `partial`, `failed`, `cancelled`, `blocked`;
- validation: `not_run`, `partial`, `passed`, `failed`, `blocked`, `inconclusive`;
- scientific status: `diagnostic`, `provisional`, `reproducible`, `validated`, `historical`, `superseded`;
- archive: `local_only`, `committed_to_pr_branch`, `merged_and_verified_on_main`.

A successful process exit is not numerical convergence; passing tests are not physical validation; an upload is not a verified main-branch archive.

## 6. Domain extensions

Keep shared fields at the top level. Put domain-specific physics fields under a namespaced `extensions` object. Preserve the exact conventions and dimensions required by each research area; do not flatten physically distinct quantities into one field.

For UV–EFT and loop calculations, record the model/Lagrangian version, field content, mass basis, coupling normalization, loop order, topology/subgraph, momentum conventions, gauge and gamma5 prescriptions, renormalization scheme/scale, IR regulator/subtraction, operator basis, matching scale, and counterterm coverage. Wilson coefficients must include basis order, dimensions, and units; per-diagram contributions should be tabulated separately.

For purely analytic derivations with no numerical arrays, do not create empty CSV files. Archive editable derivation sources and the run record for any symbolic execution.

## 7. Schema and archive validation

Validate JSON records with the local Draft 2020-12 validator:

```bash
python -m pip install -r docs/schemas/requirements-result-validation.txt
python docs/schemas/validate_result_records.py --schema docs/schemas/research-result-record-v1.0.1.schema.json --repo-root . results/<run_label>/run_manifest.json results/<run_label>/result_summary.json results/<run_label>/validation_report.json
```

The script checks schema validity, strict JSON numbers, referenced file paths/byte counts/SHA-256, and CSV row counts, headers, per-column units, and non-finite values. Pass only record files that exist for the run.

Run the validator's regression suite with `python -m unittest discover -s docs/schemas/tests -v`. It covers non-standard JSON constants, float overflow/underflow, and input provenance locator requirements. A validation status of `passed` requires at least one check and every check to be `passed`; otherwise use `partial`, `failed`, or `inconclusive`. Check CSV headers, units, row counts, finite numeric values, and grid coverage. Verify every referenced output's path, byte size, and SHA-256. After pushing, retrieve the remote files and compare paths, sizes, counts, and hashes. Report archive status separately from scientific validation.

## 8. Historical records

Apply this standard to new runs from adoption onward. Preserve existing JSON, CSV, logs, plots, and historical manifests byte-for-byte. Do not fabricate missing metadata or rewrite raw values to satisfy the new profile. A new index or manifest may reference a legacy file, clearly labelling it as legacy and only adding fields supported by source evidence.
## Collider-specific extension

### Collider Monte Carlo and paper reproduction

The existing `progress/run_manifest.yaml` may continue as the incremental progress record. Each substantial run must also produce a final `run_manifest.json`, `result_summary.json`, and `validation_report.json`, alongside the native event files and analysis outputs. The final JSON run manifest must include the full v1.0.1 `execution.source_control` record captured for the actual run checkout.

`extensions.collider_mc` records:

- Model/UFO name, version and file fingerprints; process definition and multiparticle definitions
- Collider type, beam energies, centre-of-mass energy, PDF set/version, and renormalization/factorization scales
- Generation cuts, matching/merging, decay chains, width scheme, and random seed
- Actual versions of MadGraph, Pythia8, Delphes, MadAnalysis5, FeynRules, LHAPDF, and related tools
- Requested/generated/selected event counts, event weights, cross sections, and statistical uncertainties
- Shower tune, detector card, pile-up, object definitions, cutflow, and systematic uncertainties
- The data level of each LHE/HepMC/ROOT/Parquet output: parton, hadron, or reconstruction level

Use CSV for cutflows, histograms, and cross-section scans. Preserve large event samples in their native LHE/HepMC/ROOT/Parquet formats and record event counts, weight conventions, byte sizes, and SHA-256. Keep tool/blueprint success, model validation, event generation, analysis validation, and paper reproduction as separate statuses.
