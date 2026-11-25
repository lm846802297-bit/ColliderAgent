# CANON 37-master source-system intake (not the canonical answer)

This directory contains an independent Kira family and matching derivative
generator for Table 1 / §IV.1 of
[CANON arXiv:2611.33100v1](https://arxiv.org/html/2611.33100v1#S4.SS1).
The author's original pre-canonical table is not needed for this independently generated basis. The [native discovery receipt](native_discovery/receipt.json) records two successful 37-master runs with byte-identical order, plus a native sector-30 check; it is not evidence that the full symbolic run is complete. No search timing is reported.

## Derivatives before IBP

Use the independent Gram variables `s,t,Q3sq,Q4sq,m2`, with external
`p4=-p1-p2-p3`. With external vectors forming a column of vectors p, the
differential operator for x moves p by C_x p, where
C_x = (partial_x G) G^(-1)/2. This enforces
C_x G + G C_x^T = partial_x G at generic nonzero Gram determinant. Loop
vectors are held fixed. For denominator (a.k+b.p)^2-M^2, differentiate the
quadratic form in directional variables, then use the exact inverse linear
map between all nine denominator/ISP slots and the nine scalar products.
Expand each derivative row by shifting powers of its affected propagator
and the at-most-linear numerator. For m² the D7 derivative is -1; the
integrand derivative is a7 times the integral with one more D7 power.
The measure's regulator factor is independent of kinematics.

A separate loop-Euler check on each denominator verifies
`sum_x x*d_x D_i + (1/2)*sum_l k_l*d_kl D_i = D_i`.
After IBP, each master with powers a_i must therefore satisfy
`sum_x x*A_x[row,:] = (4-2*eps-sum_i(a_i))*unit_row`. This is tested as an
exact input gate before accepting the resulting source matrix. Passing it
alone is not independent proof of the underlying reducer output. An exact
four-vector test compares all 45 denominator/direction pairs against a
different construction (Minkowski components and linear constraints).

## Running the two untimed preparation stages

1. Obtain a verified Kira 3/FireFly executable from the
   [upstream distribution](https://gitlab.com/kira-pyred/kira), record the
   release/build and checksum. In a fresh discovery directory copy
   `config/` and `discovery.yaml`; run `kira discovery.yaml`. Check that
   the ordered candidate masters are stable under increasing seeds, exactly
   37 unique, and span the needed derivative targets in the symbolic run.
   The first listing can contain unresolved integrals; do not equate
   the discovery count alone with success.
2. From the repository root, freeze the selected source order with
   `python python-agent/tools/canon_pdb_intake.py prepare masters.txt NEW_JOB`.
   Kira-format `masters.txt` uses `PDB[i1,...,i9]`, one per line. Inside the
   fresh directory, run `kira jobs.yaml` (see the
   [author's Kira pipeline](https://github.com/Alice-Shimada/CANON-release/tree/6e5db3c713d1602c0d79d01e0dcfef8e5acb5490/components/reducers/kira)).
   If seed-edge or closure diagnostics fail, adjust bounds and record the
   change. Do not specialize any of the five variables; `m2` is a squared
   mass, and its differential direction is required.
3. Preserve the unmodified Kira export. Normalize it to JSON
   `{"schema":"pheno-pdb-ibp-v1","masters":[...],"rules":{"PDB[...]":{"PDB[...]":"exact rational coefficient"}}}`
   without changing the order or coefficients (`d` or `eps` accepted).
   A zero rule must be present as an empty object; a missing target does not
   imply zero. Use `python python-agent/tools/kira_pdb_export.py KIRA_EXPORT.m NEW_JOB/preferred-masters NEW_JOB/targets NORMALIZED.json`. The data-only converter was exercised on a real export for the sector-30 subfamily. Kira uses lowercase `q3sq,q4sq` for Fermat; the converter maps them back to the intake names without changing kinematics. Obtain the 21-letter alphabet as exact
   expressions from the published output only; do not expose its residue
   matrices or canonical basis.
4. Run `python python-agent/tools/canon_pdb_intake.py assemble NEW_JOB NORMALIZED.json LETTERS.json SOURCE.json`.
   The tool regenerates derivatives from the frozen master list, refuses
   missing rules or unexpected output masters, and checks homogeneity across
   all five directions. Hash the native and normalized inputs and compare
   independent exact/finite-field probes before trusting the full A_x
   source. Only then proceed to [paired search](../README.md).

Local tests:
`python -m unittest discover -s python-agent/tests -p test_canon_pdb_intake.py -v`.
As a small analytic control, sector 30 factorizes into two massless bubbles
carrying s; their scaling is `(-s-i0)^(-2*eps)`. A closed row from the
single-bubble IBP relation goes through the assembled format and verifier;
this is not a native reduction or evidence that the other 36 rows are known.

### Native evidence

The deposited Kira build is [Kira 3.1/FireFly, Mendeley v3](https://doi.org/10.17632/v3cmsnfrnn.3).
The 128-bit build's bytes matched the deposit's SHA-256 before execution.
For this noncommercial research run, obtain Fermat separately from the
[author](https://home.bway.net/lewis/ferm7.html), preserving the `BACKWARD`
directory, and set `FERMATPATH` to the executable. No binaries are stored here.
The sector-30 native rules reproduce the independent result (3-d)/s for the
dotted bubble ratio and explicitly set its scaleless counterpart to zero.
