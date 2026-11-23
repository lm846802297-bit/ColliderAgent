# Calling a native DDCalc shared library from Python

The unmodified upstream Python binding reproduced the prior native Fortran XENON1T 2017 benchmark exactly. At local halo density 0.30 GeV/cm³ the expected signal is **5.754551805903094** events; using 0.15 with all other inputs unchanged, it is **2.877275902951547**. The number observed is 0 and the fixed expected background is 0.36 in both cases. The full independent Poisson log likelihood matches at both points. No experimental limit or detector-model validation is claimed.

[DDCalc v2.3.0](https://github.com/GambitBSM/DDCalc/tree/v2.3.0) peels to `065c126c563107de090a9644bed997462d72ec61`, with embedded version string `2.1.0` unchanged. Its checked [ctypes binding](https://github.com/GambitBSM/DDCalc/blob/065c126c563107de090a9644bed997462d72ec61/include/DDCalc.py) was used as-is. The target is Fortran Example 1, not the upstream Python demonstration, which uses a tabulated halo by default. The parent [native Fortran stdout](https://github.com/lm846802297-bit/ColliderAgent/blob/2c38172ffbc29246fade0138446d900dfad0a103/docs/benchmarks/ddcalc-native-elastic/native.stdout) is hash-pinned.

The shared link succeeds when the previously missing libgfortran5 runtime is supplied with a matching compiler package; no upstream source or Makefile change is needed. On Debian trixie x86-64 use the exact [manifest packages](run_manifest.json), checking the Debian-signed InRelease and package-index hashes before extracting into a private scratch tree. Set your shell's `FC_DIR` to that extracted root, `DOCS` to this benchmark directory, and `PARENT_STDOUT` to the verified parent output. From the exact upstream source root:

```sh
FC="$FC_DIR/usr/bin/x86_64-linux-gnu-gfortran-14"
FC="$FC -B$FC_DIR/usr/libexec/gcc/x86_64-linux-gnu/14/ -B$FC_DIR/usr/lib/gcc/x86_64-linux-gnu/14/ -B/usr/lib/gcc/x86_64-linux-gnu/14/"
LC_ALL=C make -j3 lib ddcalcinclude FC="$FC"
export LD_LIBRARY_PATH="$FC_DIR/usr/lib/x86_64-linux-gnu"
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 LC_ALL=C \
  python "$DOCS/replay.py" "$PWD" "$PARENT_STDOUT" "$LD_LIBRARY_PATH/libgfortran.so.5"
```

The replay checks the actual mapped DSO and Fortran runtime using Linux procfs. Passing a byte-identical copy of the runtime at an unmapped path is rejected. Built-library hashes can differ across directories because upstream embeds source paths. No compiler packages, binaries or experiment files are archived here. This is a local benchmark for one supported API path, not a bundled install, release artifact or new physics result.
