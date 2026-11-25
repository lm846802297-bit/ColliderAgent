# Fermi-LAT dwarf likelihood reconstruction

Public-analysis benchmark, not a new model-specific bound. Reconstructs the observed
95% CL six-year Pass 8 curves in Fig. 1 of [Ackermann et al.](https://arxiv.org/html/1503.02641v2#S5)
for pure b bbar and tau+ tau− prompt annihilation. The 15 targets and rounded
log10 J values and errors are taken from Table 1. The likelihood tables are the
official [revision 01-00-02 release](https://www-glast.stanford.edu/pub_data/1048/).
The prompt grid is Fermipy commit fbecde1a01c03fd3d8a9ecc8e997506d5bda9589
(DMFit format). We have not established exact identity of that grid and all 
analysis settings with the 2015 internal configuration.

Use phi_bin=J <sigma v>/(8 pi m^2) times the integral of E dN/dE in each bin,
for self-conjugate dark matter. Integrate the interpolated DMFit E dN/dE with
subintervals at each tabulated log-energy knot, stopping at E=m. Each released
bin's delta-log-likelihood is interpolated linearly in energy flux, referenced
to the background-only point, and not extrapolated. For each dwarf combine the
bin functions in one amplitude and profile z=log10(J/J_obs) with penalty
z²/(2 sigma²). Within each linear segment a stationary point is computable via
Lambert W. Enumerate all segment ends and both real branches when applicable.
Use a positive cross section and a one-sided 2 delta log L=2.71 bound relative
to the profiled best fit. A separate implementation interpolates each original
bin independently and numerically maximizes in z. At six benchmark masses
its limit differs by at most 1.43e-10 relatively. Zero in-band signal and
fixed-J over-table-bound flux are rejected.

The observed original curve is solid black, not the blue Pass 7 line or dashed
median. All 23 original vector nodes match the official numeric table to
less than 8.3e-7 relative precision; the original was used only after solving.
The independent results are lower by up to 5.67% (b bbar, 100 GeV) and 5.28%
(tau, 10 GeV). This is a near reproduction, not an exact reconstruction of
the original LAT analysis. Rounded J factors, DMFit grid identity, and finite
likelihood tabulation/interpolation are possible contributing factors; the
difference is not attributed to any one of them without evidence. At 100
GeV, fixing each J to its published mean rather than profiling moves the
reconstructed b and tau limits down 14.25% and 6.39%. This is a nuisance
handling control, not a systematic uncertainty band or additional LAT limit.
No detector-level reanalysis, confidence coverage study, or Lagrangian-specific
model limits in this increment. No inference is transferred to LZ or ATLAS.

## Replay

Save the official tarball as release.tar.gz from the link above and the arXiv v2
source archive as paper-source.tar.gz. Download the Fermipy grid from
https://raw.githubusercontent.com/fermipy/fermipy/fbecde1a01c03fd3d8a9ecc8e997506d5bda9589/fermipy/data/gammamc_dif.dat 
as gammamc_dif.dat.pin. Extract the two archives to official/ and paper/,
respectively, and run sha256sum -c SOURCE.SHA256. The repository does not
redistribute the source assets. With Python, NumPy 2.3.5, SciPy 1.17.0, and
PyMuPDF, run:

```sh
export OPENBLAS_NUM_THREADS=1
python recalc.py > trial.log
python verify.py > independent.json
python overlay.py
```

The generated vector overlay has the source page at its native scale and
placement, with additional legend space below. Pages 1/2 are b bbar and
pages 3/4 tau. The even pages also show the fixed-J curve. The adjacent CSV
contains absolute limits in cm^3/s and signed fractional deviations.
