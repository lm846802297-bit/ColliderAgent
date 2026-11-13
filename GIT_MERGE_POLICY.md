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
