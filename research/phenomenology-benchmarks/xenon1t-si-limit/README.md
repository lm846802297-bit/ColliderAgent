# Heavy-vector Dirac dark matter → XENON1T 90% CL
This is a recast of the collaboration's **public approximate likelihood**
arXiv:2210.07231, Fig. 5(a), not a reconstruction of the 2018 full likelihood.
It is the first non-collider vertical benchmark for PhenoAgent.

Take a massive vector V, a Dirac fermion chi, and nucleons N=p,n.
The interaction terms are -V_mu [g_chi chi_bar gamma^mu chi +
g_N(p_bar gamma^mu p + n_bar gamma^mu n)]. Include canonical kinetic and
mass terms. At |q| << m_V, integrating out V gives the dimension-six
vector-vector contact with absolute coefficient C=|g_chi g_N|/m_V^2.
For coherent isoscalar elastic scattering,
sigma_p = mu_p^2 C^2/pi in natural units, and
sigma_A(0) = sigma_p A^2 (mu_A/mu_p)^2.
No thermal abundance computation; chi is assumed to supply the local DM.
The public demo's effective xenon A=131.293 and Helm parameters are retained;
this is not an isotope-resolved or two-body-current calculation.

The analytic rate is proportional to rho/m_chi times
sigma_p A^2 F_Helm^2(q) eta(vmin)/(2 mu_p^2), with explicit conversion
to events/(keV tonne year) in elastic_limit.py. eta integrates the
lab-frame cut Maxwellian; vmin=q/(2 mu_A), q=sqrt(2 m_A E_R), and
rho=0.3 GeV/cm^3, v0=220, vE=232, vesc=544 in km/s.
Use the public migration matrix in the existing release to get the
reconstructed bin yields; do not multiply acceptance or exposure a second
time. Each observed bin's profiled likelihood is interpolated as a function
of predicted signal. Independently sum the piecewise linear likelihoods,
find the global minimum over their knots, and solve for the upper
crossing with the public toy-derived threshold (also report asymptotic).
The public notebook uses a further 1,000-node interpolation before solving.
No result normalization is fitted.

45 mass points, 6–1000 GeV. Rate cross-check against wimprates 0.3.2
at 10,30,50,100,500 GeV: maximum relative residual 0.120% away from vanishing tails.
Numerical inference parity with public v1.0.0 code on the same analytic spectrum:
max relative difference 0.00788% across both thresholds. At 30 GeV the
toy-threshold bound is 4.38044e-47 cm^2, compared with the old full-likelihood
tabulated 4.05e-47 cm^2; at 6 GeV, 5.98602e-44 vs 2.49e-44 cm^2.
Those discrepancies are not errors against the approximate implementation.
The plotted 2018 points are read only at the plotting step.
Null signal is rejected rather than producing a finite upper bound.
This validates elastic SI O1 only, not the high-energy LZ radiative signal.

Replay:
- Get source archive from https://codeload.github.com/XENON1T/xenon1t_approximate_nuclear_recoil_likelihood/tar.gz/refs/tags/v1.0.0,
  SHA-256 0b48903ff1dbf0e9160f54ded71d23025ebdfbb17736334072f77084c9b25e77.
  Extract under this directory as xenon1t_approximate_nuclear_recoil_likelihood-1.0.0.
- Download pinned Python distributions, check SOURCE.SHA256, and extract
  wimprates-0.3.2.tar.gz here unchanged; install the three wheels into deps/.
- CPython 3.12 / NumPy 2.3.5 / SciPy 1.17.0. From this directory run:
  PYTHONPATH="$PWD/deps:$PWD/wimprates-0.3.2:$PWD/xenon1t_approximate_nuclear_recoil_likelihood-1.0.0" python elastic_limit.py > validation.json
  Then python plot_limits.py. Use a writable MPLCONFIGDIR.
- The published inputs and original outputs of other teams are not reuploaded.

Two fresh processes produced byte-identical observed limits and reconstructed
signal arrays. As expected numericalunits varies its internal unit realization;
the independent check's reported relative residuals moved at most 7e-15.
The original check and replay are both retained. The citation "Fig. 4" in the
pre-run brief referred to the toy calibration figure; Fig. 5(a) is the limit plot.

## Original-panel validation
The layered PDF is based on the original author vector panel
figures/binwise_ul_vs_published_SI.pdf from https://arxiv.org/src/2210.07231v1
(CC BY 4.0), SHA-256 239cae7a8737d87434af65e97d33b4b8ef81cc19b107af05cfbbf5e49b492aac.
No axis is reconstructed or redrawn. Measured three major ticks on each axis,
matched original nodes to the exact 6–1000 GeV logspace of 50 points, and
recomputed the limits at those masses without using digitized y values.
Read the source curve's vector vertices only after computing the rates.
At the 50 original vertices: max |delta| 0.33061% (nonasymptotic),
0.38701% (asymptotic), both at 6 GeV. RMS 0.11236% and 0.11790%.
For replay, extract the author panel as Fig5a_original.pdf. Run
paper-grid/elastic_limit_paper_grid.py under the paper-grid directory
with the same absolute PYTHONPATH as above, and then overlay_original.py
from this directory. The pointwise CSV and overlay_validation.json expose
the raw values, residuals and tick calibration.
