# Fig. 5(a): visible reproduction and one-parameter variations
The original XENON panel is an unscaled vector form, preserved on both pages.
Bold dashed curves on page 1 distinguish the independently recomputed
nonasymptotic and asymptotic curves without shifting any point. The original
50-node comparison is unchanged. Page 2 uses the same published log axes.
Curves are clipped at the original plot limits; the CSV holds all masses.

Fixed model assumptions: elastic SI, isoscalar nucleon vector current, standard
Halo velocities, same underlying XENON1T binwise response and nonasymptotic
threshold. Each new curve replaces one baseline parameter. The density change
0.30 to 0.20 GeV/cm^3 at fixed mass and shape scales the cross-section limit by 1.5.
For finite mediator mass 100 or 50 MeV, take the leading elastic t-channel ratio
(dR/dE)/(dR_contact/dE) = (1+Q^2/mV^2)^(-2), Q^2=2m_A E_R.
The horizontal variable remains m_chi; the vertical variable is the upper
bound on the zero-momentum WIMP-nucleon cross section. This is not a reanalysis
of the 2018 full likelihood or a limit on the inelastic LZ radiative model.

Replay from this directory: materialize the unchanged source panel as
../Fig5a_original.pdf, as specified in the parent README. Add the parent
directory and the parent's pinned library source/deps to PYTHONPATH.
Run python parameter_scan.py then python render_v2.py (PyMuPDF and system
DejaVu fonts required). Native-vs-independent limit error <2.03e-5 relative
over 100 finite-mediator limits. Three density controls and zero-transfer
and contact limits passed. XENON Collaboration Fig. 5(a), CC BY 4.0,
source https://arxiv.org/src/2210.07231v1; only overlays are new.
