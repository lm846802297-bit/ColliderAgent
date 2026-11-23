# ColliderAgent paper-reproduction archive extension

**Status:** Project-specific extension to the central Git merge policy.  
**Central source commit:** 142267bc803c90aa681110293b66b73947bbcaa1

The shared rules for pull-request review, merge strategy, history preservation, and post-merge verification are defined by the [central Git merge policy](https://github.com/lm846802297-bit/high-energy-theory-research/blob/142267bc803c90aa681110293b66b73947bbcaa1/docs/governance/GIT_MERGE_POLICY.md). This file retains only ColliderAgent's paper-reproduction lifecycle and study-discoverability requirements.

## 1. Canonical location for completed reproductions

- A paper-specific result belongs in the research repository that owns the scientific study whenever such a repository exists. Record that repository, immutable commit, and PR in the ColliderAgent execution summary.
- If the reproduction is intentionally maintained as a ColliderAgent example, store the completed run under the relevant paper directory at paper-reproduction/<arXiv-ID>/results/<run_label>/.
- Keep the clean user-facing prompt, annotated debugging prompt, original paper assets, model/UFO sources, process cards, event samples, analysis scripts, and generated results distinguishable.
- Each run uses a unique run label. An incremental run records its parent and never overwrites the previous run's progress, scripts, cards, events, summaries, or outputs.

## 2. Main-branch discoverability

Every completed reproduction maintained in this repository must be discoverable from both:

- the relevant paper-reproduction/<arXiv-ID>/README.md; and
- the root paper-reproduction index.

The entry must identify the source paper and target figure/table, prompt and model revision, run label and parent, model/UFO/process and cards, event sample and random seeds, logs and native outputs, checksums, validation actually performed, reproduction status, limitations, and next step.

Update the study README and root index in the same PR whenever practical. After merge, verify the merge commit, run records, study README, index, and linked artifacts on main. Do not rely on open PRs, branch names, chat history, or temporary Magnus/Actions artifacts as the only discovery path.

## 3. Lifecycle

- In-progress reproductions remain on topic branches. A Draft PR is useful for early review or handoff when its missing stages and evidence are explicit.
- Completed and accepted reproductions are merged to main after the central review requirements and the stated task-specific acceptance criteria are satisfied.
- Diagnostic, partial, approximate, failed, historical, and superseded reproductions may be retained on main when clearly labelled and scientifically scoped.
- Preserve historical runs and link successors; do not replace a previous run merely because a later run uses more events or changed settings.
- Do not bulk-merge dependent pipeline PRs without checking their baselines, parent runs, configurations, downstream stage status, and acceptance evidence.

The central Git policy determines the merge method. ColliderAgent's default remains Create a merge commit for substantive model, simulation, analysis, reproduction, and validation work.
