# ATLAS (280,1) GeV: separate generator-filter definition and detector response

Reuse the exact frozen 4,216 matched events and the existing nominal native Delphes run. Do not choose either filter by agreement with the experiment, change the previous cutflow, reweight the signal, or run the three control regions.

## Generator filter

[ATLAS HEPData v2 Table 17](https://doi.org/10.17182/hepdata.92006.v2/t17) specifies two tau leptons, each with pT>15 GeV and |eta|<2.6, but its table caption does not distinguish pre-decay and visible four-momenta. Its weighted fraction is 875.46/1147.71 = 76.279%. The general [ATLAS Athena TauFilter implementation](https://gitlab.cern.ch/atlas/athena/-/blob/41da040949efeca5de0e5adbd84054868a5165c6/Generators/GeneratorFilters/src/TauFilter.cxx) explicitly subtracts daughter neutrinos and has independent configurable electron, muon, and hadronic thresholds. CERN API cross-checked exact source SHA-256 99b1112d9ca994bc705a9b0091726b00cc4905561a3924f676a8effca57d7c0a. This is evidence for a realistic visible-tau interpretation, **not identification of the historical job configuration for the published samples**.

| Same sample, original weights | Fraction |
|---|---:|
| Pre-decay tau momenta, any decay mode | 90.278% |
| Visible decay products summed, any decay mode | 75.706% |
| Pre-decay tau momenta and both taus decaying hadronically | 39.425% |
| Visible decay products and both taus decaying hadronically | 36.708% |

Changing only the four-vector definition removes 621 events from the original pass set (none migrate in here). Weighted drop is **14.572 ± 0.565 percentage points** using a paired event-level finite-MC estimate with fixed production weights. The visible result is 0.573 percentage points below the paper's weighted value. Summing visible daughter momenta gives the same classification as subtracting invisible momenta from the parent for all 8,432 tau decays. No published value enters the selection. The t17 reference is outside these calculations and is hash-checked before comparison. In these two modes the six hard classes use odd IDs for left-handed stau, even IDs right-handed, and 0/1/2 additional matrix-element partons; the last descriptor is not reconstructed jet multiplicity.

A composition-only counterfactual applying the rounded paper L:R cross sections 5.8:2.2 fb to the two separately computed efficiencies raises the parent value by 0.025 pp (visible by 0.023 pp), insufficient to explain the original gap. Across the existing 0/1/2 additional-parton classes the parent filter grows from 88.88% to 93.30%; visible grows 73.68% to 79.45%. Varying all the weights among those three frozen classes alone cannot reach 76.28% under their parent definition; that does not bound genuine changes to within-class spectra, generator version, ME–PS merging, or tau modeling.

## Existing detector response as a same-event diagnostic

The nominal ROOT has identical frozen event IDs/weights, not retuned events. For the 537 contributors to the previous low-SR trigger row, hold that row and all object selections fixed; only substitute true invisible missing transverse momentum for the recast tower MET in the 75–150 GeV window. Retention changes **33.456% → 33.903%** when replacing reconstructed by truth, a paired difference of **−0.447 ± 1.260 pp** for reco minus truth; **7.618%** of the weighted sample migrates into or out of the window, with partial cancellation. The unchanged ATLAS row is **38.983%**. The net effect of this particular detector simulation’s tower smearing does not account for the full conditional gap with all other selections held fixed. It does not calibrate ATLAS's object/track-soft-term MET, or quantify the effect of jointly changing objects and MET. Independent tower-vector summation closes to 0.184 MeV in each tested component; the truth-invisible MET uses neutralinos and neutrinos exactly once.

For truth hadronic tau visible vectors in the stated fiducial region, the matching diagnostic requires an existing reconstructed, same-charge candidate within Delta R<0.2, including reconstruction/track/overlap cuts before the paper's medium and tight probability. In true pT bins 20–50, 50–100, and >=100 GeV, weighted matched fractions are **84.8%, 85.4%, 84.9%**, while matched mean reconstructed/visible pT ratios are **1.124, 1.060, 1.025**. The ratio is selection-conditional and affected by threshold migration, so it is not an ATLAS energy-scale bias. There is no in-data tau efficiency validation in this check. No SR is declared validated.

## Replay

Use the prior run's exact handoff and t17 input. `response_audit.py` also uses its frozen ROOT output and cutflow implementation (place `cutflow.py` next to that installed detector runtime as in the prior run). The three arguments after the detector-runtime directory in the response command are actual file paths.

```bash
python -m unittest -v test_filter_audit.py
python filter_audit.py FROZEN.jsonl.gz ATLAS-T17.json result.json
bash run-response.sh DETECTOR-RUNTIME detector-34025.root FROZEN.jsonl.gz response-result.json
```

Both JSON payloads replayed byte-identically. Four unit tests cover strict boundaries, a visible-only threshold difference, momentum conservation rejection and weighted acceptance. See [previous detector gate](../stau-atlas-detector-cutflow/README.md) for environments, hashes, and two SR stopping conditions. If the original generator job options surface, verify the exact thresholds and tau types before changing the production cutflow. In parallel, seek independent ATLAS tau ID/trigger and MET response information without fitting to the signal-region totals.
