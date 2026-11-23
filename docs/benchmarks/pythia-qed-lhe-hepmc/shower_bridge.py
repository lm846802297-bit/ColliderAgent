"""Native Pythia LHE→HepMC3 stable truth projection; fixed benchmark only."""
import argparse
import gzip
import hashlib
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import tempfile

INPUT = "a327716b960989c32bcf34d8f59d7ddf3899f52a5ddbdf0478b5d329f7ab54fd"
LHE = "dcfc8bee00f318ba4c037a059bdafd531bdc0223d239e2c10f6e7aee459fc13e"
RATE_PB, ERROR_PB = 8.6845, 0.0038517
EVENTS, SEED = 128, 314159
MOM_TOL, RATE_TOL = 1e-5, 1e-7
CARD = (
    "Beams:frameType = 4", "PartonShowers:model = 1", "PartonLevel:ISR = off",
    "PartonLevel:MPI = off", "PartonLevel:FSR = on", "HadronLevel:all = off",
    "TimeShower:QCDshower = off", "TimeShower:QEDshowerByQ = off",
    "TimeShower:QEDshowerByGamma = off", "TimeShower:QEDshowerByOther = off", "Random:setSeed = on", f"Random:seed = {SEED}",
    "Print:quiet = on", "Next:numberShowInfo = 0", "Next:numberShowProcess = 0",
    "Next:numberShowEvent = 0",
)


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def vectors(p):
    return (p.px(), p.py(), p.pz(), p.e())


def check(beam, final):
    require(sorted((pid, s) for pid,s,_ in beam) == [(-11,4),(11,4)], "beam IDs or statuses changed")
    require(sorted((pid,s) for pid,s,_ in final if pid != 22) == [(-13,1),(13,1)]
            and all(s == 1 for _,s,_ in final), "stable particles or status changed")
    require(all(math.isfinite(x) for _,_,v in [*beam,*final] for x in v)
            and all(v[3] > 0 for _,_,v in [*beam,*final]), "non-physical energy or momentum")
    require(all(abs(v[3]-50.) <= MOM_TOL for _,_,v in beam), "wrong beam energy")
    require(all(abs(math.hypot(*v[:3])-v[3]) <= MOM_TOL
                for pid,_,v in final if pid == 22), "non-massless photon")
    delta = max(abs(sum(v[j] for _,_,v in beam)-sum(v[j] for _,_,v in final)) for j in range(4))
    require(delta <= MOM_TOL, "four-momentum closure failed")
    return delta


def generate(lhe, xml, out, fsr):
    import pythia8mc as p
    import pyhepmc as h
    require(Path(os.environ.get("PYTHIA8DATA", "")).resolve()==xml.resolve(),
            "set PYTHIA8DATA to the exact wheel XML path")
    py = p.Pythia(str(xml), False)
    commands = [*CARD, f"Beams:LHEF = {lhe}", "TimeShower:QEDshowerByL = "+("on" if fsr else "off")]
    for command in commands:
        require(py.readString(command), f"invalid Pythia setting: {command.split('=')[0]}")
    require(py.init(), "native Pythia initialization failed")
    run = h.GenRunInfo()
    run.weight_names = ["nominal_lhe_pb"]
    before, weights = [], []
    radiative, photons, hard_events = 0,0,0
    pythia_photon_status = set()
    with h.open(out, "w", precision=17) as f:
        for k in range(1, EVENTS+1):
            require(py.next(), "native Pythia event generation failed")
            ev = py.event
            incoming = [ev[1],ev[2]]
            require(all(x.status() == -12 and not x.isFinal() for x in incoming), "unexpected native beam status")
            stable = [x for x in ev if x.isFinal()]
            require(all(x.status() > 0 for x in stable), "unexpected native final status")
            beams = [(a.id(),4,vectors(a)) for a in incoming]
            final = [(a.id(),1,vectors(a)) for a in stable]
            check(beams,final)
            ps = [a for a in stable if a.id() == 22]
            require(fsr or not ps, "shower-off unexpectedly has photons")
            radiative += bool(ps)
            hard_events += any(a.e() > .001 for a in ps)
            photons += len(ps)
            pythia_photon_status.update(a.status() for a in ps)
            info = py.infoPython()
            require(info.lhaStrategy() == -4, "native LHE weight strategy changed")
            w = info.weight()
            require(abs(w-RATE_PB) <= RATE_TOL, "native nominal weight units or value changed")
            weights.append(w)
            event = h.GenEvent(run,h.Units.GEV,h.Units.MM)
            event.event_number = k
            event.weights = [w]
            xsec = h.GenCrossSection()
            xsec.set_cross_section(RATE_PB, ERROR_PB)
            event.cross_section = xsec
            vx = h.GenVertex()
            bp = [h.GenParticle(h.FourVector(*v),pid,s) for pid,s,v in beams]
            for a in bp:
                vx.add_particle_in(a)
            for pid,s,v in final:
                vx.add_particle_out(h.GenParticle(h.FourVector(*v),pid,s))
            event.add_vertex(vx)
            event.set_beam_particles(*bp)
            f.write(event)
            before.append(sorted([*beams,*final]))
    info = py.infoPython()
    require(info.nSelected()==info.nAccepted()==EVENTS and abs(info.sigmaGen()*1e9-RATE_PB) <= RATE_TOL,
            "native sample count or cross section changed")
    require(not fsr or hard_events > 0, "no resolved QED radiation in on-sample")
    return before, dict(native_cross_section_pb=info.sigmaGen()*1e9, avg_weight_pb=sum(weights)/EVENTS,
                        n_selected=info.nSelected(), n_accepted=info.nAccepted(), radiation_events=radiative, hard_photon_events=hard_events, photon_count=photons,
                        pythia_final_photon_status=sorted(pythia_photon_status))


