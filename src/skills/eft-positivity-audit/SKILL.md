---
name: eft-positivity-audit
description: Opt-in theory screen for the specific dimension-eight aQGC M-sector positivity bound of Chang, Wan and Zhou, arXiv:2611.26692v1 Eq. (18).
---

# EFT positivity audit

Run only when explicitly requested or when the user opts in to a theory screen.
Do not use this as an automatic filter in an experimental likelihood or as a
test of complete SMEFT positivity. Confirm the coefficient mapping first.

1. Verify the four $F_{Mi}$ against the arXiv v1 Appendix D operator definitions
   and rescaling, including a common inverse-fourth-power energy unit. If the
   mapping is missing, return UNDETERMINED; never identify by name alone.
2. Run the local JSON CLI in [the repository guide](../../../research/eft_positivity/README.md)
   or call `check_eq18(payload)`. Keep INTERIOR, BOUNDARY and OUTSIDE scoped to
   Eq. (18). A boundary output uses the exact supplied numbers; it does not
   establish saturation for uncertain underlying coefficients.
3. Preserve source and assumptions and report the failed principal minors if any.
   Do not infer a unique heavy mediator or an observed/expected exclusion.
