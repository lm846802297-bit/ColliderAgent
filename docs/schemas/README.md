# Structured research-result schema and validator

This directory contains the ColliderAgent copy of the centrally adopted RCRPS v1.0.1 implementation from `high-energy-theory-research`.

The v1.0.1 schema is a compatibility superset: it accepts v1.0.0 records under their original requirements and requires the 14-field `execution.source_control` contract only for v1.0.1 `run_manifest` records.

## Contents

- `research-result-record-v1.0.1.schema.json`: adopted Draft 2020-12 schema for v1.0.0 and v1.0.1 run manifests, result summaries, and validation reports
- `research-result-record-v1.0.0.schema.json`: frozen legacy schema for explicit v1.0.0-only validation
- `validate_result_records.py`: strict JSON parsing, schema validation, input/output path and SHA-256 checks, CSV structural/unit checks, and v1.0.1 source-control semantic validation
- `requirements-result-validation.txt`: pinned `jsonschema[format]==4.26.0` dependency, including URI format validation
- `tests/rcrps_v1_0_1_fixtures.py`, `tests/test_source_control_schema_v1_0_1.py`, and `tests/test_source_control_semantics_v1_0_1.py`: central schema and semantic regression fixtures
- `tests/test_validate_result_records.py`: v1.0.0 compatibility and strict JSON/input provenance tests

## Run the tests

```bash
python -m pip install -r docs/schemas/requirements-result-validation.txt
python -m unittest discover -s docs/schemas/tests -v
python -m compileall -q docs/schemas
```

## Collider run records

Keep `progress/run_manifest.yaml` for incremental orchestration state. For every substantial run, the execution-summarizer must also produce final `run_manifest.json`, `result_summary.json`, and `validation_report.json` records under the run's results directory.

Capture the 14-field source-control object at run start, before output files are generated, and carry that frozen object into the final run manifest. Preserve the `extensions.collider_mc` profile and native LHE/HepMC/ROOT/Parquet files.

Existing v1.0.0 records and event outputs remain unchanged. New substantial runs use v1.0.1.
