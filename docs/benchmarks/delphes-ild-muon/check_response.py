"""Verify native Delphes muon response against independent HepMC input and ILD formulas."""
import argparse
import hashlib
import json
import math
from pathlib import Path

PARENT = "9eb41a2c8a19f35bfab0ffe24bef03ea11f481fa6ab3dbcde68946f747225989"
EFF = .99*.95
N_EVENTS = 128


def require(condition, msg):
    if not condition:
        raise ValueError(msg)


def read_truth(src):
    raw = src.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PARENT, "wrong archived HepMC bytes")
    groups, current = [], {}
    for line in raw.decode().splitlines():
        x = line.split()
        if not x:
            continue
        if x[0] == "E":
            if current:
                groups.append(current)
            current = {}
        if x[0] == "P" and int(x[3]) in (-13, 13) and int(x[-1]) == 1:
            pid = int(x[3])
            require(pid not in current, "unexpected duplicate truth charge")
            current[pid] = tuple(map(float,x[4:8]))
    groups.append(current)
    require(len(groups) == N_EVENTS and all(set(g) == {-13,13} for g in groups), "wrong truth sample")
    return groups


def check(inp, root_file, delphes_lib):
    truth = read_truth(inp)
    import ROOT
    ROOT.gROOT.SetBatch(True)
    require(ROOT.gSystem.Load(str(delphes_lib.resolve())) >= 0, "loading genuine Delphes DLL failed")
    data = ROOT.TFile.Open(str(root_file))
    require(data and not data.IsZombie(), "invalid native ROOT file")
    tree = data.Get("Delphes")
    require(tree and tree.GetEntries() == N_EVENTS, "wrong native ROOT entry count")
    n_central, n_matched, n_reco = 0,0,0
    max_dir,max_truth = 0.,0.
    z_values = []
    payload = hashlib.sha256()
    for k, base in enumerate(truth):
        require(tree.GetEntry(k) > 0, "failed reading native ROOT event")
        refs = [p for p in tree.Particle if int(p.Status)==1 and abs(int(p.PID))==13]
        ref = {int(p.PID):p for p in refs}
        require(len(refs) == 2 and ref.keys() == base.keys(), "ROOT truth IDs/status changed")
        for pid, expected in base.items():
            row = ref[pid]
            observed = (row.Px,row.Py,row.Pz,row.E)
            max_truth=max(max_truth,*[abs(a-b) for a,b in zip(observed,expected,strict=True)])
        reco={}
        for mu in tree.Muon:
            charge = int(mu.Charge)
            require(charge in {-1,1}, "wrong reconstructed charge")
            pid = -13*charge
            require(pid in ref and pid not in reco, "reco muon ID is ambiguous")
            linked=mu.Particle.GetObject()
            require(linked and int(linked.PID)==pid and int(linked.Status)==1, "wrong native truth link")
            reco[pid]=(float(mu.PT),float(mu.Eta),float(mu.Phi))
        payload.update(json.dumps([[pid,ref[pid].Px,ref[pid].Py,ref[pid].Pz,ref[pid].E]
                                   for pid in sorted(ref)],separators=(",",":")).encode())
        payload.update(json.dumps(sorted(reco.items()),separators=(",",":")).encode())
        n_reco+=len(reco)
        for pid, (px,py,pz,_) in base.items():
            pt=math.hypot(px,py); eta=math.asinh(pz/pt); phi=math.atan2(py,px)
            if abs(eta)>=.7 or pt<=20:
                continue
            n_central+=1
            if pid not in reco:
                continue
            n_matched+=1
            pt_new,eta_new,phi_new=reco[pid]
            require(math.isfinite(pt_new) and pt_new>0, "invalid reconstructed momentum")
            max_dir=max(max_dir,abs(eta_new-eta),abs(math.remainder(phi_new-phi,2*math.pi)))
            sigma=math.hypot(.001,1e-5*pt)
            var_log=math.log1p(sigma*sigma)
            z_values.append((math.log(pt_new/pt)+.5*var_log)/math.sqrt(var_log))
    data.Close()
    require(n_central >= 80 and n_matched >= 50, "insufficient central response sample")
    require(max_truth <= 2e-5 and max_dir <= 1e-5, "ROOT truth or reco angular identity changed")
    eff=n_matched/n_central
    eff_z=(eff-EFF)/math.sqrt(EFF*(1-EFF)/n_central)
    z_mean=math.fsum(z_values)/n_matched
    z_rms=math.sqrt(math.fsum(z*z for z in z_values)/n_matched)
    require(abs(eff_z)<=5 and abs(z_mean)*math.sqrt(n_matched)<=5 and .65<=z_rms<=1.35,
            "ILD card response benchmark failed")
    return dict(status="passed",root_version=ROOT.gROOT.GetVersion(),events=N_EVENTS,
                reco_muons=n_reco,central_truth_muons=n_central,central_matched_muons=n_matched,
                central_efficiency=eff,expected_efficiency=EFF,efficiency_signed_binomial_sigma=eff_z,
                standardized_logpt_mean=z_mean,standardized_logpt_rms=z_rms,max_truth_fourvector_delta_GeV=max_truth,
                max_matched_angle_delta=max_dir, physics_payload_sha256=payload.hexdigest())


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_hepmc",type=Path)
    ap.add_argument("delphes_root",type=Path)
    ap.add_argument("delphes_library",type=Path)
    a=ap.parse_args()
    print(json.dumps(check(a.input_hepmc,a.delphes_root,a.delphes_library),indent=2,allow_nan=False))