def replay(path, before=None):
    import pyhepmc as h
    n,delta,delta_vector,rad = 0,0.,0.,0
    with h.open(path,"r") as f:
        for ev in f:
            n+=1
            require(ev.event_number == n and ev.momentum_unit == h.Units.GEV and ev.length_unit == h.Units.MM,
                    "HepMC event sequence or units changed")
            require(len(ev.vertices)==1 and len(ev.weights)==1 and abs(ev.weights[0]-RATE_PB)<=RATE_TOL
                    and abs(ev.cross_section.xsec()-RATE_PB)<=RATE_TOL
                    and abs(ev.cross_section.xsec_err()-ERROR_PB)<=RATE_TOL, "HepMC graph/normalization changed")
            v=ev.vertices[0]
            def row(p):
                q=p.momentum
                return p.pid,p.status,(q.px,q.py,q.pz,q.e)
            beam=[row(x) for x in v.particles_in]
            final=[row(x) for x in v.particles_out]
            require(len(ev.particles)==len(beam)+len(final), "orphaned HepMC particle")
            delta=max(delta,check(beam,final))
            if before is not None:
                for (p,s,v),(p0,s0,v0) in zip(sorted([*beam,*final]),before[n-1],strict=True):
                    require((p,s)==(p0,s0),"roundtrip native identity changed")
                    delta_vector=max(delta_vector,*[abs(a-b) for a,b in zip(v,v0,strict=True)])
            rad+=any(pid==22 for pid,_,_ in final)
    require(n==EVENTS and delta_vector <= 1e-10, "wrong HepMC record count or roundtrip precision")
    return dict(events=n, photon_events=rad, max_closure_GeV=delta, max_native_roundtrip_GeV=delta_vector)


def run(source, xml, out):
    require(version("pythia8mc")=="8.317.0" and version("pyhepmc")=="2.15.1", "wrong native tool versions")
    packed = source.read_bytes()
    require(digest_bytes(packed)==INPUT,"wrong exact parent LHE bytes")
    raw = gzip.decompress(packed)
    require(digest_bytes(raw)==LHE,"wrong decompressed LHE bytes")
    result={}
    with tempfile.TemporaryDirectory() as tmp:
        lhe=Path(tmp)/"parent.lhe"
        lhe.write_bytes(raw)
        for key,fsr in (("off",False),("on",True)):
            target=out/f"qed_fsr_{key}.hepmc"
            records,r=generate(lhe,xml,target,fsr)
            r["roundtrip"]=replay(target,records)
            require(r["roundtrip"]["photon_events"]==r["radiation_events"],"roundtrip photon counts differ")
            r["hepmc_sha256"]=digest_bytes(target.read_bytes())
            result[key]=r
    return {"parent_lhe_gzip_sha256":INPUT,"parent_uncompressed_sha256":LHE,
            "seed":SEED,"results":result}


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archived_lhe_gz",type=Path)
    ap.add_argument("pythia_xmldoc",type=Path)
    ap.add_argument("output_dir",type=Path)
    a=ap.parse_args()
    result = run(a.archived_lhe_gz, a.pythia_xmldoc, a.output_dir)
    (a.output_dir/"bridge_result.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
