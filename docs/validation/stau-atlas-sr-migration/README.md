# Fixed-sample truth-filter and high-SR mT2 migrations

The (280,1) GeV nominal Delphes sample, 4,216 frozen CKKW-L matched events at 13 TeV and the original fb weights are unchanged. This is an event-level *diagnostic*, not ATLAS detector validation or a new official cutflow. We replay the same [cut definitions and detector output](../stau-atlas-detector-cutflow/README.md). The baseline was re-evaluated for every input, and all 18 original weighted rows replay to 2e-12 events tolerance. The same-event truth vectors and filter definitions come from [the previous audit](../stau-atlas-filter-response-audit/README.md).

## Does the upstream filter difference propagate?

The visible-momentum filter removes all and only 621 prior parent-pass events at the generator filter. Their original weighted yield is 139.89 events at 139/fb; none pass the existing reconstructed baseline, or any later cut. This is not an algebraic equivalence of definitions; it is verified only on this frozen sample and reconstructed configuration.

| Stage | Parent tau filter | Visible tau filter |
|---|---:|---:|
| Before filtering | 959.994 | 959.994 |
| After generator filter | 866.661 | 726.768 |
| Reconstructed baseline | 185.832 | 185.832 |
| Low final | 4.675 | 4.675 |
| High final | 16.624 | 16.624 |

The filter-only change *raises* the conditional reconstructed baseline fraction from 21.44% to 25.57% by shrinking the denominator; [ATLAS HEPData t17](https://doi.org/10.17182/hepdata.92006.v2/t17) gives 21.06%. Agreement at one row does not diagnose the next row. The ATLAS production configuration is not inferred from these numbers. No retuning or re-normalization is performed.

## Does high-SR mT2 input smearing alone close the excess?

For each of the 300 events contributing to high SR immediately before its massless mT2 cut, freeze all earlier cuts and weights. Both selected tau objects match distinct same-sign-to-truth visible hadronic tau candidates within Delta R<0.2 using pseudorapidity and wrapped Delta phi. Use the same [ATLAS massless mT2 definition](https://arxiv.org/abs/1911.06660v2) as the reference recast. Substitute only the tau inputs or only the missing transverse momentum vector, or both, in mT2. Earlier cuts, conditional efficiencies and object assignments use the original reco values and are not rerun with truth. Truth MET is the negative recoil represented by the sum of known invisible neutrino and neutralino transverse vectors; no correction is made to reco MET. All masks use a strict 70 GeV cut. Event migration counts are unweighted; efficiency columns use the frozen weighted pre-cut denominator.

| Inputs to mT2 only | Retention | Difference vs reco (pp, paired stat.) | Lost / gained |
|---|---:|---:|---:|
| Both reconstructed | 71.674% | 0 | 0 / 0 |
| True visible tau only | 71.389% | -0.285 +/- 0.939 | 4 / 3 |
| True invisible MET only | 71.512% | -0.162 +/- 0.554 | 2 / 1 |
| Both truth inputs | 71.792% | +0.118 +/- 1.157 | 6 / 6 |

ATLAS t17 gives 14.35/21.95 = 65.38% at this step. On this **fixed pre-cut sample**, changing the two mT2 inputs moves both ways and does not close the discrepancy. The result is compatible with the earlier cuts selecting a different ensemble or differing kinematics before reconstruction; it does not isolate those effects or test ATLAS object transfer functions. Near-cut results for a +/-10 GeV reconstructed mT2 band and full paired migration matrices are in the JSON. Unmatched candidates would be reported separately; there are none at this step. No control regions or limits are calculated. Priority is independent tau ID/trigger inputs and the pre-mT2 joint tau-MET distributions, not taking truth substitutions as signal-response corrections.

## Reproduction

```bash
bash run.sh DETECTOR_RUNTIME FILTER_AUDIT_DIR NOMINAL.root FROZEN.jsonl.gz NOMINAL_CUTFLOW.json result.json
```

The native ROOT and JSONL are inputs with pinned SHA-256 fingerprints. The existing cutflow, filter and response modules are required from their previous isolated run directories. Two runs regenerate byte-identical result JSON; three unit checks cover identity, unequal weights and cancelling migrations. The paired finite-MC error is based on event differences divided by the fixed weighted denominator, excluding detector and theory systematics.
