# 13 TeV stau Born + PDF and native Pythia handoff

This is a **recast qualification checkpoint**, not the ATLAS signal model, detector efficiency or exclusion. Baseline: PhenoAgent's Born generator (commit `d18677905f635844f58cca4efb4e1d07d8f23170`); (m_stau,m_bino)=(400,80) GeV, unmixed stau eigenstates, prompt pure-bino Yukawa decays. Sources: [ATLAS, arXiv:1911.06660v2](https://arxiv.org/abs/1911.06660v2), §3.2; [LHAPDF 6 build instructions](https://www.lhapdf.org/install.html) and [CERN PDF grid](https://lhapdfsets.web.cern.ch/lhapdfsets/current/NNPDF23_lo_as_0130_qed.tar.gz); [Pythia TauDecays reference](https://pythia.org/latest-doxygen/classPythia8_1_1TauDecays.html). ATLAS used a different generator version, A14 and up to two hard extra partons with CKKW–L matching, and an external NLO+NLL normalization. None of those precision or multiplicity claims follows from this inclusive Born integrator.

## What was measured

- Native LHAPDF 6.5.5 evaluates central NNPDF2.3 LO member 0, with factorization scale fixed at 400 GeV. The two integration paths are direct x₁,x₂ on the physical support, and log τ,y with τ=x₁x₂ and y=(log x₁−log x₂)/2. The xfxQ API returns x f, not f. The 1/τ cancels the log-τ Jacobian only in the second path. Both beam orderings are included, all five light quark flavors, no photon channel. 24,48,96 point comparisons pass at the highest order.
- Native xfxQ includes tiny negative entries near x=1. In the positive event-generation mode only, explicitly clamp them to zero; the maximum per-state/flavor rate change versus unclipped native values is 1.63e−9 relative. This is documented generator policy, not a statement that the input grid is everywhere nonnegative. No extrapolation accepted.
- Weighted proposals from a fixed 16,384-point pseudorandom pool are resampled into 2,048 LHE events. The streams differ only in tau SPINUP, not momentum, IDs, or event weights. The LHE init normalization is the numerical integral, not the finite-pool estimate. Because some proposal points repeat this is a smoke-test stream, not a precision sample. Validate every hard and resonance vertex.
- For each chirality and charge, boost the exact spin axis from the scalar rest frame and sample the helicity using the longitudinal projection in the beam frame. The LHE SPINUP format carries this projection, not a full spin density matrix. Native Pythia 8.317.0 uses external SPINUP. Validate using tau→πν: with L/R and charge convention folded to a common sign, the analytic means for the almost-pure tags are close to +1/3, −1/3 and 0 for ordinary, flipped and absent labels. Isolate QCD ISR by disabling FSR, MPI and primordial kT in the four controls. A fifth run enables ISR/FSR/MPI and unforced tau channels (lepton QED shower and primordial kT still off); it is a stability smoke test, **not** validation of each decay mode or tau ID.
- These results do not establish the detector-level signal or control yields, systematics or matching uncertainties. Next: verify externally generated jet multiplicities, spin treatment and a detector response against an ATLAS validation point, then compare all five regions. No fit or exclusion is claimed.

## Replay

Environment: Python 3.12.14, NumPy 2.3.5, x86-64, G++ 14.2.0. Use the pinned tarballs and member-0 files listed in `source.sha256` and the exact PyPI Pythia8mc wheel in `wheel.sha256`. The wheel is installed with `python -m pip install --no-deps --target pythia-local WHEEL`; the sources/data are intentionally not redistributed. Build LHAPDF in the local directory with `./configure --disable-python --prefix="$PWD/../install"`, `make -j4`, `make install` from its extracted source directory. Extract the .info and member 0000 .dat directories beside these scripts.
From this directory, after verifying source and wheel checksums:

```sh
g++ -O2 -fPIC -shared pdf_bridge.cc -Iinstall/include -Linstall/lib -Wl,-rpath,'$ORIGIN/install/lib' -lLHAPDF -o pdf_bridge.so
export PYTHONPATH="../../../python-agent/tools:pythia-local"
export PYTHIA8DATA="$PWD/pythia-local/share/Pythia8/xmldoc"
python integrate_pp.py > pp-result.json
python make_lhe.py > lhe-result.json
sha256sum -c lhe.sha256
python shower_probe.py
python validate.py > validation-result.json
```

`lhe.sha256` records the regenerated full raw LHE files, not included in this checkout. `shower-result.json` is the raw replayable summary of the native Pythia runs, not a HepMC or detector record.
