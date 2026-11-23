# MadGraph LHE to truth-level cutflow

Compiled MadGraph5_aMC@NLO v3.5.17 produced 5,000 unweighted parton-level events for massless e⁺e⁻ → γ* → μ⁺μ⁻ at 100 GeV. The integrated cross section was **8.684500 ± 0.003851700 pb**, vs. **8.685447567 pb** from the independent Born QED formula. The absolute difference is 0.000947567 pb (0.246 integration standard errors). The independent LHE reader checks particle IDs, mass shell and momentum conservation in every event; all pass. The `|cos θ| < 0.8` truth-level cut retains **3,671 / 5,000 (73.42%)** vs. the analytic **72.8%** (+0.99 binomial standard errors), where θ is measured from the incoming electron to the outgoing negative muon. The fiducial cross section is 6.3761599 pb before any shower/detector selection.

The [official source tag](https://github.com/mg5amcnlo/mg5amcnlo/tree/4492b3e392effbb650447763fef5f67700673f03) includes `bin/create_release.py`, so the program itself prints a development/not-for-production warning. This is a diagnostic of the pinned source, not a qualified production release. The unchanged generator gzip includes all native process/run/SLHA cards and its original event payload. The embedded process card includes four red ANSI warning lines; raw LHE digest and normalized reader-view digest are explicitly distinct. The offline reader removes only eight known ANSI tokens in that one process card before standard XML parsing. A truncated file, a changed outgoing PDG code, and ANSI injected inside an event were each rejected. There is no global stripping or rewriting of the archived native gzip.

## Replay

Use the exact [MadGraph source](https://github.com/mg5amcnlo/mg5amcnlo/tree/4492b3e392effbb650447763fef5f67700673f03), Python 3.12, `six` 1.17.0, and a working GNU Fortran 14.2.0-19 compiler. This run used verified Debian packages extracted unprivileged in scratch, without system package changes. See the manifest for exact toolchain and model fingerprints. From an empty scratch working directory:

```sh
python /path/to/mg5/bin/mg5_aMC /path/to/generate.mg5
python /path/to/analyze_lhe.py qedpair/Events/run_01/unweighted_events.lhe.gz
```

Replaying the archived gzip with the analyzer reproduces the JSON byte-for-byte; independent regeneration need not reproduce archive hashes because metadata and toolchain paths can change. The generator's LHE average-weight convention assigns each positive event the common weight 8.6845, not a unit weight or a per-event integrated cross section. The sample-normalized rate is `sum(w)/N`; the selected rate is `sum(w_selected)/N`. There are no PDFs, ISR or showering, decays, detector response, inference or limits. The generator is [MadGraph5_aMC@NLO](https://arxiv.org/abs/1405.0301); data level is parton-level [LHE](https://arxiv.org/abs/hep-ph/0609017).
