# Fixed two-bin Asimov diagnostic for triple Higgs production
Source: Campbell et al., [arXiv:2611.33105v1, Fig. 8 lower left and Eq. (2.2)](https://arxiv.org/html/2611.33105v1#S2.SS2).
Nominal models (k3, k4, kt, k2t, k3t): A=(1.5,10,1,0,1.8), B=(0.7,-60,1,0,-1).
The fixed boundary is 750 GeV, twice threshold, locked before extracting differences.
Source vector steps (not pixels) are calibrated against five ticks; each 40 GeV
step is integrated in linear probability, clipped to [400,1200] GeV, with 750
splitting its containing step. The high-bin fractions in that window are
0.34712 and 0.27858. Inclusive LO rates from author JSON are 12.10932 and
12.67734 fb; the selected-window yield ratio is 1.05937 if the common
in-window signal acceptance is flat and the decay branching ratios are fixed.
Outputs include an exact equal-selected-rate control.

For a truth point with nominal Asimov signal plus background, fit each
hypothesis using Poisson bins with standard-normal auxiliary constraints.
Rates vary as exp(0.15 theta_s), exp(0.20 theta_b). Each high-bin probability
has a logit nuisance with local absolute width w; the low bin is its complement.
Symmetric migration r maps p to r+(1-2r)p before these nuisances. 
For the common illustrative 4b2gamma selection, 30 A events, 100 background
events, background high fraction .30, 10% signal migration, 5 percentage point
shape widths for both signal and background, q_A = 0.00579 -> 0.05279 for
A truth and 0.00570 -> 0.05233 for B truth. This median Asimov diagnostic is
not a calibrated significance, measurement, or experimental projection. The
30/100 yields and response parameters are not fitted to CMS or ATLAS. At 300
A events the tested model still gives sqrt(q_A)<1 both ways; 300 is a purely
mathematical stress test and not a realistic 4b2gamma selected yield assumption.
Selection outside the plotted range is not considered. No detector simulation.
The realistic next inputs would be reconstructed response and an experimental
background covariance; this result does not warrant implementing an exclusion.

Checks: exact equal-rate identical-shape control, matching-mixture different-rate
control, Poisson count/conditional-multinomial factorization, 1 GeV independent
midpoint sum check, exact analytic gradient against Powell objective minima
(<1e-7), and q_two >= q_one. L-BFGS-B line search can terminate near machine
precision; require a small gradient and a separately converged Powell profile.

Replay: get the versioned arXiv source bundle, extract only
HLLHC_mix_m3h_YR5.pdf and anc/coeffs_14000.json, verify source hashes, run
python extract.py then python profile.py > results.json. Python 3.12,
PyMuPDF 1.26.6, NumPy 2.3.5, SciPy 1.17.0. Third-party originals are not
republished in this package. Source bundle SHA256:
5ffded2747827c6e9e0b6f83c0f00ddae88f2fd80db2f4d6ad5b9a3ec9d39917
