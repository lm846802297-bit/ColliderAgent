"""Audit existing native fast response without rerunning or changing the signal cuts."""
import hashlib
import json
import math
from pathlib import Path
import sys

import ROOT
from filter_audit import visible,INVIS
import cutflow as cf

ROOT_SHA='b5e6d26d82d63acfe0949f1de8557befb7c8703670b8700fe283cce3d6f0a9f5'


def weighted(rows):
    scale=math.fsum(w for w,x in rows)
    mean=math.fsum(w*x for w,x in rows)/scale
    return dict(n=len(rows),sum_fb=scale,mean=mean,
                sigma=math.sqrt(math.fsum((w*(x-mean))**2 for w,x in rows))/scale,
                std=math.sqrt(math.fsum(w*(x-mean)**2 for w,x in rows)/scale))


def truth_met(r):
    xs=r['other_particles']+[(pid,v) for t in r['taus'] for pid,v in t['products']]
    xs+=[(1000022,t['neutralino']) for t in r['taus']]
    return [math.fsum(v[j] for pid,v in xs if abs(pid) in INVIS) for j in range(2)]


def band(x): return 0 if x<=75 else 1 if x<150 else 2


def match(t,js):
    v=visible(t['products'])
    if any(abs(p) in (12,14) for p,x in t['products']): return None
    p=math.hypot(*v[:2]); ee=cf.eta(v); ph=math.atan2(v[1],v[0])
    if p<=20 or abs(ee)>=2.5 or 1.37<=abs(ee)<=1.52: return None
    j=min(js,key=lambda a:math.hypot(a.eta-ee,cf.dphi(a.v.Phi(),ph)),default=None)
    ok=j is not None and j.charge==(1 if t['pid']<0 else -1) and math.hypot(j.eta-ee,cf.dphi(j.v.Phi(),ph))<.2
    return (p,ok,j.pt/p if ok else None)


def main():
    src,truth,lib,out=sys.argv[1:5]
    for p,h in [(src,ROOT_SHA),(truth,cf.SOURCE_SHA)]:
        with open(p,'rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=h: raise ValueError('wrong input')
    if ROOT.gSystem.Load(lib)<0: raise ValueError('cannot load Delphes')
    f=ROOT.TFile.Open(src); tr=f.Get('Delphes')
    a=list(cf.rows(truth))
    if len(a)!=tr.GetEntries() or len(a)!=4216: raise ValueError('count mismatch')
    mat=[[[] for i in range(3)] for j in range(3)]
    tau={q:{'match':[],'ratio':[]} for q in ('20-50','50-100','100+')}
    met=[]; tower_res=0.; window={'truth':[],'reco':[],'reco_minus_truth':[],'any_window_migration':[]}; nden=0
    for i,e in enumerate(tr):
        r=a[i]; c,k=map(int,r['event_id'].split(':'))
        if e.Event.At(0).Number!=10000*c+k: raise ValueError('event mismatch')
        w=r['weight_fb']; v=e.MissingET.At(0).P4(); mtruth=math.hypot(*truth_met(r)); mreco=v.Pt()
        tx=math.fsum(t.ET*math.cos(t.Phi) for t in e.Tower)
        ty=math.fsum(t.ET*math.sin(t.Phi) for t in e.Tower)
        tower_res=max(tower_res,abs(tx+v.Px()),abs(ty+v.Py()))
        met.append((w,mreco-mtruth)); js=cf.cutobjs(e)[0]
        matched=[match(t,js) for t in r['taus']]
        if all(x is not None and x[1] for x in matched) and len(js)==1:
            raise ValueError('shared reconstructed candidate; require one-to-one for efficiency')
        for vinfo in matched:
            if vinfo is None: continue
            p,matched,rsp=vinfo; b='20-50' if p<50 else '50-100' if p<100 else '100+'
            tau[b]['match'].append((w,matched))
            if matched: tau[b]['ratio'].append((w,rsp))
        _,low,_,_=cf.take(e,r)
        if low[0]>0:
            eff=w*low[0]; nden+=1
            mat[band(mtruth)][band(mreco)].append(eff)
            window['truth'].append((eff,75<mtruth<150))
            window['reco'].append((eff,75<mreco<150))
            window['reco_minus_truth'].append((eff,int(75<mreco<150)-int(75<mtruth<150)))
            window['any_window_migration'].append((eff,(75<mreco<150)!=(75<mtruth<150)))
    if tower_res>2e-3: raise ValueError(f'MET does not equal independent tower sum: {tower_res}')
    report={'status':'DIAGNOSTIC_NOT_ATLAS_RESPONSE_CALIBRATION','met_reco_minus_truth_gev':weighted(met),
            'tower_met_component_max_residual_gev':tower_res,'weight_low_trigger_stage_to_met_window':{k:weighted(v) for k,v in window.items()},
            'low_trigger_contributors':nden,'low_trigger_truth_vs_reco_met_band_matrix_fb':[[math.fsum(x) for x in y] for y in mat],
            'tau_matched_charge_response':{k:{q:{a:b for a,b in weighted(x).items() if a!='sigma'} for q,x in v.items()} for k,v in tau.items()}}
    Path(out).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')


if __name__=='__main__': main()
