# ATLAS 1ℓbb: cutflow yields to nominal HistFactory predictions

**Nine out of nine selected yields agree at their printed precision.** This compares separately published ATLAS cutflow tables to official workspace templates for the **same** analysis, mass points and exclusive bins. It also verifies the values that the native likelihood receives when only the signal-strength parameter changes. It does not combine ILD with ATLAS, generate detector-level ATLAS events, fit any data, or produce a limit.

- [ATLAS SUSY-2019-08, arXiv:1909.09226v2](https://arxiv.org/abs/1909.09226v2), Table 2 fixes the 13 TeV, 139 fb⁻¹ analysis and all three exclusive nonoverlapping mCT bins (the last includes overflow). [HEPData v4](https://doi.org/10.17182/hepdata.90607.v4) publishes the three representative mass points (300,75), (500,0), (750,100) GeV in the corresponding low-, medium- and high-mass signal regions. Use the final weighted selected yield of each cutflow, not the first raw generator row, a signal efficiency, or the post-fit background.
- [Official full likelihood, v4/r3](https://doi.org/10.17182/hepdata.90607.v4/r3), plus final cutflow tables [t42](https://doi.org/10.17182/hepdata.90607.v4/t42) through [t50](https://doi.org/10.17182/hepdata.90607.v4/t50). Exact download URLs and SHA-256 digests are in [input-lock.json](input-lock.json). The response uses native pyhf 0.7.6 at the workspace's suggested nuisance values, with its eight channels and measurements intact and the signal strength toggled 0→1. The three matched sets agree exactly with their respective original signal vectors in this environment.
- The [signed results](transfer_result.json) retain yield precision, bin identity and both comparison paths. The largest absolute selected-yield residual is 0.04873 events, under its 0.05-event tolerance. Tolerances came from half of the last printed decimal unit, not published statistical errors. All three deliberate low/high bin swaps were rejected.

To replay offline, obtain each official input from its locked URL under the exact filename listed in [input-lock.json](input-lock.json), use CPython 3.12 and the [pinned pyhf runtime](https://github.com/lm846802297-bit/ColliderAgent/blob/2fe73292c5549ff4063cdc9135a71e123955646d/docs/benchmarks/one-bin-histfactory-native/replay-wheels.txt) with the NumPy/SciPy versions in the manifest, then run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python transfer.py /path/to/official-inputs > replay.json
cmp transfer_result.json replay.json
```

No experiment files or Python wheels are repackaged here. Passing this bridge validates nominal selected-yield transfer for nine official cells; it does not validate an experimental recast, signal uncertainties, treatment of other benchmark masses, or projected limits.
