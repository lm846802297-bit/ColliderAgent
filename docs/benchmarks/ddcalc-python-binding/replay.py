"""Run a pinned XENON1T benchmark through original DDCalc Python/ctypes."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

BINDING = "6de8ffbe8db5b4bcc3d405e8a534ee5df152528bfa33e2b2c46282deed3dce6c"
STATIC = "1456cc1e442ca518432540f6a53eea3aa9b635d3a9d7c5654a5a620b1653280a"
RUNTIME = "d1c716d10039872bb5481b921d2142577c7873cad4d8d9f09028231aa7e42127"
TOL = 1e-10


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(root, static_file, runtime):
    binding = root / "include/DDCalc.py"
    library = root / "lib/libDDCalc.so"
    runtime = runtime.resolve(strict=True)
    if digest(binding) != BINDING or digest(static_file) != STATIC:
        raise ValueError("unmatched upstream binding or parent reference bytes")
    if digest(runtime) != RUNTIME:
        raise ValueError("unexpected Fortran runtime bytes")
    if library.read_bytes()[:4] != b"\x7fELF":
        raise ValueError("expected a native ELF library")
    with static_file.open() as fp:
        _, obs, signal, back, logl = fp.readline().split()
    n, s0, b, ll0 = int(obs), float(signal), float(back), float(logl)
    sys.path.insert(0, str(binding.parent))
    import DDCalc as dd
    if Path(dd.__file__).resolve() != binding or Path(dd.DDCalc_library).resolve() != library:
        raise ValueError("binding resolved an unexpected file")
    mapped = {Path(line.split(maxsplit=5)[5]).resolve()
              for line in Path("/proc/self/maps").read_text().splitlines()
              if len(line.split(maxsplit=5)) == 6 and line.split(maxsplit=5)[5].startswith("/")}
    if library not in mapped or runtime not in mapped:
        raise ValueError("did not map the requested native library and Fortran runtime")
    rows = []
    try:
        detector = dd.InitExperiment("Xenon1T_2017")
        wimp = dd.InitWIMP()
        halo = dd.InitHalo()
        dd.SetWIMP_msigma(wimp, 100., 4e-9, -0.3e-9, 2e-5, 8e-5)
        for rho in (0.30, 0.15):
            dd.SetSHM(halo, rho, 235., 235., 550.)
            dd.CalcRates(detector, wimp, halo)
            m, s, c, ll = dd.Events(detector), dd.Signal(detector), dd.Background(detector), dd.LogLikelihood(detector)
            expect_signal = s0 * (rho / 0.30)
            expect_mean = expect_signal + b
            full_poisson = m * math.log(s + c) - (s + c) - math.lgamma(m + 1)
            expected_ll = ll0 if rho == .30 else n * math.log(expect_mean) - expect_mean - math.lgamma(n + 1)
            ds, dl, dp = s - expect_signal, ll - expected_ll, ll - full_poisson
            if n != m or m != 0 or c != b or c != .36 or not all(abs(x) <= TOL for x in (ds, dl, dp)):
                raise ValueError("native rate/likelihood gate failed")
            rows.append({"density_GeV_per_cm3": rho, "observed": m, "signal": s, "background": c,
                         "log_likelihood": ll, "signed_signal_delta": ds, "signed_logl_delta": dl,
                         "signed_poisson_delta": dp})
    finally:
        dd.FreeAll()
    density_delta = rows[1]["signal"] - .5 * rows[0]["signal"]
    if not abs(density_delta) <= TOL:
        raise ValueError("density half-rate gate failed")
    return {"status": "passed", "binding_sha256": BINDING, "static_reference_sha256": STATIC,
            "native_shared_sha256": digest(library), "loaded_runtime_sha256": digest(runtime),
            "absolute_tolerance": TOL, "signed_density_half_rate_delta": density_delta, "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ddcalc_root", type=Path)
    parser.add_argument("parent_native_stdout", type=Path)
    parser.add_argument("fortran_runtime", type=Path)
    a = parser.parse_args()
    print(json.dumps(run(a.ddcalc_root.resolve(), a.parent_native_stdout, a.fortran_runtime),
                     indent=2, allow_nan=False))
