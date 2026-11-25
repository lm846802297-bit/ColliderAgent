"""Strict audit of native hard events, without detector cuts or merging."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re


def audit(path):
    raw=path.read_bytes()
    lines=(gzip.decompress(raw) if path.suffix==".gz" else raw).decode("utf-8")
    result=collections.Counter()
    maxerr=0.
    for event in re.finditer(r"<event>\s*\n(.*?)</event>",lines,re.S):
        content=event.group(1).splitlines()
        n, proc=map(int, content[0].split()[:2])
        rows=[l.split() for l in content[1:1+n]]
        if len(rows)!=n or not all(len(row)==13 for row in rows):
            raise ValueError("bad event size")
        inc=[r for r in rows if int(r[1])==-1]
        fs=[r for r in rows if int(r[1])==1]
        parents=[r for r in fs if abs(int(r[0])) in (1000015,2000015)]
        partons=[r for r in fs if abs(int(r[0])) in (1,2,3,4,5,21)]
        if len(inc)!=2 or len(parents)!=2 or len(fs)!=len(partons)+2 or len(partons)>2:
            raise ValueError("bad external particle topology")
        if int(parents[0][0])!=-int(parents[1][0]) or any(abs(float(r[10])-280)>1e-7 for r in parents):
            raise ValueError("incorrect stau species or mass")
        l,r=([sum(float(row[k]) for row in entries) for k in range(6,10)]
             for entries in (inc,fs))
        maxerr=max(maxerr,max(abs(a-b) for a,b in zip(l,r))/l[3])
        state="L" if abs(int(parents[0][0]))==1000015 else "R"
        result[f"{state}{len(partons)}"]+=1
    if set(result) != {state+str(j) for state in "LR" for j in range(3)} or maxerr>1e-8:
        raise ValueError(f"missing channel or momentum error: {result}, {maxerr}")
    return dict(events=sum(result.values()),matrix_element_event_counts=dict(sorted(result.items())),
                max_scaled_momentum_residual=maxerr, sha256=hashlib.sha256(raw).hexdigest(),
                merging="NOT_RUN", detector="NOT_RUN", acceptance="hard_event_topology_only")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("lhe",type=Path)
    print(json.dumps(audit(p.parse_args().lhe),indent=2,sort_keys=True))
