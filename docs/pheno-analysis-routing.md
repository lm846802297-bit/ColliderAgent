# Experimental analysis preflight

## Research task brief

**Question:** Can the pipeline distinguish an applicable ATLAS recast with missing model and detector inputs from a kinematically closed analysis, without treating either as an experimental exclusion? This addresses the gap between separately validated simulation/likelihood tools and a reproducible experiment selection. Scope: deterministic, read-only preflight on a reviewed release catalog and already-derived model facts; not LaTeX inference, new detector simulation, a fit, automated literature discovery or a coverage claim beyond the catalog.

**Acceptance:** Match the published simplified-model and on-shell domains; report concrete missing experimental inputs; distinguish inapplicable, unknown, blocked and ready-for-review; reject malformed values; preserve per-release result provenance boundary. Check the (400,80) GeV stau example and the on-shell invisible Higgs negative control. Stop before setting numerical limits or merging analyses.

## Run

From the repository root:

```sh
python python-agent/tools/analysis_routing.py docs/pheno-analysis-catalog.v1.json MODEL_FACTS.json
python -m unittest discover -s python-agent/tests -p 'test_analysis_routing.py' -v
```

The input JSON has `facts` and optional `evidence` maps. Facts must come from the chosen model implementation, not from the catalog. Masses use GeV. Omit unknown facts rather than setting them to false. An evidence entry is a digest reference supplied by an upstream stage, not an assertion of physical validity; the gate checks its syntax and scope, not the underlying files. Only populate it with independently reviewed artifacts tied to this exact analysis release and model point.

Example:

```json
{
  "facts": {
    "direct_stau_pair": true,
    "unmixed_degenerate_staus": true,
    "bino_lsp": true,
    "stau_to_tau_lsp_exclusive_prompt": true,
    "higgs_mass_gev": 125,
    "invisible_pair_mass_gev": 80
  },
  "evidence": {}
}
```

That point matches the recorded stau topology but returns `blocked_missing_evidence`; the 125 GeV on-shell Higgs decay to the 80 GeV pair returns `not_applicable`. This does not rule out off-shell production or other Higgs channels. The stau checklist includes independent signal acceptance in both signal regions and **both multijet control regions plus the W+jets control region**. Its public (120,1) signal card is not a validated (400,80) input. A known limit calculated with the experimental signal patch cannot fill the independent yield slots.

The catalog is deliberately bounded. A ready route still has `limit_status: not_run`. An absent search is not evidence that it is irrelevant, and the output never combines overlapping or unknown correlations. Next: connect the entry point to reviewed model artifacts, then independently validate the card/UFO and five detector-level yields before running the stau limit.
