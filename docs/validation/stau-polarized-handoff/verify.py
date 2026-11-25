"""Independent frozen particle stream audit; no detector output or event selection."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path


def check(path, reference):
    ids=set()
    weights=defaultdict(list)
    counts=Counter()
    products=Counter()
    max_mass_error=0.
    max_total=0.
    def mass2(q):
        return q[3]**2-math.fsum(v*v for v in q[:3])
    m_tau2=1.77686**2
    with gzip.open(path,"rt") as f:
        for row in f:
            d=json.loads(row)
            key=d["event_id"]
            if key in ids: raise ValueError("duplicate event identity")
            ids.add(key)
            proc,idx=key.split(":")
            if not 1<=int(idx)<=reference[proc]["native_count"]: raise ValueError("hard event index")
            w=d["weight_fb"]
            if not math.isfinite(w) or w<=0: raise ValueError("nonpositive nominal weight")
            weights[proc].append(w)
            counts[proc]+=1
            if len(d["taus"])!=2 or {t["pid"] for t in d["taus"]}!={-15,15}:
                raise ValueError("charge handoff")
            pp={1 if pid>0 else -1:p for pid,p in d["parents"]}
            for t in d["taus"]:
                p=t["p"]; ch=t["neutralino"]; h=pp[1 if t["pid"]>0 else -1]
                max_mass_error=max(max_mass_error,abs(mass2(p)-m_tau2),abs(mass2(ch)-1))
                if max(abs(h[j]-p[j]-ch[j]) for j in range(4))>1e-7:
                    raise ValueError("daughter sum does not reconstruct parent")
                if max(abs(p[j]-math.fsum(v[j] for _,v in t["products"])) for j in range(4))>1e-7:
                    raise ValueError("tau daughters do not close")
                products[tuple(sorted(abs(a) for a,_ in t["products"]))]+=1
            finals=[v for _,v in d["other_particles"]]+[v for t in d["taus"] for _,v in t["products"]]+[t["neutralino"] for t in d["taus"]]
            pp13=(0,0,0,13000)
            err=max(abs(math.fsum(v[j] for v in finals)-pp13[j]) for j in range(4))/13000
            max_total=max(max_total,err)
            if err>1e-8: raise ValueError("global beam conservation")
    if set(weights)!=set(reference): raise ValueError("incomplete process coverage")
    if any(not math.isclose(math.fsum(w),reference[k]["sigma_fb"],rel_tol=1e-12) for k,w in weights.items()):
        raise ValueError("selected weights not normalized")
    if max_mass_error>1e-7: raise ValueError("mass shells")
    return dict(file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),events=len(ids),
                by_process=dict(sorted(counts.items())),sum_weights_fb=math.fsum(x for l in weights.values() for x in l),
                unique_tau_stable_signatures=len(products), max_abs_mass2_error_gev2=max_mass_error,
                max_global_relative_momentum_error=max_total,detector="NOT_RUN")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("sample",type=Path)
    p.add_argument("reference",type=Path)
    a=p.parse_args()
    print(json.dumps(check(a.sample,json.loads(a.reference.read_text())["30"]["41324"]),indent=2,sort_keys=True))
