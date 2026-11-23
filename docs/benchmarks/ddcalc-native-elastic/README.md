# Native DDCalc standard-elastic benchmark

The official XENON1T 2017 example (100 GeV DM, mixed SI and SD) and our focused driver both return **5.754551805903094** expected signal events, 0 observed, 0.36 fixed expected background, and log likelihood −6.114551805903094. The independently evaluated total Poisson log likelihood matches exactly at this point. This does not independently validate the detector signal model: the two rate executions use the same library.

Across 18 independent Galactic-shell integral points the largest native inverse-speed residual is 1.963e-13 s/km; the single elastic recoil velocity differs by 2.84e-14 km/s. Native cutoffs are exactly zero. Both native output files reproduced byte-for-byte on replay with this environment. The extra official examples are preserved in full stdout but were not validated or used as acceptance evidence.

## Identity and replay

- [Upstream v2.3.0 tag](https://github.com/GambitBSM/DDCalc/tree/v2.3.0) peels to exact [commit `065c126c…`](https://github.com/GambitBSM/DDCalc/tree/065c126c563107de090a9644bed997462d72ec61); upstream's internal version string still reads `2.1.0`. Neither source nor version was modified. The signal target is [official Example 1](https://github.com/GambitBSM/DDCalc/blob/065c126c563107de090a9644bed997462d72ec61/examples/DDCalc_exampleF.f90).
- GNU Fortran 14.2.0-19 Debian trixie packages were checked against SHA-256 entries in `Packages.xz`, whose own SHA-256 was checked against Debian-signed `InRelease` verified with the installed Debian archive keyring. These were unpacked only to a temporary directory. [Run manifest](run_manifest.json) contains exact compiler, code and output identities; no binaries/debs are distributed here.
- With a working gfortran and the exact upstream checkout, from its source root:
  ```sh
  make DDCalc_exampleF FC=gfortran
  gfortran -O3 -Ibuild /path/to/native_elastic.f90 lib/libDDCalc.a -o native_elastic
  ./DDCalc_exampleF > official.stdout
  ./native_elastic > native.stdout
  python /path/to/verify.py native.stdout official.stdout /path/to/reference.json
  ```
- `reference.json` is the [frozen independent reference](https://github.com/lm846802297-bit/ColliderAgent/blob/6886256018ef89ea6bf1ffacf5a5647c4d712683/docs/benchmarks/elastic-shm/reference.json), not redistributed here. The verifier rejects a wrong reference hash or support above the cutoff. Do not expect compiled hashes to be portable; upstream Makefile embeds build paths.
- DDCalc was linked into the native Fortran executable via upstream's static archive; this is not a claim of a fully static system binary. The separate shared-library target failed to link against the isolated compiler's non-PIC gfortran static runtime; Python/shared-library binding was not validated. No new limits, radiative or three-body nuclear response, Monte Carlo samples, or CI.

Physics and software: [DarkBit](https://arxiv.org/abs/1705.07920), [DDCalc v2 analysis](https://arxiv.org/abs/1808.10465), and [XENON1T 2017](https://arxiv.org/abs/1705.06655).
