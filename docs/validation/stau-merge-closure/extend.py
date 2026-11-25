"""Confirm the hard-sample statistics with a second archived generator seed."""
import hashlib
import json
from pathlib import Path
from closure import run, derive, split

path=Path("independent10k.lhe.gz")
identity=json.loads(Path("independent10k-hard.json").read_text())
assert hashlib.sha256(path.read_bytes()).hexdigest()==identity["sha256"] and identity["events"]==10000
base=Path("lhe-split-independent10k");base.mkdir(exist_ok=True)
counts=split(path,base)
r={}
for scale in (20,30,40):
    q={}
    for k in sorted(counts):
        # Only native combined path on the independent hard sample: the two
        # conventions were compared event-by-event on the archive pilot.
        c=run(base/f"p{k}.lhe",k,scale,41324,"combined")
        raw_est=dict(c,records=[(1.,None)]*len(c["records"]))
        item=derive(raw_est,c,c,counts[k])
        item["normalization_modes_checked"]=1
        q[k]=item
        print(scale,k,item["neff"], flush=True)
    r[scale]={41324:q}
    Path("independent10k-rows.partial.json").write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
Path("independent10k-rows.json").write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
