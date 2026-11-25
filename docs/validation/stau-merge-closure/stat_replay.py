import argparse
import json
from pathlib import Path
from closure import run

p=argparse.ArgumentParser()
p.add_argument("rows",type=Path)
p.add_argument("split",type=Path)
p.add_argument("--all",action="store_true")
a=p.parse_args()
rows=json.loads(a.rows.read_text())
for scale, seeds in sorted(rows.items()):
    for seed, cases in sorted(seeds.items()):
        for k,r in sorted(cases.items()):
            # Recheck every affected native summary and one unaffected control per scale.
            if a.all or (int(k)==1 and int(seed)==41324) or abs(r["native_sigmaGen_fb"]/r["sigma_fb"]-1)>1e-8:
                run(a.split/f"p{k}.lhe",int(k),int(scale),int(seed),"combined",stats=True,jets=False)
