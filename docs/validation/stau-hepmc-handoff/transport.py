"""HepMC3 detector handoff for the frozen 280/1 GeV polarized stau run."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform

import pyhepmc as hep

INPUT_SHA = "ac20e8b056e16b98b19d566dc683f9658277393f321b21c864cc38241ea1614e"
WEIGHT = "matched_xsec_fb"
NOMINAL_TOTAL = 6.906428701209656
COUNTS = {1: 1753, 2: 747, 3: 808, 4: 338, 5: 397, 6: 173}
PROTON_E = 6500.0
PROTON_M = 0.93827208816
BEAM_P = math.sqrt((PROTON_E - PROTON_M) * (PROTON_E + PROTON_M))
BEAMS = [(2212, (0., 0., x * BEAM_P, PROTON_E)) for x in (1, -1)]
MAX_BEAM_RESIDUAL_GEV = 2.0e-5  # GeV: bound on global residual of the original hadronized record
INVIS = {12, 14, 16, 1000022}


def require(ok, label):
    if not ok:
        raise ValueError(label)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def key(row):
    c, i = map(int, row["event_id"].split(":"))
    require(c in COUNTS and 1 <= i < 10000 and
            row["event_id"] == f"{c}:{i}", "invalid event ID")
    return 10000*c+i


def spec(items):
    out = []
    for pid, p in items:
        xyz = tuple(map(float, p))
        require(pid != 0 and len(xyz) == 4 and all(map(math.isfinite, xyz))
                and (xyz[-1] > 0 or (pid == 22 and xyz == (0., 0., 0., 0.))), "invalid particle")
        out.append((pid, xyz))
    return out


def expected(row):
    staus = sorted(spec(row["parents"]))
    require(len(staus) == 2 and staus[0][0] == -staus[1][0]
            and abs(staus[0][0]) in {1000015, 2000015}, "invalid parent pair")
    stable = spec(row["other_particles"])
    require(not any(abs(a) in {15, 1000015, 2000015, 1000022}
                    for a, _ in stable), "untracked decay-chain particle")
    taus = {t["pid"]: t for t in row["taus"]}
    require(len(row["taus"]) == 2 and set(taus) == {-15, 15}, "tau pair")
    decays = []
    for s in staus:
        pid = 15 if s[0] > 0 else -15
        tr = taus[pid]
        t, n = spec([(pid, tr["p"]), (1000022, tr["neutralino"])])
        ds = spec(tr["products"])
        nu = [a for a, _ in ds if abs(a) == 16]
        require(nu == ([16] if pid > 0 else [-16]), "tau neutrino charge")
        decays.append((s, t, n, ds))
    w = float(row["weight_fb"])
    require(w > 0 and math.isfinite(w), "invalid weight")
    require(len(row["kt"]) == 2 and all(math.isfinite(v) for v in row["kt"]), "invalid jet metadata")
    return stable, decays, w


def particle(item, status):
    return hep.GenParticle(item[1], item[0], status)


def make_event(row, run):
    oth, decays, w = expected(row)
    evt = hep.GenEvent(hep.Units.GEV, hep.Units.MM)
    evt.run_info, evt.weights = run, [w]
    evt.event_number = key(row)
    evt.attributes["source_id"] = row["event_id"]
    evt.attributes["ckkwl_kt_d01_d12_gev"] = " ".join(repr(v) for v in row["kt"])
    primary = hep.GenVertex()
    evt.add_vertex(primary)
    for x in BEAMS:
        primary.add_particle_in(particle(x, 4))
    for x in oth:
        primary.add_particle_out(particle(x, 1))
    for s, t, n, ds in decays:
        ps, pt = particle(s, 2), particle(t, 2)
        sv, tv = hep.GenVertex(), hep.GenVertex()
        primary.add_particle_out(ps)
        sv.add_particle_in(ps)
        sv.add_particle_out(particle(n, 1))
        sv.add_particle_out(pt)
        tv.add_particle_in(pt)
        for x in ds:
            tv.add_particle_out(particle(x, 1))
        evt.add_vertex(sv)
        evt.add_vertex(tv)
    return evt


def four(p):
    v = p.momentum
    return v.px, v.py, v.pz, v.e


def identity(p):
    return p.pid, four(p)


def balance(a, b):
    return max(abs(math.fsum([*(x[j] for x in a), *(-x[j] for x in b)]))
               for j in range(4))


def verify_event(row, e):
    oth, decays, w = expected(row)
    require(e.event_number == key(row) and str(e.attributes["source_id"]) == row["event_id"], "source ID changed")
    require(list(e.weights) == [w] and e.weight_names == [WEIGHT], "event weight changed")
    require(str(e.attributes["ckkwl_kt_d01_d12_gev"]).split() == [repr(v) for v in row["kt"]],
            "jet metadata changed")
    require(e.momentum_unit == hep.Units.GEV and e.length_unit == hep.Units.MM, "units changed")
    require(len(e.vertices) == 5 and sorted(map(identity, e.beams)) == sorted(BEAMS)
            and all(p.status == 4 for p in e.beams), "projected primary vertex")
    prim = e.beams[0].end_vertex
    require(len(prim.particles_in) == 2 and all(v.position.is_zero() for v in e.vertices),
            "production position was invented")
    seen = []
    for s, t, n, ds in decays:
        p = next(x for x in prim.particles_out if x.pid == s[0])
        require(p.status == 2 and identity(p) == s, "stau changed")
        sv = p.end_vertex
        require(sv is not None and [identity(q) for q in sv.particles_in] == [s]
                and sorted(map(identity, sv.particles_out)) == sorted([t, n]), "stau daughters changed")
        pt = next(q for q in sv.particles_out if q.pid == t[0])
        nv = next(q for q in sv.particles_out if q.pid == n[0])
        require(pt.status == 2 and nv.status == 1 and nv.end_vertex is None, "decay status")
        tv = pt.end_vertex
        require(tv is not None and [identity(q) for q in tv.particles_in] == [t]
                and sorted(map(identity, tv.particles_out)) == sorted(ds)
                and all(q.status == 1 and q.end_vertex is None for q in tv.particles_out), "tau daughters changed")
        require(balance([s[1]], [t[1], n[1]]) < 1e-7 and
                balance([t[1]], [v for _, v in ds]) < 1e-7, "decay conservation")
        seen.extend([n, *ds])
    require(sorted(map(identity, (p for p in prim.particles_out if p.status == 1))) == sorted(oth),
            "primary stable particles changed")
    final = [identity(p) for p in e.particles if p.status == 1]
    require(sorted(final) == sorted(oth + seen) and
            len(e.particles) == 6 + len(final), "lost, duplicated, or nonphysical particle")
    residual = balance([v for _, v in BEAMS], [v for _, v in final])
    require(residual <= MAX_BEAM_RESIDUAL_GEV, "projected beams and final state disagree")
    met = [math.fsum(v[j] for a, v in final if abs(a) in INVIS) for j in (0, 1)]
    return residual, len(final), sum(abs(a) in INVIS for a, _ in final), math.hypot(*met)


def rows(p):
    with gzip.open(p, "rt", encoding="utf8") as f:
        yield from map(json.loads, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("report")
    args = ap.parse_args()
    require(hep.__version__ == "2.15.1" and sha(args.input) == INPUT_SHA, "source/tool version mismatch")
    require(not Path(args.output).exists(), "output already exists")
    require(str(args.output).endswith(".hepmc"), "uncompressed HepMC required during validation")
    draft = str(args.output) + ".partial"
    ri = hep.GenRunInfo()
    ri.weight_names = [WEIGHT]
    ri.tools = [("PhenoAgent", "280-1-tms30", "stau/tau ancestry projection; not full shower history")]
    with hep.open(draft, "w", precision=17) as f:
        for r in rows(args.input):
            f.write(make_event(r, ri))
    counts, weights, wmet = Counter(), [], []
    maxr, ns, ni, prev = 0.0, 0, 0, 0
    zero_photon_events = []
    with hep.open(draft) as f:
        for r in rows(args.input):
            e = f.read()
            k = key(r)
            require(e is not None and k > prev, "truncated or repeated event ID")
            maxerr, stable, invisible, met = verify_event(r, e)
            prev = k
            counts[k//10000] += 1
            weights.append(e.weights[0])
            wmet.append(e.weights[0]*met)
            maxr, ns, ni = max(maxr,maxerr), ns+stable, ni+invisible
            if any(p.status == 1 and p.pid == 22 and p.momentum.is_zero() for p in e.particles):
                zero_photon_events.append(r["event_id"])
        require(f.read() is None and dict(counts) == COUNTS, "event count disagreement")
    totalw = math.fsum(weights)
    require(abs(totalw-NOMINAL_TOTAL) < 1e-14, "nominal total mismatch")
    Path(draft).rename(args.output)
    rpt = {"status":"PASS", "classification":"native HepMC3 round-trip, detector NOT RUN",
           "python": platform.python_version(), "pyhepmc":hep.__version__,
           "source_sha256":INPUT_SHA, "native_sha256":sha(args.output),
           "native_bytes":Path(args.output).stat().st_size, "exact_vectors_and_weights":True,
           "events":len(weights), "counts_by_process":dict(counts), "tau_vertices":2*len(weights),
           "stau_vertices":2*len(weights), "stable_particles":ns, "invisible_particles":ni,
           "sum_weight_fb":totalw,"weight_normalization":"cross section in fb; do not divide by event count",
           "neff":totalw**2/math.fsum(w*w for w in weights),
           "truth_invisible_met_weighted_mean_gev":math.fsum(wmet)/totalw,
           "exact_zero_photon_events":zero_photon_events,
           "max_beam_to_final_component_residual_gev":maxr}
    Path(args.report).write_text(json.dumps(rpt,sort_keys=True,indent=2)+"\n")


if __name__ == "__main__":
    main()
