# Git merge strategy and research commit-history policy

This policy applies to research reproductions, model/simulation/analysis pipelines, validation code, and substantive repository maintenance.

## 1. Default: Create a merge commit

Use GitHub **Create a merge commit** by default for substantive work. Preserve meaningful commits from the topic branch and the explicit PR boundary. In this repository, commits may record separate model definitions, FeynRules/UFO checks, process cards, event-generation settings, detector configurations, cutflows, statistical treatment, numerical fixes, regression tests, or reproduction evidence. Keeping those steps traceable supports reproducibility, debugging, and Git bisect.

## 2. Exceptions

- **Squash and merge:** only for trivial, indivisible maintenance or documentation changes (such as spelling/formatting cleanup) whose intermediate commits have no useful independent technical or research provenance. Do not squash substantive model, simulation, analysis, or validation work merely to shorten the main log.
- **Rebase and merge:** only when linear history is explicitly desired and the topic commits are already meaningful, ordered, and reviewable. Rebase rewrites commit identities and does not preserve the original branch's exact commit graph.

## 3. Before merge

1. Inspect the full PR commit list and actual diff; commit count alone does not determine the strategy.
2. Clean up temporary, duplicate, or misleading commits before final review when appropriate.
3. Confirm the PR is focused and records the exact source revision, run labels/parents, cards/configurations, inputs, outputs, provenance, checks actually executed, and limitations as applicable.
4. Use **Create a merge commit** unless a documented exception applies. Explain any Squash/Rebase choice in the PR description.
5. Do not rewrite or force-push reviewed/shared history for cosmetic cleanup.

## 4. After merge

Verify the merge commit and the integrated main state. Check run manifests, source/configuration files, logs, native outputs, checksums, and links as applicable. Report archival status separately from model validation, event-generation validation, detector/analysis validation, and scientific reproduction.

## 5. Existing history

This policy is prospective. Do not rewrite already merged PRs to change their merge method. Existing squash/rebase merges remain part of the historical record; their PRs and retained branch history can still provide context.

**Default rule:** substantive research and pipeline changes use Merge Commit; Squash is for trivial changes with no independent provenance; Rebase is for an intentional linear history with curated commits.

## 6. Main is the canonical reproduction archive

The default branch `main` is the canonical, searchable archive of completed and accepted paper-reproduction work. A PR is a review and integration mechanism; it is not a permanent substitute for merging completed reproduction records into `main`.

### Reproduction lifecycle

| State | Required handling |
|---|---|
| In-progress reproduction or pipeline | Keep on a topic branch. Use a Draft PR for early review/handoff and list unexecuted stages and missing evidence. |
| Ready for review | Open a focused PR to `main` with the paper/arXiv source, prompt/figure target, exact model and run configuration, run manifest, native outputs, logs, and checksums as applicable. |
| Completed and accepted reproduction | Merge after reviewing the actual diff and checking the documented acceptance criteria. Do not leave the accepted record only on a branch, open PR, or expiring remote job. |
| Historical or superseded run | Retain it on `main` with its run label, parent relationship, source revision, and explicit status; link the successor rather than overwriting it. |

### Searchable record requirements

Every substantive reproduction merged to `main` must be discoverable from the relevant `paper-reproduction/<arXiv-ID>/README.md` and the root paper-reproduction index. The record should identify the source paper and target figure/table, prompt and model revision, run label and parent, exact model/UFO/process and cards/configurations, event sample and random seeds, logs and native outputs, checksums, validation actually performed, scientific/reproduction status, limitations, and next step. If a result is only a partial pipeline stage, label it as such.

Update the study README and parent index in the same PR whenever practical. After merge, verify the indexed paths and artifacts on `main`. Do not rely on PR search, branch names, chat history, or temporary Magnus/Actions outputs as the only discovery path.

### Merge and branch closure

- Merge a completed, reviewed reproduction once its stated acceptance criteria are met; the record may be diagnostic or partial if labelled honestly.
- Keep Draft PRs for genuinely unfinished work. Do not merge merely to reduce open-PR counts.
- Do not bulk-merge dependent PRs without checking parent runs, branch baselines, exact configs, and downstream stage status.
- After merge, verify the merge commit, run manifest, study README, and root index on `main`. Delete a topic branch only when it contains no unique unmerged run or follow-up work.

This section adds an archive/discoverability lifecycle and does not change the existing default of **Create a merge commit** for substantive reproduction work.

