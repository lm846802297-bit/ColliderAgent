"""Validate preserved native DDCalc outputs without building or importing DDCalc."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re

REFERENCE_SHA = "9cb0d591fa33416ef6a88ee547a5984102a012823b2c404bbdb97a7012479d50"


def verify(native, official, reference):
    ref_bytes = reference.read_bytes()
    if sha256(ref_bytes).hexdigest() != REFERENCE_SHA:
        raise ValueError("wrong independent SHM reference bytes")
    ref = json.loads(ref_bytes)
    raw = [line.split() for line in native.read_text().splitlines()]
    if [r[0] for r in raw] != ["rate", "vmin", *(["eta"] * 18)]:
        raise ValueError("unexpected native record count or types")
    events = int(raw[0][1])
    signal, background, logl = map(float, raw[0][2:])
    demo = official.read_text().split("Example 2:", 1)[0]
    if "Example 1: Mixed SI and SD interactions at XENON1T (2017)" not in demo:
        raise ValueError("missing named upstream example")
    def demo_value(label):
        return float(re.search(r"^\s*" + re.escape(label) + r":\s*([+\-\d.Ee]+)", demo,
                               re.MULTILINE)[1])
    expected_events, expected_signal, expected_background, expected_logl = [
        demo_value(k) for k in ("Observed number of events", "Expected number of signal events",
                                 "Expected number of background events", "Log(likelihood)")]
    expo = signal + background
    poisson = events * math.log(expo) - expo - math.lgamma(events + 1)
    scalar_residuals = [signal - expected_signal, background - expected_background, logl - expected_logl]
    if (events != 0 or expected_events != 0 or background != .36
            or not math.isfinite(signal) or signal <= 0
            or not all(abs(r) <= 1e-10 for r in scalar_residuals)
            or not abs(logl - poisson) <= 1e-10):
        raise ValueError("rate or likelihood gate failed")
    vmin = float(raw[1][1])
    vmin_delta = vmin - ref["unit_control"]["correct_vmin_km_s"]
    if not abs(vmin_delta) <= 1e-9:
        raise ValueError("elastic recoil vmin gate failed")
    points = []
    for (_, b, v, eta), row in zip(raw[2:], ref["points"], strict=True):
        b, v, eta = map(float, (b, v, eta))
        if (b, v) != (row["boost_km_s"], row["vmin_km_s"]):
            raise ValueError("different halo point")
        delta = eta - row["galactic_shell_s_per_km"]
        if not abs(delta) <= 2e-12 or (v >= 544 + b and eta != 0.):
            raise ValueError("halo inverse speed gate failed")
        points.append(dict(boost_km_s=b, vmin_km_s=v, eta_s_per_km=eta,
                           signed_delta_s_per_km=delta))
    return dict(status="passed", observed_events=events, expected_signal=signal,
                fixed_background=background, log_likelihood=logl, signed_rate_deltas=scalar_residuals,
                signed_poisson_delta=logl - poisson, vmin_km_s=vmin, signed_vmin_delta_km_s=vmin_delta,
                max_eta_abs_delta_s_per_km=max(abs(r["signed_delta_s_per_km"]) for r in points),
                halo_points=points)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native", type=Path)
    parser.add_argument("official", type=Path)
    parser.add_argument("reference", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.native, args.official, args.reference), indent=2, allow_nan=False))
