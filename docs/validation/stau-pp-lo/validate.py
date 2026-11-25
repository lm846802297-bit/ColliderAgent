"""Validate the three raw LHE streams and the native trial summary."""
import json
import math
from pathlib import Path
import re
import numpy as np


def parse(path):
    body=Path(path).read_text()
    for block in re.findall(r"<event>\s*(.*?)\s*</event>",body,re.S):
        rows=[line.split() for line in block.splitlines()]
        assert rows[0][:3]==["8","1","1.0"]
        assert len(rows)==9 and all(len(row)==13 for row in rows[1:])
        yield rows[1:]


def signature(e):
    return [row[:-1] for row in e]


def check_raw():
    count=0
    max_rel=0.
    for a,b,c in zip(*(parse(n+".lhe") for n in ("longitudinal","reversed","no_tag")),strict=True):
        assert signature(a)==signature(b)==signature(c)
        p=np.array([[float(x) for x in row[6:10]] for row in a])
        ids=[int(r[0]) for r in a]
        assert ids[0]==-ids[1] and 1<=abs(ids[0])<=5 and ids[2]==-ids[3]
        assert abs(ids[2]) in (1000015,2000015)
        assert ids[4:]==[15,1000022,-15,1000022]
        for i in range(8):
            mass=(0.,0.,400.,400.,1.77686,80.,1.77686,80.)[i]
            assert abs(p[i,3]**2-p[i,:3]@p[i,:3]-mass**2)<1e-7
        for i,j in (((0,1),(2,3)),((2,),(4,5)),((3,),(6,7))):
            v=p[list(i)].sum(axis=0); w=p[list(j)].sum(axis=0)
            max_rel=max(max_rel,float(np.max(np.abs(v-w)))/v[3])
        for k in (4,6):
            assert a[k][-1] in ("1","-1") and int(a[k][-1])==-int(b[k][-1]) and c[k][-1]=="9"
        assert all(a[k][-1]==b[k][-1]==c[k][-1]=="9" for k in (0,1,2,3,5,7))
        count+=1
    assert count==2048 and max_rel<1e-12
    return max_rel


def verify():
    p=json.loads(Path("pp-result.json").read_text())
    assert p["accepted"] and p["max_rel_diff"]<.001 and p["largest_pdf_positivity_shift"]<.001
    mu=json.loads(Path("shower-result.json").read_text())
    assert len(mu)==5
    assert all(row["successful"]==row["total"]==1024 and row["n_stau_pairs"]==1024
               and row["hard_tau_decays"]==2048 for row in mu)
    assert all(row["pion_angles"]==2048 for row in mu[:4])
    assert all(row["n_recoils_gt_1gev"]==0 for row in mu[:3])
    assert mu[3]["n_recoils_gt_1gev"]>512
    for row,ref in zip(mu,[1/3,-1/3,0,1/3]):
        assert abs(row["mean_folded_cos"]-ref)<4*row["mean_se"]
    assert 0<mu[4]["pion_angles"]<2048
    assert len(mu[4]["decay_signatures"])>=5
    return {"status":"PASS", "max_lhe_conservation_scaled":check_raw(),
            "scope":"Born+PDF integration and native shower/LHE longitudinal tau-spin handoff only"}


if __name__=="__main__":
    print(json.dumps(verify(),indent=2))
