"""Run native Pythia on stau LHE. Probe tau->pi nu with and without SPINUP."""
import argparse
import json
import math
from pathlib import Path
import statistics
import pythia8mc as py


def run(path, isr, n, pion_only=True):
    g=py.Pythia("",False)
    settings=[
      "Tune:pp = 21", "PDF:pSet = 13",
      "Beams:frameType = 4", f"Beams:LHEF = {path}",
      "Random:setSeed = on", "Random:seed = 271823",
      "Print:quiet = on", "Init:showChangedSettings = off",
      "Next:numberShowInfo = 0","Next:numberShowProcess = 0","Next:numberShowEvent = 0",
      f"PartonLevel:ISR = {'on' if isr else 'off'}",
      f"PartonLevel:MPI = {'off' if pion_only else 'on'}",
      f"PartonLevel:FSR = {'off' if pion_only else 'on'}",
      "BeamRemnants:primordialKT = off", "TimeShower:QEDshowerByL = off", 
      "TauDecays:mode = 5","TauDecays:externalMode = 0",
      "1000015:m0 = 400","2000015:m0 = 400","1000022:m0 = 80",
      "1000015:mayDecay = off","2000015:mayDecay = off","1000022:mayDecay = off",
    ]
    if pion_only:
        settings.extend(("15:onMode = off","15:onIfMatch = 16 -211"))
    for s in settings:
        if not g.readString(s): raise ValueError(s)
    if not g.init(): raise ValueError("Pythia init refused LHE")
    vals,pts=[],[]
    fail=0
    other_tau_pi=0
    hard_tau_count=0
    modes={}
    for _ in range(n):
        if not g.next():
            fail+=1
            continue
        ev=g.event
        h=[ev[i] for i in range(ev.size()) if abs(ev[i].id()) in (1000015,2000015)]
        if h:
            last={p.id():p for p in h}
            if len(last)!=2: raise RuntimeError("missing stau pair")
            pts.append(math.hypot(sum(p.px() for p in last.values()),sum(p.py() for p in last.values())))
        for i in range(ev.size()):
            t=ev[i]
            if abs(t.id())!=15 or t.isFinal(): continue
            daughter=[ev[j] for j in t.daughterList()]
            todo,visited=t.motherList(),set()
            parents=[]
            while todo:
                idx=todo.pop()
                if idx<=0 or idx in visited: continue
                visited.add(idx)
                mom=ev[idx]
                if abs(mom.id()) in (1000015,2000015):
                    parents.append(mom)
                elif abs(mom.id())==15:
                    todo.extend(mom.motherList())
            if not parents:
                other_tau_pi+=int(sorted(abs(d.id()) for d in daughter)==[16,211])
                continue
            if len({abs(p.id()) for p in parents})!=1: raise ValueError("ambiguous ancestry")
            theory=(1 if abs(parents[0].id())==2000015 else -1)
            if not any(abs(d.id())==16 for d in daughter): continue
            hard_tau_count+=1
            mode=str(sorted(abs(d.id()) for d in daughter))
            modes[mode]=modes.get(mode,0)+1
            pi=[d for d in daughter if abs(d.id())==211]
            if len(pi)!=1 or sorted(abs(d.id()) for d in daughter)!=[16,211]: continue
            m=t.m(); mpi=pi[0].m()
            e0=(m*m+mpi*mpi)/(2*m); p0=(m*m-mpi*mpi)/(2*m)
            pabs=math.sqrt(t.px()**2+t.py()**2+t.pz()**2)
            cos=(m*pi[0].e()-t.e()*e0)/(pabs*p0)
            if abs(cos)>1.000001: raise ValueError(f"bad pion angle {cos}")
            # Fold L/R and charge using the outgoing parent's species and tau charge.
            vals.append(theory*cos)
    return dict(input=str(path),isr=isr,total=n,successful=n-fail,failed=fail,
        pion_only=pion_only, pion_angles=len(vals),other_tau_pi=other_tau_pi,
        hard_tau_decays=hard_tau_count, decay_signatures=modes,mean_folded_cos=statistics.mean(vals) if vals else None,
        mean_se=statistics.stdev(vals)/math.sqrt(len(vals)) if len(vals)>1 else None,
        n_recoils_gt_1gev=sum(x>1 for x in pts),n_stau_pairs=len(pts),
        max_pair_pt_gev=max(pts,default=0))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--count",type=int,default=1024)
    ap.add_argument("--output",type=Path,default=Path("shower-result.json"))
    a=ap.parse_args()
    out=[run(Path(nm+".lhe"),False,a.count) for nm in ("longitudinal","reversed","no_tag")]
    out.append(run(Path("longitudinal.lhe"),True,a.count))
    out.append(run(Path("longitudinal.lhe"),True,a.count,pion_only=False))
    a.output.write_text(json.dumps(out,indent=2)+"\n")

if __name__=="__main__":
    main()
