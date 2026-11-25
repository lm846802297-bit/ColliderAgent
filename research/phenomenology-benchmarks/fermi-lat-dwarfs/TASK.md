# Six-year Fermi-LAT dwarf likelihood benchmark

Question: Can an independent solver rebuild the observed Fig. 1 upper limits for
the 15-dwarf combined b and tau channels using only released energy-bin likelihoods,
documented J-factor constraints, and pinned DMFit prompt yields?

The reference numbers and PDF path are validation only. No fit to the published
curve, no change to J central values, no detector reanalysis. For this approximate
public-input benchmark, quantify every source node, report a discrepancy explicitly
rather than forcing an exact match. Verify an independent direct per-bin optimizer
at three masses per channel to relative 1e-4. Reject zero in-band flux, invalid
input, and flux beyond the released tables. If a model-specific recast is not
independently validated, mark it NOT RUN. A fixed-J alternative is a diagnostic,
not an astrophysical systematic band or a new experimental result.
