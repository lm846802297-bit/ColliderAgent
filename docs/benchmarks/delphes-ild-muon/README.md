# Delphes ILD central-muon response on the archived shower sample

Real [Delphes 3.5.1](https://github.com/delphes/delphes/tree/28658365abeb71ee36dfc739f9670c1514c0cb10) read the [128-event Pythia FSR-off HepMC sample](https://github.com/lm846802297-bit/ColliderAgent/blob/8158d025024363f3870bd0c334a8a19ddc7d2104/docs/benchmarks/pythia-qed-lhe-hepmc/qed_fsr_off.hepmc) and wrote 128 ROOT entries. It reconstructed 237 muons. In the prespecified central sample, 117 of 122 truth muons were matched (95.90%), consistent with the [stock ILD card](https://github.com/delphes/delphes/blob/28658365abeb71ee36dfc739f9670c1514c0cb10/cards/delphes_card_ILD.tcl)'s 0.99×0.95=94.05% model (+0.865 binomial standard errors). The independently standardized log-pT residual has mean 0.00622 and RMS 1.0271. Charge and native truth references agree; maximum native truth input component difference is 1.87e-6 GeV and maximum central angular difference is 1.16e-7.

This tests the card's isolated central muon parameterization, not ILD or detector performance, hadronic recoil, detector uncertainties or data agreement. The input is a one-vertex stable truth projection, with no shower photons, hadronization or pile-up. The official card was untouched; the wrapper only pins the seed. The independent verifier takes truth from HepMC ASCII and matches the native ROOT truth references by charge/event. It uses the original [MomentumSmearing log-normal transform](https://github.com/delphes/delphes/blob/28658365abeb71ee36dfc739f9670c1514c0cb10/modules/MomentumSmearing.cc) with the card's central pT resolution. The central selection avoids efficiency and resolution boundaries.

## Replay

The [CERN ROOT CPython wheel](https://root.cern.ch/getroot/) is explicitly alpha and used only for this local test. See [the run manifest](run_manifest.json) for the exact wheel and headers. In scratch, unpack the verified wheel to `deps`, check out Delphes at the pinned commit in `dd`, and use GCC/G++ 14.2.0. Set shell variables from the scratch directory:

```sh
top=$PWD
r=$top/deps/ROOT
mkdir -p "$r/mock_site_packages"
ln -s ../ "$r/mock_site_packages/ROOT"  # relocation layout expected by root-config in this wheel
export PATH="$r/bin:$PATH" ROOTSYS="$r"
export ROOT_INCLUDE_PATH="$top/dd:$top/dd/external"
export LD_LIBRARY_PATH="$top/dd:$r/lib:$top/deps/root.libs"
export PYTHONPATH="$top/deps"
(cd dd && make -j3 DelphesHepMC3 libDelphes.so ClassesDict_rdict.pcm ExRootAnalysisDict_rdict.pcm ModulesDict_rdict.pcm FastJetDict_rdict.pcm)
```

Put the benchmark's `seed_wrapper.tcl` and the exact parent `parent.hepmc` in a sibling directory `run`, then run `../dd/DelphesHepMC3 seed_wrapper.tcl delphes.root parent.hepmc` from there. Pass the input, ROOT file and `dd/libDelphes.so` to `check_response.py`. This reproduces [the response summary](response.json) and full checked truth/reco physics payload SHA-256, not the raw ROOT UUID and timing metadata. The archived ROOT file is the actual first validated output, not a rebuilt substitute. Building only the reader target omits required dictionaries; use the complete target list above. No packages or executables are archived.
