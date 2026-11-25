# ATLAS SUSY-2018-04: native detector and two-SR cutflow diagnostic

This run uses the same frozen (280 GeV stau, 1 GeV neutralino), 13 TeV sample throughout. It runs *actual Delphes*, not an ATLAS detector simulation, on the exact 4,216-event [HepMC3 handoff](../stau-hepmc-handoff/README.md), then applies cutflow order from [HEPData v2 Table 17](https://doi.org/10.17182/hepdata.92006.v2/t17). No generation or decays were rerun, and ATLAS event yields are only comparison targets. This is **not** a passing two-SR validation. No control regions or experimental limit were calculated.

## Result and earliest disagreement

| Checkpoint | This run | ATLAS |
|---|---:|---:|
| Generator filter conditional efficiency | 90.28% | 76.28% |
| Baseline efficiency conditional on filter | 21.44% | 21.06% |
| Medium OS and third-tau veto conditional on baseline | 45.56% | 55.12% |
| Low-mass SR: MET window survival | 33.45% | 38.98% |
| Low-mass SR: tight-ID step survival | 62.44% | 68.88% |
| Low-mass SR final events | 4.68 ± 0.49 | 6.08 ± 0.79 |
| High-mass SR: final mT2 step survival | 71.67% | 65.38% |
| High-mass SR final events | 16.62 ± 1.19 | 14.35 ± 1.13 |

The nominal analysis uses the original matched 6.9064287012 fb times 139/fb (959.99 total events) rather than rescaling to HEPData (1147.71 total). All quoted errors are finite-sample statistical estimates as documented in the raw rows, not detector systematics. After dividing by each prediction's own prefilter total, final acceptance times efficiency is 0.487% vs 0.530% in low and 1.732% vs 1.250% in high (approximately -8% and +39%). On alternative detector seeds the same event sample gives low 4.77–5.42 and high 15.66–16.91; this is a detector RNG sensitivity on the same events, not independent samples. A coarse absolute yield screen passes both *final rows*, but four intermediate low rows fail. Final yield proximity is partly a compensation between efficiency and differing input cross sections. Neither fast-sim calibration nor nominal 30 GeV matching parity with the ATLAS setup is established.

The earliest disagreement precedes detector simulation, in the truth tau pT/eta filter. Isolate the generation composition and matching prescription before attributing later differences to detector response alone. The sizeable conditional losses at the medium selection and low MET window, and excess high mT2 acceptance, indicate which object-level comparisons to do next; they are not a determination of the causes.

## Frozen response

- [ATLAS article (v2)](https://arxiv.org/abs/1911.06660v2), pp. 5–8, and HEPData t17. Generator filter uses both parent tau momenta, pT>15 GeV and |eta|<2.6; it is not inferred from ATLAS event counts. Baseline uses native truth-matched tau reconstruction with 50/40 GeV thresholds as a proxy for the public loose BDT criterion. Medium OS, no third baseline tau, b veto, light-lepton veto, m(tau,tau)>120 GeV; then region-specific trigger, MET, tight ID, angular cuts and the massless mT2 definition on p. 8. Thresholds are strict. Delta R uses rapidity as in the ATLAS definition; geometric matching uses eta.
- [Authors' deposited Delphes recast](https://doi.org/10.14428/DVN/UN3NND), [public card file 1579](https://dataverse.uclouvain.be/api/access/datafile/1579). Only fixed random seed and the truth output branch are added; detector modules are unchanged. The companion MA5 C++ selection was consulted, **not run**; in particular, its unit weight override and yield-derived reweights were not used.
- Apply published medium/tight efficiencies per reconstructed prong and 95% per tau electron rejection from paper p. 6, assuming independent tau responses. Tight is conditional on medium. Trigger probability is 0.775 at plateau, the midpoint of the stated 75–80% range, with separate 2015–17 and 2018 thresholds combined with luminosity weights 80.5 and 58.5/fb. These are probabilities, not a post-selection rescale. There is no calibrated prong/eta-dependent ID uncertainty or trigger decision matching.
- The deposited response uses calorimeter-tower MET, not full ATLAS object/track-soft-term MET; implements neither detailed BDT efficiencies, pileup nor fake taus. The event handoff did not preserve hard parton/heavy-hadron ancestry or decay positions for non-tau objects, so b-flavour tagging and displacement-dependent efficiencies cannot be established. Electron/muon isolation and overlap removal are approximated. The two zero-energy photons are untouched in the input; the Delphes propagator drops transverse momentum squared below 1e-9 GeV² before propagation. Never reinterpret these approximations as the official response.
- All 4,216 ROOT entries rejoin the exact double-precision input weights by immutable event IDs. The Delphes float weight is separately checked (relative error below 6e-8), not used for normalization. Tau daughter counts, signs and native serialized four-vectors were rechecked at 8,432 tau vertices; the low/high final regions are disjoint. Nominal analysis replay reproduced identical JSON; the companion seeds preserve identical hard sample. The nominal ROOT file is kept privately; public source and comparison summaries below do not include event payloads.

## Reproduce

Use Delphes 3.5.1 commit `28658365abeb71ee36dfc739f9670c1514c0cb10` from the official repository, ROOT 6.38.00 (official PyPI alpha wheel `root==0.1a10` used for this diagnostic), Python 3.12.14, GNU C++ 14.2.0 and `mt2==1.3.1`. Source and card fingerprints are pinned in `inputs.json`. With the wheel under `runtime` and mt2 under `mt2-runtime`, and after building `DelphesHepMC3 libDelphes.so`, place the generated `*Dict_rdict.pcm` beside the binary. The run scripts set the local ROOT include/lib search paths. The executable and shared library use the unchanged upstream physics source. Run from a fresh directory with no existing detector ROOT output:
    
```bash
python prepare_cards.py recast-1579
for seed in 34025 34026 34027; do
  bash run-native.sh "$seed" INPUT.hepmc
  bash run-cutflow.sh "$seed" FROZEN.jsonl.gz ATLAS-T17.json
done
python summarize.py
PYTHONPATH=runtime:mt2-runtime python -m unittest -v test_cutflow.py
```

The table in `comparison.csv` contains all 18 numerical steps, totals, statistical errors, conditional and absolute efficiencies and alternate-seed span. The count variance proxy is sum of squared selected event contributions (fractional expected efficiencies); it excludes unmodelled detector and theory systematics. Four unit checks cover angular wrapping, analytic balanced massless mT2 with zero upstream momentum, the strict MET trigger bound and medium/tight nesting. The numerical screen in the task brief is diagnostic only. Before control regions, require an independently verified acceptance description of the generator filter and transfer/response validation for the two SRs, not a baseline reweight.
