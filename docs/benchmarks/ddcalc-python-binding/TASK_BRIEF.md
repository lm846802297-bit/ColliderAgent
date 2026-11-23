# Native DDCalc Python/shared-library parity

Parent: ColliderAgent native/static benchmark `2c38172ffbc29246fade0138446d900dfad0a103`. Goal: make the verified standard-elastic backend callable from Python. Question: can the unmodified upstream Python binding, using a genuine shared library built from exact DDCalc v2.3.0 source, reproduce XENON1T 2017 Fortran Example 1?

Pin upstream v2.3.0 commit `065c126c563107de090a9644bed997462d72ec61` (internal string remains 2.1.0); pin binding and previous native output bytes. Use locally verified and transient extracted GNU Fortran Debian 14.2.0-19 packages. Check exact binding/lib loading and the signed Debian matching runtime's actual mapped bytes. No system installs or credentials.

Gate fixed before inference: at 100 GeV with the official signed SI/SD cross sections and the Fortran SHM parameters, require n=0, b=0.36, absolute signal and log-likelihood residuals against the static native parent no larger than 1e-10, and independent full fixed-background Poisson log likelihood within 1e-10. Halve only local density and require signal halves within 1e-10, with n and b unchanged and the same independent log-likelihood check. Validate one CLI/Python case and density control only: no new detector constraints, exclusions, radiative scattering, or testing of all DDCalc interface methods. Stop if untrusted/absent runtime or any gate fails.
