# Research Task Brief — Standard elastic SHM interface
Task ID: 20261123-collider-elastic-shm-interface

1. Parent objective: distinguish a verified reusable DM input from a candidate external engine. Question: do the analytic velocity integral and elastic recoil-to-speed map survive independent normalizations, support boundaries and unit controls? Claim limited to fixed synthetic benchmarks.
2. Primary sources: DDCalc v2.3.0 065c126c563107de090a9644bed997462d72ec61, src/DDHalo.f90 (SHA-256 c3e7ef05c339f66f3a22727a7410c7f031bfd799aecd5806bcc18a07288d1529) and src/DDRates.f90. Baxter et al. (arXiv:2105.00599v3), §3.1, Eqs. (10–12).
3. Baseline: lm846802297-bit/ColliderAgent main a6663822dc478cfe81f39e61e3970d0abdb205cf, clean clone, existing topic branches not modified; central lock 142267bc803c90aa681110293b66b73947bbcaa1.
4. Conventions: Galactic-frame spherical speed cutoff; lab speed positive or zero; η in s/km, v in km/s, recoil keV, masses GeV, c=299792.458 km/s. No invariant four-momentum or interaction signs in this benchmark.
5. Scope: isolated standard nonrelativistic elastic kinematics and sharply truncated isotropic Maxwellian; fixed synthetic boosts and masses. No scattering model, inelastic/radiative channel, likelihood, detector, or native DDCalc.
6. Known evidence: DDHalo declares units and source interface; no native numerical result assumed. Previous pyhf/QED candidates are different tasks.
7. Independent work: derive vmin from q and reduced mass; compare analytic branches to Galactic-shell angular integration with composite radial Simpson and numerical normalization.
8. Acceptance fixed before run: absolute η error <=2e-11 s/km, normalization error <=2e-9, two radial resolutions, join/cutoff/zero-boost and wrong keV↔GeV control. Stop if alignment, data identity or checks fail.
9. Outputs: fixed no-dependency reference/CLI, targeted tests, short source-linked benchmark documentation, plain local result JSON and manifest.
10. Remaining gaps: DDCalc absent and native parity not run; no new scope, remote change, or CI.
