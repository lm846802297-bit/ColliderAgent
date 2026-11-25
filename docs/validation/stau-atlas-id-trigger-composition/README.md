# Fixed stau sample: which events pass tau identification and trigger?

This is a composition diagnostic on the same 4,216 matched events and nominal Delphes record at (280, 1) GeV, not a refit or ATLAS detector calibration. The eighteen previously archived absolute cutflow rows replay within 2e-12 events. Original event weights, detector kinematics, object selections, and the final 70 GeV mT2 cut did not change. The table compares **conditional distributions** normalized to each indicated stage, with the same underlying samples. For the trigger-era split, apply the separate threshold masks to the same common-selected sample; a constant HLT plateau efficiency cannot reshape distributions.

| Diagnostic on fixed recast | Before -> after | Paired difference (percentage points) |
|---|---:|---:|
| Medium identification + OS/third-candidate selection: fraction above mT2 70 GeV | 54.11% -> 54.08% | -0.03 +/- 0.33 |
| Low trigger: fraction in MET 75–150 GeV | 34.63% -> 33.46% | -1.17 +/- 1.14 |
| Low trigger thresholds, early vs late era: fraction in MET 75–150 GeV | 33.70% -> 33.04% | -0.67 +/- 1.02 |
| Low tight identification after MET window: fraction above mT2 70 GeV | 56.51% -> 56.50% | -0.01 +/- 0.13 |
| High MET plateau requirement alone: fraction above mT2 70 GeV | 50.96% -> 70.55% | +19.59 +/- 2.19 |
| Full high trigger selection: fraction above mT2 70 GeV | 50.96% -> 70.64% | +19.69 +/- 2.19 |
| High tight identification: fraction above mT2 70 GeV | 70.64% -> 70.60% | -0.038 +/- 0.016 |

The uncertainties are finite-sample estimates for the paired normalized differences, grouping by the same input event and not by separate independent stages; they are **not** detector systematics. Probability weights give fractional contributors; the raw nonzero contributor count is not a predicted count.

- The medium+OS/third selection shifts the fraction with two reconstructed one-prong candidates from 58.34% to 64.39%, while it hardly shifts mean leading/subleading tau pT or the mT2 spectrum near 70. The implemented medium/tight proxy uses only reconstructed track multiplicity plus the fixed electron-veto probability. The result does not imply actual ATLAS ID cannot affect shapes.
- The low trigger hardens both tau objects: the subleading mean goes from 112.76 to 136.57 GeV; the late 75 GeV (rather than early 60 GeV) threshold reduces eligible raw contributors from 537 to 439 at fixed common selections. It changes the MET-window fraction by just about half a percentage point. This is insufficient as the sole explanation for the gap to the [t17 conditional window fraction](https://doi.org/10.17182/hepdata.92006.v2/t17), 38.98%. The HLT turn-on and actual period/object correlations are not modeled by this exercise.
- High SR is strongly sculpted by requiring MET>150 GeV **before** the mT2 cut. Almost all of its +19.69 pp enrichment is already present with MET alone; imposing the additional high trigger tau thresholds changes that by about +0.10 pp. Compare the **joint** MET/mT2 population, not an isolated mT2 smearing tweak. The ATLAS final conditional fraction (65.38%) is after angular cuts, so it must not be compared directly to the 70.64% trigger-stage diagnostic. The nominal immediate pre-cut fraction after angular cuts is 71.67%. Without an independent, matching stage ATLAS response or joint upstream distribution we cannot assign the discrepancy to a particular transfer function.

The reported means and reconstructed-prong composition are in populations.json. Each CSV carries variable names, lower/upper bin edges (left inclusive), contributor counts, weighted fb and normalized fraction. Zero-weight cells are omitted; the recorded overflow bins retain all weight. The joint distributions (subleading tau pT–MET and mT2–MET) and the one-dimensional distributions conserve each stage's weight. Neither signal region is marked validated; no control regions, limit, or fit.

## Replay

Use the unchanged nominal detector and filter-audit environments. The required module imports are from those two prior directories. No detector or generator is rerun for this calculation.

```bash
bash run.sh DETECTOR_RUNTIME FILTER_AUDIT_DIR NOMINAL.root FROZEN.jsonl.gz NOMINAL_CUTFLOW.json OUTPUT_DIR
```

The two output runs were compared byte-for-byte. Two separate unit checks cover strict era/trigger thresholds and the invariance under common-weight rescaling of a paired normalized difference.
