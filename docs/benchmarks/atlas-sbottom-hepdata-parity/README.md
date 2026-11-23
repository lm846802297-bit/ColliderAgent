# Preserved ATLAS sbottom likelihood: a two-point pyhf benchmark

**Result:** pyhf 0.7.6 reproduces the older published pyhf reference on two exact RegionA patches, to an overall maximum residual of 1.70e-6 (predeclared absolute tolerance 5e-4). At nominal signal strength 1, the observed CLs values are 0.24443572887286977 and 0.04076573157590668. The first point's five expected bands also match the published FAIRS-HEP reference. The second point's expected bands appear in the native output for replay only; there is no benchmark target for them. This verifies treatment of a preserved workspace with 6 bins and 63 free nuisance parameters; it does not validate new limits, event generation or the paper's observed/expected contour.

- Public inputs: [HEPData resource, DOI 10.17182/hepdata.89408.v1/r2](https://doi.org/10.17182/hepdata.89408.v1/r2), from [the ATLAS sbottom search](https://doi.org/10.1007/JHEP12(2019)060). Fetch the original version; later revisions, regions and file names are not interchangeable.
- Reference values, acceptance thresholds and exclusions are fixed in [the task brief](TASK_BRIEF.md). The cited talks report pyhf reference implementations, not independent statistical or experimental point estimates.
- Replay uses a preverified pyhf 0.7.6 environment as pinned in the [parent wheel manifest](https://github.com/lm846802297-bit/ColliderAgent/blob/2fe73292c5549ff4063cdc9135a71e123955646d/docs/benchmarks/one-bin-histfactory-native/replay-wheels.txt), with Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. The archive remains at HEPData; the code rejects any non-identical archive before reading exact named regular files as data.
- Official pyhf CLI and API produced exactly equal numeric results for all twelve outputs. They share the same library and are not independent algorithms. A mutated archive is rejected. This archive also records a byte-identical offline replay of the API result in the same environment; floating-point byte equality is not promised on other platforms.

From the repository root, with the cited Python environment active and the original archive available locally:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/atlas_sbottom_hepdata_parity.py HEPData_workspaces.tar.gz > replay.json
cmp replay.json docs/benchmarks/atlas-sbottom-hepdata-parity/native_pyhf.json
```
