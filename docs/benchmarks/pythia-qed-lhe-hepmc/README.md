# Native Pythia QED FSR to HepMC3

The first 128 exact events from the archived [MadGraph muon-pair LHE](https://github.com/lm846802297-bit/ColliderAgent/blob/82176bc774410f07584a03adeccbc5673a7b57ea/docs/benchmarks/mg5-qed-lived-lhe/unweighted_events.lhe.gz) were read via the official [Pythia 8.317 Python distribution](https://pypi.org/project/pythia8mc/8.317.0/) after byte-exact gzip decompression, without stripping its warning bytes. Only the leptonic QED final-state-shower switch differed between the two runs. Both selected and accepted 128 events. Shower-off produced no photons; shower-on produced 125 photons in 79 events, including 67 events with a photon above 1 MeV. All stable photon statuses were native Pythia 51. These are sample counts for this specific seed, not precision predictions.

Both runs preserve the 8.6845 pb input normalization (negative-four LHE weight strategy and positive nominal event weights). Pythia stores the total cross section in mb; conversion to pb agrees to 2e-15 pb. The maximum post-shower momentum imbalance is below 1.24e-9 GeV. Opposite-sign stable muons and physical electron/positron beams were checked; the native shower uses physical lepton masses, whereas the archived hard process is massless. The [HepMC3](https://hepmc.web.cern.ch/) records use GeV/mm, beam status 4 and stable final status 1. Every projected momentum survives serialization and readback exactly in this run.

These files are a **one-vertex projection of the native beams and stable final particles**, not a complete shower genealogy or a detector event. The wheel has no built-in HepMC bridge; the writer and reader are the native HepMC3 bindings bundled in [Scikit-HEP pyhepmc 2.15.1](https://pypi.org/project/pyhepmc/2.15.1/). No ISR, MPI, decays, hadronization, detector simulation, or exclusion was run. Deliberately wrong HepMC units and corrupted input are rejected.

## Offline replay

Use CPython 3.12 on the compatible Linux platform and the two verified [wheel pins](wheels.lock), installed only into a temporary Python target. Set `PYTHONPATH` to that target and `PYTHIA8DATA` to its `share/Pythia8/xmldoc`. Download and hash-check the exact parent archive above. From a local copy of this benchmark:

```sh
mkdir -p replay
python shower_bridge.py /path/to/unweighted_events.lhe.gz "$PYTHIA8DATA" replay
cmp bridge_result.json replay/bridge_result.json
cmp qed_fsr_off.hepmc replay/qed_fsr_off.hepmc
cmp qed_fsr_on.hepmc replay/qed_fsr_on.hepmc
```

All three outputs matched byte-for-byte in separate runs in the pinned environment. No wheels or binaries are committed. See [Pythia event weight conventions](https://pythia.org/manuals/pythia8317/CrossSectionsAndWeights.html) for strategy −4 and [the Pythia shower manual](https://pythia.org/manuals/pythia8317/TimelikeShowers.html) for the lepton setting.
