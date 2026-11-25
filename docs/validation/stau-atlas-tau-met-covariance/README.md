# Correlated tau–MET response on frozen stau events

## What ATLAS measures

The stau search combines calibrated transverse momenta of jets, tau candidates and other identified objects with a primary-vertex track soft term not used by those objects ([SUSY-2018-04, section 4](https://arxiv.org/html/1911.06660v2#S4)). This is not the native tower-sum MET of the recast card. The later full-Run-2 [ATLAS JETM-2020-03 study](https://arxiv.org/html/2402.05858v2) gives the relevant definitions and explicitly resolves shared object signals to avoid double counting (section 6). Its response comparison in Fig. 7 is PFlow MC in W and top samples; its soft-term uncertainties in Figs. 13/19 (PFlow/EMTopo) are from Z->ee and are uncertainties on soft-term response/resolution, not a 2x2 tau–MET response for stau. These public benchmarks can test ingredients in matching control samples, not provide the signal covariance or an absolute rescale. The public [SimpleAnalysis MET significance note](https://cds.cern.ch/record/2839789/files/ATL-PHYS-PUB-2022-045.pdf) describes an object-resolution model; significance and the joint signal transfer function are different observables.

## What this fast-sim sample shows

Keep the same nominal 4,216 events and all physics weights for each of the three previously archived detector seeds. Under frozen common selections, all 707–708 contributors per seed have two uniquely identified visible, hadronic truth taus matched to the same-charge reconstructed candidates within Delta R<0.2. Let x be the vector sum of the two reconstructed-minus-visible-true tau momenta, and y be reconstructed tower MET minus the true invisible momentum sum, all in the transverse plane. Project both on the truth MET vector and its signed perpendicular; also store three truth MET bins in the JSON.

| Delphes seed | rho(x,y), parallel | rho(x,y), perpendicular | sigma parallel y -> y+x | sigma perpendicular y -> y+x |
|---|---:|---:|---:|---:|
| 34025 | -0.758 | -0.781 | 13.69 -> 9.08 GeV | 14.37 -> 9.05 GeV |
| 34026 | -0.701 | -0.848 | 13.27 -> 9.96 GeV | 14.76 -> 7.86 GeV |
| 34027 | -0.726 | -0.813 | 13.09 -> 9.31 GeV | 16.51 -> 9.62 GeV |

These are weighted centered widths, covariances and correlations, not independent random smearing widths. The three seeds repeat detector stochastic response on the same truth sample, not independent signal samples. The negative association is consistent with shared calorimeter inputs and transverse momentum balance. We explicitly check var(x+y) = var(x)+var(y)+2 cov(x,y), then recover the same component by separately adding x to the MET vector (closure below 1e-11 GeV). Do not neglect this term merely because marginal widths have been tuned.

## How much does the explicit balance probe change a window?

Use y+x only as a diagnostic: it pretends to replace the two tau momenta in the balance while leaving the rest of the detector event unchanged. The tower sum is not an ATLAS object-association map, so adding x is not an ATLAS recalibration or evidence for a measured resolution. Hold upstream weights and reconstructed candidate masks fixed. For low mass use the original low trigger before the MET window. For high mass use the original luminosity-weighted tau-only thresholds *before* the MET gate, not a sample already selected on MET. Neither side applies this probe to the final limit or cutflow.

Nominal seed: low 75–150 GeV retention 33.456% -> 34.079% (+0.623 +/- 1.019 pp paired finite-MC), high >150 GeV 45.303% -> 44.222% (-1.081 +/- 0.724 pp). Across the original seeds the low shift spans -1.30 to +0.62 pp and the high shift -1.08 to -0.57 pp. The nominal low row remains well below the reported 38.98% benchmark. This correlated balance study affects widths more than the integrated windows in the present fast-sim sample; it does not establish that other ATLAS soft-term, object association or acceptance effects are small. No rate retuning, no control-region yields and no limit.

## Replay

Use the frozen three ROOT hashes, JSONL, and prior analysis and migration code. Paths are arguments in order: detector runtime, filter audit, migration audit, frozen truth, output JSON. Two exact byte replays and two deterministic tests are required.

```bash
bash run.sh DETECTOR_RUNTIME FILTER_AUDIT MIGRATION_AUDIT FROZEN.jsonl.gz result.json
```
