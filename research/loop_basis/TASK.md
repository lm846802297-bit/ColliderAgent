# Independent loop-basis acceptance gate

Task: 20261125-loop-basis. Baseline: ColliderAgent main at
1254037e968d996befb2b69a40b019a6df0617de. Standalone symbolic validation;
no event-generation, detector, or statistics changes.

Question: can fixed rules and an agent submit their candidate bases to the
same exact test without trusting either producer's algebra? Accept only if
the input hash, generic invertibility, and reconstructed differential system
match a constant-residue dlog connection in every direction. Reject sign
errors, singular transformations and candidates matching only at probe
points. Use exact arithmetic, no pointwise proof. Test a separately defined
fixture, including a quadratic root and an omitted direction. Full-family
comparison stops if the pre-canonical IBP-derived DE or source basis is absent.

Source: CANON arXiv:2611.33100v1 §II.2 and §IV.1; authors' public release
6e5db3c713d1602c0d79d01e0dcfef8e5acb5490. The 37-master target has five
invariants and one quadratic root. Explicit convention: column vectors,
dI/dx=A_x I, J=T I (the inverse of CANON's naming convention), and the
target is epsilon times a sum of constant residue matrices times dlog letters.
Generic invertibility excludes the singular locus, not all kinematic points.
No boundary constants, purity or original IBP reduction is certified.

Environment: local Python + SymPy for symbolic implementation and regression;
no experimental analysis, native IBP production or numerical physics run.
Central lock: research/standards-lock.yaml at central 14155487afc075d301fa7f6cf452c7bff137e869;
task provenance: research/standards-provenance/tasks/20261125-loop-basis.json.
