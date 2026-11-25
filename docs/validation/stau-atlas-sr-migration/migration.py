"""Frozen-event two-signal-region migration diagnostic."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import ROOT
import cutflow as cf
from filter_audit import defined_visible,event
from response_audit import truth_met,ROOT_SHA


def sha(path): 
    import hashlib
    with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def match_tau(jet,taus):
    vals=[]
    for t in taus:
        if jet.charge != (1 if t['pid'] < 0 else -1): continue
        if any(abs(pid) in {12,14} for pid,p in t['products']): continue
        v=ROOT.TLorentzVector(*defined_visible(t))
        dr=math.hypot(v.Eta()-jet.eta,cf.dphi(v.Phi(),jet.v.Phi()))
        if dr<.2: vals.append((dr,t['pid'],v))
    return min(vals,key=lambda u:u[0]) if vals else None


def transfer(data):
    # data = positive pre-mT2 weights and two masks on paired rows
    norm=math.fsum(w for w,_,_ in data)
    grid=[[math.fsum(w for w,a,b in data if a==i and b==j) for j in (False,True)] for i in (False,True)]
    p=(grid[0][1]-grid[1][0])/norm
    se=math.sqrt(math.fsum((w*(int(b)-int(a)-p))**2 for w,a,b in data))/norm
    return dict(precut_fb=norm,reco_fb=math.fsum(grid[1]),substituted_fb=grid[0][1]+grid[1][1],
                reco_efficiency=math.fsum(grid[1])/norm,substituted_efficiency=(grid[0][1]+grid[1][1])/norm,
                paired_delta_fraction=p,paired_se=se,
                lost_n=sum(a and not b for w,a,b in data),gained_n=sum(not a and b for w,a,b in data),
                matrix_fb=grid,net_yield_delta_139=p*norm*139)


def main():
    p=argparse.ArgumentParser()
    for n in ('root','truth','lib','baseline','output'): p.add_argument(n)
    x=p.parse_args()
    assert sha(x.truth)==cf.SOURCE_SHA and sha(x.root)==ROOT_SHA
    assert ROOT.gSystem.Load(x.lib)>=0
    f=ROOT.TFile.Open(x.root); d=f.Get('Delphes'); g=list(cf.rows(x.truth))
    assert len(g)==int(d.GetEntries())==4216
    labels={'common':cf.BASE,'low':cf.LOW,'high':cf.HIGH}
    filtered={k:[[] for t in v] for k,v in labels.items()}
    probes=defaultdict(list); ranges=defaultdict(list)
    pre=[]; missed=[]
    for r,e in zip(g,d):
        i,n=map(int,r['event_id'].split(':'))
        assert e.Event.At(0).Number==10000*i+n
        cut=event(r['taus']); parent=cut['parent']; vis=cut['visible_all']; w=r['weight_fb']
        assert not vis or parent
        co,lo,hi,v=cf.take(e,r)
        for k,group in [('common',co),('low',lo),('high',hi)]:
            for j,value in enumerate(group):
                alt=value if (k=='common' and j==0) or vis else 0
                filtered[k][j].append((w,value,alt))
        if not hi[-2]>0: continue
        wt=w*hi[-2]
        assert v is not None
        pre.append((wt,v>70.))
        jets=cf.cutobjs(e)[0]
        first=match_tau(jets[0],r['taus']); second=match_tau(jets[1],r['taus'])
        if first is None or second is None or first[1]==second[1]:
            missed.append((wt,v>70.))
            continue
        assert vis
        met=e.MissingET.At(0).P4()
        px,py=truth_met(r); tm=ROOT.TLorentzVector(px,py,0.,math.hypot(px,py))
        full_reco=cf.m2(jets[0].v,jets[1].v,met)
        assert full_reco==v
        z={'tau_truth':cf.m2(first[2],second[2],met),
           'met_truth':cf.m2(jets[0].v,jets[1].v,tm),
           'both_truth':cf.m2(first[2],second[2],tm)}
        for name,u in z.items():
            assert math.isfinite(u)
            probes[name].append((wt,v>70.,u>70.))
            if abs(v-70.)<10.: ranges[name].append((wt,v>70.,u>70.))
    base=json.loads(Path(x.baseline).read_text())
    table={}
    for name,rows in filtered.items():
        table[name]=[]
        for j,L in enumerate(rows):
            a=math.fsum(w*p for w,p,_ in L); b=math.fsum(w*q for w,_,q in L)
            delta=[w*(q-p) for w,p,q in L]
            ref=base['cutflow'][name][j]['ours']
            assert abs(ref-a*139.)<2e-12
            table[name].append(dict(label=labels[name][j],parent_fb=a,visible_fb=b,parent_events_139=a*139.,
                visible_events_139=b*139.,lost_n=sum(p>0 and q==0 for w,p,q in L),
                paired_absolute_sigma_events_139=139*math.sqrt(math.fsum(d*d for d in delta))))
    report=dict(status='DIAGNOSTIC_NOT_SR_VALIDATION',root_sha256=ROOT_SHA,
       truth_sha256=cf.SOURCE_SHA,reference_baseline_sha256=sha(x.baseline),
       cutflow=table,high_before_mt2_n=len(pre),high_matched_pair_n=len(probes['both_truth']),
       high_unmatched_pair_n=len(missed),high_unmatched_pair_fb=math.fsum(w for w,_ in missed),
       high_unmatched_pair_final_fb=math.fsum(w for w,v in missed if v),
       high_probe_all={k:transfer(t) for k,t in probes.items()},
       high_probe_within_10gev_of_reco_threshold={k:transfer(t) for k,t in ranges.items()},
       controls=dict(parent_replay_all_rows=True,no_visible_only_events=True))
    Path(x.output).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')


if __name__=='__main__': main()
