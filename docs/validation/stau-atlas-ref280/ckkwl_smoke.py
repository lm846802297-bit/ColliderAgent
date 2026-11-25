"""Native CKKW-L plumbing controls, with stable staus and fixed raw input."""
import argparse
from collections import defaultdict
import gzip
import json
import math
from pathlib import Path
import re

import pythia8mc as py


def split(source, outdir):
    content=gzip.decompress(source.read_bytes()).decode("utf-8")
    header=content.split("<init>",1)[0]
    init=content.split("<init>",1)[1].split("</init>",1)[0].strip().splitlines()
    beam=init[0].split()
    assert beam[8:]==["-4","6"]
    proc={int(l.split()[-1]):l.strip() for l in init[1:7]}
    events=defaultdict(list)
    weights=set()
    for block in re.findall(r"<event>\s*\n(.*?)</event>",content,re.S):
        fields=block.splitlines()[0].split()
        assert len(fields)==6
        n,k=int(fields[0]),int(fields[1])
        assert n==4+(k-1)//2
        weights.add(float(fields[2]))
        fields[2]="1.0"
        events[k].append("<event>\n"+" ".join(fields)+"\n"+block.partition("\n")[2]+"</event>\n")
    assert len(weights)==1 and set(proc)==set(events)==set(range(1,7))
    beam[8:]=["3","1"]
    for k in range(1,7):
        row=proc[k].split()
        row[2]="1.0"
        (outdir/f"p{k}.lhe").write_text(header+"<init>\n"+" ".join(beam)+"\n"+" ".join(row)
                       +"\n</init>\n"+"".join(events[k])+"</LesHouchesEvents>\n")
    return {k:len(v) for k,v in events.items()}


def native(path, k, tms, estimate):
    g=py.Pythia("",False)
    mass=1000015 if k%2 else 2000015
    n=(k-1)//2
    opts=["Tune:pp = 21","PDF:pSet = 13", "Beams:frameType = 4", f"Beams:LHEF = {path}",
          "Random:setSeed = on","Random:seed = 41324","Print:quiet = on",
          "Init:showChangedSettings = off","Next:numberShowInfo = 0","Next:numberShowProcess = 0",
          "Next:numberShowEvent = 0","PartonLevel:MPI = off","HadronLevel:all = off",
          f"Merging:Process = pp>{{stau-,{mass}}}{{stau+,{-mass}}}",
          "Merging:doKTMerging = on","Merging:nJetMax = 2",f"Merging:nRequested = {n}",
          f"Merging:TMS = {tms}", "Merging:includeWeightInXsection = on",
          f"Merging:doXSectionEstimate = {'on' if estimate else 'off'}",
          "1000015:m0 = 280","2000015:m0 = 280","1000015:mayDecay = off","2000015:mayDecay = off"]
    for x in opts:
        if not g.readString(x): raise ValueError(x)
    if not g.init(): raise RuntimeError("Pythia init failed")
    weights=[]
    errors=0
    for i in range(2000):
        ok=g.next()
        info=g.infoPython()
        if info.atEndOfFile(): break
        if not ok:
            errors+=1
            continue
        w=info.weight()
        if not math.isfinite(w): raise ValueError("nonfinite merging weight")
        weights.append(w)
    else:
        raise RuntimeError("loop never reached EoF")
    return dict(scale_gev=tms,process=k,estimation_phase=estimate,successful=len(weights),
       veto_or_trial_failure=errors,weights_nonzero=sum(w!=0 for w in weights),
       weight_min=min(weights,default=None),weight_max=max(weights,default=None))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    args=p.parse_args()
    d=Path("lhe-split");d.mkdir(exist_ok=True)
    counts=split(args.source,d)
    out=[native(d/f"p{k}.lhe",k,tms,est) for tms in (20.,40.) for k in counts for est in (True,False)]
    Path("ckkwl-result.json").write_text(json.dumps(dict(counts=counts,trials=out,
        validity="interface-smoke-only; no validated matched cross section or detector response"),sort_keys=True,indent=2)+"\n")


if __name__=="__main__":
    main()
