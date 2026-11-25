# Axial-lepton contact benchmark: Lagrangian to Fermi-LAT limit

This is a new interpretation of the [Fermi-LAT six-year, 15-dwarf public
likelihood](https://arxiv.org/html/1503.02641v2#S4), not a result for the
original no-DM axial-vector model. It assumes a stable symmetric Dirac
fermion and keeps the charged-lepton pure-axial / neutrino left-handed
relative coupling strengths of an axial \(L_\mu-L_\tau\) inspired benchmark.
In the heavy-mediator limit define \(C=g_\chi g_X/m_{A'}^2\).
The terms below have the overall convention \(C\) (sign irrelevant here):
\[
{\cal L}_\mathrm{eff}=C(\bar\chi\gamma^\mu\chi)
  [\bar\mu\gamma_\mu\gamma^5\mu-\bar\tau\gamma_\mu\gamma^5\tau
  +\bar\nu_\mu\gamma_\mu P_L\nu_\mu-\bar\nu_\tau\gamma_\mu P_L\nu_\tau].
\]
The distinct flavor final states do not interfere in the rate. At
\(s=4m_\chi^2\) the unpolarized initial dark current is spatial; for
a charged axial lepton the contracted trace scales as \(m_\chi^2
|\mathbf{k}|^2\), and the two-body phase space supplies a further beta.
Thus in natural units
\[
(\sigma v)_\ell=\frac{C^2m_\chi^2}{\pi}\,\beta_\ell^3
\quad(m_\chi>m_\ell),\qquad
(\sigma v)_{\nu_\ell}=\frac{C^2m_\chi^2}{2\pi}.
\]
\(\beta_\ell=\sqrt{1-m_\ell^2/m_\chi^2}\); outside the channel threshold
set the leading term to zero. The neutrino factor one half follows from
one massless chirality, tested by a separate matrix trace. We use
\((\hbar c)^2c\) to convert GeV^-2 to cm^3/s. For equal particle and
antiparticle densities, \(n_\chi n_{\bar\chi}=\rho^2/(4m_\chi^2)\);
combining with the geometric factor gives
\[
\frac{d\Phi_i}{dE}=\frac{J_i}{16\pi m_\chi^2}
 \sum_{f=\mu,\tau}(\sigma v)_f\frac{dN_f}{dE}.
\]
The closed or invisible channels are not reassigned to a photon template;
neutrino channels still count in the total annihilation rate. No gamma yield
from neutrinos is included in this prompt-only benchmark, and weak radiation
and inverse Compton are not modeled. The two prompt spectra are mixed in each
of the original 24 energy bins, using the respective partial rates, before
the nuisance fit. Fixed DMFit yields are an approximation, not a detector
reanalysis. The solver profiles the 15 J factors with the published Eq. (3),
and uses \(2\Delta\ln{\cal L}=2.71\). The 25 mass nodes use no fitted
information from the published Fig. 1 limits. Comparison with original axes
is archived separately in ../fermi-lat-dwarfs (pure-channel calibration);
the new coupling plot has no published same-model contour to overlay.

At \(m_\chi=2\) GeV, \(\mathrm{BR}_\tau=4.62\%\) and
\(\mathrm{BR}_\mu=47.59\%\). At 100 GeV, the model bound is
\(|C|<1.15823\times10^{-6}\ {\rm GeV}^{-2}\) with the adopted 95% likelihood
criterion, corresponding to \(1/\sqrt{|C|}>929.2\) GeV and
\(\langle\sigma v\rangle_{\rm total}<1.49516\times10^{-25}\) cm^3/s.
The fitted coefficient constrains a product-over-mass-squared, not a unique
\(g_X\), \(m_{A'}\), or relic abundance prediction. It applies inside the
EFT regime. If \(m_{A'}\) is not much larger than \(2m_\chi\), the propagator
and width must be treated explicitly. Open dark-sector final states (including
\(A'A'\) when kinematically open) and their cascades are not covered.

## Replay

Use the pinned inputs and code in the [public-likelihood
benchmark](https://github.com/lm846802297-bit/ColliderAgent/tree/0e66d7d69c551ddd2a1118d9659d6d8666cf9ffa/research/phenomenology-benchmarks/fermi-lat-dwarfs).
Place the pinned archive extracts and spectrum grid in that benchmark folder
and run its SOURCE.SHA256 check. Then, in this folder run:

    OPENBLAS_NUM_THREADS=1 python contact.py ../fermi-lat-dwarfs
    python plot.py

The CSV carries branching fractions and total and visible upper limits.
signals.json gives absolute energy flux per bin at the exclusion crossing
for a nominal unprofiled J=10^19 GeV² cm⁻⁵, not a detector count or a fitted
individual dwarf flux. Tests include independent Clifford traces and numeric
per-bin likelihood roots at held-out masses 3.7, 17 and 73 GeV, threshold,
zero coefficient, pure-channel template, and Dirac normalization controls.
