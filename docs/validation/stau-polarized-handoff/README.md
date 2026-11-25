# Matched stau sample: frozen hadronization and polarized tau handoff

Scope: local native event interface, not an ATLAS detector prediction. Exact hard input is the independent 10k reference from CKKW–L closure (SHA-256 614ba091937eb45849dd0c9dcc20267280c0f962fe4265f9e5224c6e2812b4cb), nominal 30 GeV and Pythia seed 41324 per process. The six classes carry their own raw cross sections and selected-event denominators. Retain only positive matching weights, with no unweighting or rescaling to ATLAS.

The pinned closure runner is used without physics changes; only a callback is injected at a known source hash and at a unique marker after calculation of jet transitions. First replay the undecayed stream. A second native pass isolates forced hadronization from the shower RNG by saving and restoring its state. Runtime acceptance requires the same selected LHE index, full pre-hadron final-state momenta/IDs, jet transitions, event weight and per-class cross section. The event key combines process ID and the 1-based selected index in its split LHE, not final output row position.

Staus decay isotropically to tau and bino in their rest frames. For the pure bino coupling, the tau polarization magnitude there is sqrt(lambda)/(m_stau^2-m_tau^2-m_bino^2); chirality supplies sign and charge conjugation flips helicity. A separate native Pythia 8.317 tau gun uses TauDecays:mode=3 and independent event-local seeds. Decay products are rotated from the gun's z axis to the physical spin axis in each stau rest frame, then boosted together to the lab rather than assigned lab helicity. Pion-only replicas with normal, reversed and zero polarization use the same matched particle kinematics; the main recorded sample uses unforced tau channels. Visible and invisible daughter momenta reproduce the stau and tau parents. See the [Pythia 8.317 decay rules](https://gitlab.com/Pythia8/releases/-/blob/pythia8317/share/Pythia8/xmldoc/ParticleDecays.xml).

The separately stored raw gzip stream is a weighted particle-level JSON Lines projection. Each four-vector is (px,py,pz,E) in GeV. Preserve event_id, weight_fb, parents, tau daughters, neutralinos and other final particles through conversion. It is not a HepMC history or detector output. The detector adapter must reconstruct explicit tau relationships and keep all stable particles (including the invisible ones) accounted for. No ATLAS yield tuning, trigger acceptance, three control-region templates or limit.

## Replay

Use the pinned Pythia 8.317 wheel and the same environment as the stau-pp-lo checkpoint. Set PYTHONPATH to include the wheel target and sibling stau-atlas-ref280 directory for the split helper. Put the hash-verified 10k hard artifact beside closure.py and the independent run rows within the closure directory. For the complete positive-weight sample:

    python freeze.py --archive ../stau-merge-closure --per-channel 0 --output stau-ref280-tms30-polarized-events.jsonl.gz > native.stdout
    python verify.py stau-ref280-tms30-polarized-events.jsonl.gz ../stau-merge-closure/independent10k-rows.json
    python -m unittest -v test_freeze.py

The pilot subset is not a normalized full sample. For full-sample normalization, zero-weight and vetoed hard events still enter each class's denominator.

Full execution: 4,216 unique positive-weight events (8,432 tau decays), total 6.906428701209656 fb unchanged from the nominal validated matching ledger in all six classes. The mass-shell and 13 TeV total four-momentum checks pass independently. Pion angular means folded by production chirality are +0.32702, -0.34190, -0.00523 with nominal, reversed, and zero polarization, respectively; separate native tests cover each charge. The raw event stream size is 19,388,325 bytes and its SHA-256 is recorded in both JSON reports. Retain the file under its original basename in native artifact storage; do not transform to a compressed set of summary yields. No ATLAS SR or CR events calculated.
