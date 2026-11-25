"""CKKW-L normalization and post-shower first/second kT transition checks."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path

import pythia8mc as py
from ckkwl_smoke import split

INPUT_SHA = "b716b4e036b19dbe528a0f6242945ba04e17308103f935a9cc909fc3fdf85845"
EDGES = [0, 10, 20, 25, 35, 45, 60, 100, 200, 500, math.inf]
SEEDS = (41324,51997,70123)


def edges_bin(x):
    return next(i for i,b in enumerate(EDGES[1:]) if x < b)


def _kin(v):
    x,y,z,e=v
    return x*x+y*y, math.atan2(y,x), .5*math.log(max(1e-15,e+z)/max(1e-15,e-z))


def kt_transitions(vecs,R=.4):
    """Exclusive hadronic kT with beam removals, E-scheme and running max d."""
    p=list(vecs)
    h=list(map(_kin,p))
    transitions={}
    maxd=0.
    while p:
        d,i,j=min((z[0],k,-1) for k,z in enumerate(h))
        for a,(pt1,ph1,y1) in enumerate(h):
            for b in range(a):
                pt2,ph2,y2=h[b]
                dp=math.remainder(ph1-ph2,2*math.pi)
                score=min(pt1,pt2)*(dp*dp+(y1-y2)**2)/(R*R)
                if score<d: d,i,j=score,a,b
        maxd=max(maxd,d)
        if len(p)<=2: transitions[len(p)-1]=math.sqrt(maxd)
        if j>=0:
            p[j]=tuple(a+b for a,b in zip(p[i],p[j]))
            h[j]=_kin(p[j])
        p.pop(i);h.pop(i)
    return transitions.get(0,0.),transitions.get(1,0.)


def run(path, k, scale, seed, mode, stats=False, jets=True):
    estimate=mode=="estimate"
    p=py.Pythia("",False)
    mass=1000015 if k%2 else 2000015
    n=(k-1)//2
    settings=[
       "Tune:pp = 21","PDF:pSet = 13","Beams:frameType = 4",f"Beams:LHEF = {path}",
       "Random:setSeed = on",f"Random:seed = {seed}","Print:quiet = on",
       "Next:numberShowInfo = 0","Next:numberShowProcess = 0","Next:numberShowEvent = 0",
       f"Merging:Process = pp>{{stau-,{mass}}}{{stau+,{-mass}}}",
       "Merging:doKTMerging = on","Merging:nJetMax = 2",f"Merging:nRequested = {n}",
       f"Merging:TMS = {scale}",f"Merging:doXSectionEstimate = {'on' if estimate else 'off'}",
       f"Merging:includeWeightInXsection = {'on' if mode=='combined' else 'off'}",
       "PartonLevel:MPI = off","HadronLevel:all = off","BeamRemnants:primordialKT = off",
       "1000015:m0 = 280","2000015:m0 = 280","1000015:mayDecay = off","2000015:mayDecay = off",
    ]
    for setting in settings:
        if not p.readString(setting): raise ValueError(setting)
    if not p.init(): raise ValueError("native initialization failed")
    info=p.infoPython()
    if info.nProcessesLHEF()!=1: raise ValueError(f"wrong LHE interface: {info.lhaStrategy()} {info.nProcessesLHEF()}")
    raw_pb=info.sigmaLHEF(0)
    records=[]
    last_native_accept=0
    last_accept_selected=0
    for _ in range(100000):
        ok=p.next()
        info=p.infoPython()
        if info.atEndOfFile(): break
        if not ok: raise ValueError("unexpected native failure")
        if info.lhaStrategy()!=3: raise ValueError(f"wrong LHE strategy: {info.lhaStrategy()}")
        if info.nAccepted()!=last_native_accept:
            if info.nAccepted()!=last_native_accept+1:
                raise ValueError("native accepted count skipped")
            last_native_accept=info.nAccepted()
            last_accept_selected=info.nSelected()
        event_weight,merge_weight=info.weight(),info.mergingWeight()
        w=event_weight*merge_weight
        if not math.isfinite(w) or w<0: raise ValueError("invalid weight")
        if mode=="combined" and merge_weight!=1: raise ValueError("double-count weight path")
        if mode in ("estimate","split") and event_weight!=1: raise ValueError("expected unit LHE phase weight")
        transitions=None
        if mode=="combined" and w>0 and jets:
            e=p.event
            vecs=[(a.px(),a.py(),a.pz(),a.e()) for a in (e[i] for i in range(e.size()))
                  if a.isFinal() and abs(a.id()) in (1,2,3,4,5,21)
                  and a.pT()>1e-9 and abs(a.eta())<5]
            transitions=kt_transitions(vecs)
        records.append((w,transitions))
    else: raise ValueError("no EOF")
    if stats:
        print(f"FINAL-STAT {scale} {seed} {k}",flush=True)
        p.stat()
        print("END-FINAL-STAT",flush=True)
    return dict(rawpb=raw_pb,selected=info.nSelected(),accepted=info.nAccepted(),tried=info.nTried(),last_accept_selected=last_accept_selected,
                sigmaGen_fb=info.sigmaGen()*1e12, records=records)


def derive(estimate,split,combined,count):
    ws=[r[0] for r in combined["records"]]
    ww=[r[0] for r in split["records"]]
    nest=len(estimate["records"])
    if not (combined["selected"]==split["selected"]==estimate["selected"]==count):
        raise ValueError(f"nSelected disagrees with raw count: {count}; {[p['selected'] for p in (estimate,split,combined)]}")
    if not (len(ws)==len(ww)==nest):
        raise ValueError("pre-cut support disagreement")
    wdiff=max((abs(a-b) for a,b in zip(ws,ww)),default=0)
    unit=combined["rawpb"]*1000/count
    sumw=math.fsum(ws); combined_sig=unit*sumw
    split_sig=unit*math.fsum(ww)
    estimate_sig=estimate["rawpb"]*1000*nest/count
    two_pass=estimate_sig*sumw/nest
    sigma_disagreement=max(abs(combined_sig-split_sig),abs(combined_sig-two_pass))/combined_sig
    if wdiff>1e-10 or sigma_disagreement>1e-10:
        raise ValueError("native weight frontends or normalizations disagree")
    hs=[[0.]*(len(EDGES)-1) for _ in range(2)]
    h2=[[0.]*(len(EDGES)-1) for _ in range(2)]
    for weight,trans in combined["records"]:
        if not weight: continue
        for i,value in enumerate(trans):
            k=edges_bin(value)
            f=unit*weight
            hs[i][k]+=f;h2[i][k]+=f*f
    if max(abs(sum(h)-combined_sig) for h in hs)>1e-10:
        raise ValueError("histogram integral does not close")
    last=combined.get("last_accept_selected",count)
    corrected_native=combined["sigmaGen_fb"]*last/count
    numdiag=abs(corrected_native/combined_sig-1)
    return dict(sigma_fb=combined_sig,split_sigma_fb=split_sig,two_pass_sigma_fb=two_pass,
                post_cut_count=nest,neff=sumw**2/math.fsum(w*w for w in ws),
                sigma_convention_rel_diff=sigma_disagreement,native_sigmaGen_fb=combined["sigmaGen_fb"],
                estimate_native_sigmaGen_fb=estimate["sigmaGen_fb"],max_weight_diff=wdiff,
                native_last_accept_selected=last,native_count=count,
                native_snapshot_comparison_relative=numdiag,
                d01_d12_fb=hs,d01_d12_weight2_fb2=h2)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("--expected-sha256", default=INPUT_SHA)
    p.add_argument("--output",type=Path,default=Path("closure-rows.json"))
    p.add_argument("--seed",type=int,action="append",help="default: all three pilot seeds")
    a=p.parse_args()
    if hashlib.sha256(a.source.read_bytes()).hexdigest()!=a.expected_sha256: raise ValueError("unsealed input")
    folder=Path("lhe-split");folder.mkdir(exist_ok=True)
    counts=split(a.source,folder)
    runs={}
    for scale in (20,30,40):
        runs[scale]={}
        for seed in (a.seed or SEEDS):
            runs[scale][seed]={}
            for k in sorted(counts):
                path=folder/f"p{k}.lhe"
                row=derive(*(run(path,k,scale,seed,m) for m in ("estimate","split","combined")),counts[k])
                runs[scale][seed][k]=row
    a.output.write_text(json.dumps(runs,sort_keys=True,allow_nan=False,indent=2)+"\n")


if __name__=="__main__":
    main()
