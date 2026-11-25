# ATLAS stau validation: native HepMC3 detector handoff

This gate transports the frozen 13 TeV (280, 1) GeV mixed left/right stau calibration sample to a standard event format. It consumes the exact gzip of the polarized TMS=30 GeV, Pythia seed 41324 run from [the previous gate](../stau-polarized-handoff/README.md). No generation, re-showering, tau redecay, event filtering or experiment normalization is performed.

Each HepMC3 ASCII v3 event preserves its class and one-based LHE selection index in both an attribute and the integer `10000*class+index`. The single named weight `matched_xsec_fb` is a per-event cross-section contribution, not a dimensionless generator weight. Sum weights over a selection and multiply by the luminosity in inverse fb for a weighted count; do not divide by the number of events. Jet transition scales are in GeV. Status-4 nominal proton beams anchor one projected primary vertex. Status-2 staus and taus carry explicit signed ancestry to stable products, including both neutralinos and all neutrinos (status 1). The graph has five vertices per event, but does not reconstruct generator ancestry for the other hadrons, partons, or physical decay positions. All vertices have zero position in mm; do not use this file for displaced decays or impact-parameter validation. The original record contains two exact zero-four-vector photons at 1:964 and 3:110; retain them exactly for reversible transport, and exclude them as nonphysical inputs to any kinematic reconstruction that divides by their momentum. A detector must classify PDG ±12/14/16 and 1000022 as invisible, with no double counting of status-2 taus.

Native HepMC 3.02.05 via [pyhepmc 2.15.1](https://pypi.org/project/pyhepmc/2.15.1/) writes and reads GeV/mm with 17-digit momentum precision. Python 3.12.14 on Linux x86-64, NumPy 2.3.5 and packaging 26.3 were present; the official CPython 3.12 x86-64 wheel was checked against PyPI release metadata before isolated installation (SHA-256 `d6a62304979717d51048dd1bf2d415ebc1e5c3efc7d523a2dada6706a75d777f`). HepMC3 serializes the input identity and stable state; the independent stdlib parser checks all event IDs, units, weights and stable-PID/four-vector multisets directly in ASCII rather than using the HepMC API.

- Frozen input: `stau-ref280-tms30-polarized-events.jsonl.gz`, SHA-256 `ac20e8b056e16b98b19d566dc683f9658277393f321b21c864cc38241ea1614e`.
- Output, uncompressed: `stau-ref280-tms30-polarized.hepmc`, 68,770,417 bytes, SHA-256 `33ea082ce28778eb99cdc7219730a69e9c8278021bd7f28f0d588c1764d3317a`. Second invocation regenerated identical bytes and report. Its `gzip -n` transport copy is 26,179,065 bytes, SHA-256 `88108e98f8c8beda2ba2913e9057b4d4bdb6f2f05f48b3cd92ba89f901e8c1c1`, retained privately.
- 4,216 events, 8,432 signed stau vertices, 8,432 signed tau vertices, 476,355 stable particles. Total weight 6.906428701209656 fb before any detector selection. The stable momenta and per-event weights match exactly. The maximum global momentum-component imbalance relative to the nominal beams is 0.0169 MeV, inherited from the input at hadronization; no momentum repair was applied.
- Six unit checks include altered weight, event ID, tau ancestry, charge tag and a duplicate particle, all rejected. Detector/recast and ATLAS SR cutflows remain NOT RUN. No CR inputs or limits were inferred.

```sh
python -m unittest -v test_transport.py
python transport.py INPUT.jsonl.gz first.hepmc first.json
python audit_ascii.py INPUT.jsonl.gz first.hepmc ascii.json
python transport.py INPUT.jsonl.gz second.hepmc second.json
cmp first.hepmc second.hepmc
cmp first.json second.json
```

Proceed to the public ATLAS SUSY-2018-04 detector/recast response. Validate the `(280,1)` two signal-region cutflows separately, including object, MET and tau identification and trigger definitions, without calibrating yields to the ATLAS baseline. Three control regions and a limit are downstream of those gates.
