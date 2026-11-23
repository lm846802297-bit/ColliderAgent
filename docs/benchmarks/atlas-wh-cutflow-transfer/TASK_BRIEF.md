# Published ATLAS selected-yield transfer into HistFactory

Goal: bridge experiment-validated selected yields to their original likelihood without mixing analyses or regenerating detector simulation. Question: do the final nine weighted selected yields in ATLAS SUSY-2019-08 HEPData v4 tables t42–t50 agree with the native nominal signal prediction for the matched published templates?

Use release v4/r3 and tables t42–t50 at 13 TeV and 139 fb⁻¹, as defined by ATLAS arXiv:1909.09226v2, Table 2. Match SR-LM (300,75), SR-MM (500,0), and SR-HM (750,100) GeV to their low/medium/high mCT bins in [180,230], [230,280], >280 GeV. These are final weighted MC counts, not acceptance fractions or post-fit background. Original patch identity, channels, benchmark masses, energy, and bin labels must agree. The first raw MC rows are not used.

Gate fixed before numerical comparison: original signal template and native pyhf nominal increment (mu=1 minus mu=0, with all other parameters at official initialization) must both agree with the printed yield within half its least significant decimal unit. Do not use statistical errors as tolerance. Require template and native increment agree within 1e-9 events, without removing control channels or altering observations. Test misplaced bins and incorrect table identity. No fit, new limit, simulated detector transfer, or application to other benchmarks.
