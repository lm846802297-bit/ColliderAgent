# Stau CKKW-L normalization and jet-rate closure, 280/1 GeV

**Pass for this local development gate, not acceptance against ATLAS.** The archived 1,000 hard events were too small to validate the jet spectra near the merging scale. The independent 10,000-event hard sample passes the frozen local population and stability thresholds. Proceed to polarized decays of the matched sample and separate detector validation against the public two-SR cutflow; do not compute the three control regions or limits yet.

## Counting weights

For unit-weight LHE subrun k, use sigma_in,k / N_selected,k times the sum of final event weights, including zero weight after Sudakov veto. Use the total selected hard events, not the number satisfying the merging cut. Alternatively, estimate the hard cross section after the merging cut and multiply by the mean CKKW-L weight over the post-cut sample, including zero weights. Sum the six cross sections without sharing their denominators. [Pythia 8.317 main162](https://gitlab.com/Pythia8/releases/-/blob/pythia8317/examples/main162.cc) and the [Pythia CKKW-L manual](https://pythia.org/latest-manual/CKKWLMerging.html) define the single-pass and separate-weight conventions.

On the 1,000-event pilot, matched weights agree event by event whether included in Info::weight or recorded separately; the two normalization routes agree <2.1e-16 relative. Per-channel histogram bins integrate back to the matched rate. The original Info::sigmaGen after EOF can be stale: the 1k trial recorded up to 26.7% relative discrepancy. The [native ProcessContainer header](https://gitlab.com/Pythia8/releases/-/blob/pythia8317/include/Pythia8/ProcessContainer.h) and [Pythia driver](https://gitlab.com/Pythia8/releases/-/blob/pythia8317/src/Pythia.cc) show cached process-level summaries and skipped accumulation on no-emission failure. Do not use a universal last-accept rescaling: it fails a control. Native refreshed Pythia.stat tables agree to their printed precision in every affected class plus nominal controls (24 pilot, 9 independent). These witnesses are recorded in the endstat JSON.

## Jet distributions and independent hard seed

The second MG5 sample repeats the accepted generator setup with 10,000 events and random seed 266031; it is independent of the 1,000 hard events, not repeated showering. Retain the raw gzip digest from independent10k-hard.json. It is stored as a separate native artifact and is not duplicated in Git. The archived 1k raw file is in the preceding checkpoint. Pythia 8.317/A14 uses MPI off, primordial kT off, stable staus, and no hadronization for this check. The spectra use hadronic exclusive kT transition scales sqrt(d01), sqrt(d12), R=0.4, standard four-vector recombination over final light partons with |eta|<5. They are not detector jets.

At 20/30/40 GeV merging scales the independent sample gives 7.20991/6.90643/6.97255 fb. Relative to 30 GeV, the inclusive variation is at most 4.40%, and the largest near-threshold bin difference across the two kT transitions and tested scales is 17.2%. The smallest effective number in those bins rises from 7.34 in the pilot to 109.98 in the independent sample, above the frozen 25 threshold. These tests use one shower seed on the independent hard sample, three on the pilot; they are not a theoretical uncertainty estimate or ATLAS's NLO+NLL cross section. They do not calibrate detector response or certify jet distributions in the official sample.

## Replay from this directory

Supply the pinned Pythia environment from the stau-pp-lo checkpoint and include the sibling stau-atlas-ref280 directory in PYTHONPATH for the split utility. Run:

```sh
python closure.py ../stau-atlas-ref280/unweighted_events.lhe.gz > native-pilot.stdout
python extend.py > native-independent.stdout
python stat_replay.py closure-rows.json lhe-split > pilot-stat.stdout
python stat_replay.py independent10k-rows.json lhe-split-independent10k > 10k-stat.stdout
python check_stat.py closure-rows.json pilot-stat.stdout > pilot-endstat.json
python check_stat.py independent10k-rows.json 10k-stat.stdout > independent-endstat.json
python assess.py --native-stats pilot-endstat.json > summary.json
python assess.py independent10k-rows.json --native-stats independent-endstat.json > independent10k-summary.json
python -m unittest -v test_closure.py
```

The separate independent10k LHE must be hash-verified before running extend.py; its run template is included. Never combine the fitted ATLAS templates with these samples as independent predicted event yields.
