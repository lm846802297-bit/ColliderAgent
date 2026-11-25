"""Paired tau–MET response based on existing native detector outputs."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import ROOT
import cutflow as cf
from response_audit import truth_met
from migration import match_tau, transfer

PINS={
  34025:"b5e6d26d82d63acfe0949f1de8557befb7c8703670b8700fe283cce3d6f0a9f5",
  34026:"f2296769271e0434669b3e364d9afb4ca7126126a3cb228514eb573bbe8d7e68",
  34027:"bb0c6dc34f4d0556e70d0ea0dd81545d76d014b0ac1359fbdaff973e9552e913",
}


def sha(p):
    with open(p,"rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()


def project(u,x): return (u[0]*x[0]+u[1]*x[1],-u[1]*x[0]+u[0]*x[1])


def summary(rows):
    n=math.fsum(w for w,x,y in rows)
    mx=math.fsum(w*x for w,x,y in rows)/n
    my=math.fsum(w*y for w,x,y in rows)/n
    vx=math.fsum(w*(x-mx)**2 for w,x,y in rows)/n
    vy=math.fsum(w*(y-my)**2 for w,x,y in rows)/n
    cv=math.fsum(w*(x-mx)*(y-my) for w,x,y in rows)/n
    vu=math.fsum(w*((x+y)-(mx+my))**2 for w,x,y in rows)/n
    if abs(vu-(vx+vy+2*cv))>1e-9: raise ValueError('variance closure')
    return dict(n=len(rows),weight_fb=n,tau_mean_gev=mx,met_mean_gev=my,
        tau_sigma_gev=math.sqrt(vx),met_sigma_gev=math.sqrt(vy),
        met_plus_tau_sigma_gev=math.sqrt(vu),covariance_gev2=cv,
        rho=cv/math.sqrt(vx*vy))


def process(root, f, seed, lib):
    if sha(root)!=PINS[seed] or sha(f)!=cf.SOURCE_SHA:
        raise ValueError('native input mismatch')
    if ROOT.gSystem.Load(lib)<0: raise ValueError('load detector ROOT library')
    src=ROOT.TFile.Open(str(root)); objects=src.Get('Delphes'); truth=list(cf.rows(f))
    if len(truth)!=int(objects.GetEntries()) or len(truth)!=4216: raise ValueError('event count')
    cov=defaultdict(lambda:[[],[]]); windows=defaultdict(list); all_base=defaultdict(list); match_base=defaultdict(list)
    closure=0.
    for r,e in zip(truth,objects):
        k,i=map(int,r['event_id'].split(':'))
        assert e.Event.At(0).Number==10000*k+i
        common,low,high,_=cf.take(e,r)
        if not common[-1]>0: continue
        w=r['weight_fb']; reco=e.MissingET.At(0).P4()
        pt_true=truth_met(r)
        q=math.hypot(*pt_true)
        if q==0.: raise ValueError('truth axis undefined; record separately')
        ax=(pt_true[0]/q,pt_true[1]/q)
        jets=cf.cutobjs(e)[0]; a,b=jets[:2]
        flags={'common':w*common[-1],
               'low_trigger_before_window':w*low[0],
               'high_tau_threshold_before_met':w*common[-1]*cf.HLT*
                  ((1-cf.LATE)*(a.pt>50 and b.pt>40)+cf.LATE*(a.pt>75 and b.pt>40))}
        for s,wt in flags.items():
            if wt>0: all_base[s].append(wt)
        aa,bb=match_tau(a,r['taus']),match_tau(b,r['taus'])
        if aa is None or bb is None or aa[1]==bb[1]: continue
        pa,pb=aa[2],bb[2]
        u=((a.v.Px()-pa.Px())+(b.v.Px()-pb.Px()),(a.v.Py()-pa.Py())+(b.v.Py()-pb.Py()))
        D=(reco.Px()-pt_true[0],reco.Py()-pt_true[1])
        U=project(ax,u); V=project(ax,D)
        adj=(reco.Px()+u[0],reco.Py()+u[1])
        dp=project(ax,(adj[0]-pt_true[0],adj[1]-pt_true[1]))
        closure=max(closure,*(abs(x+y-z) for x,y,z in zip(U,V,dp)))
        mag=math.hypot(*adj)
        grp='truth_met_'+('lt75' if q<75 else '75to150' if q<150 else 'ge150')
        flags[grp]=flags['common']
        for s,wt in flags.items():
            if wt<=0: continue
            match_base[s].append(wt)
            for h in (0,1): cov[s][h].append((wt,U[h],V[h]))
        if flags['low_trigger_before_window']:
            windows['low_75to150'].append((flags['low_trigger_before_window'],75<reco.Pt()<150,75<mag<150))
        if flags['high_tau_threshold_before_met']:
            windows['high_gt150'].append((flags['high_tau_threshold_before_met'],reco.Pt()>150,mag>150))
    if closure>1e-11: raise ValueError('momentum sign closure')
    return dict(seed=seed,root_sha256=PINS[seed],truth_sha256=cf.SOURCE_SHA,
                paired_covariance={s:{'parallel':summary(v[0]),'perpendicular':summary(v[1])} for s,v in cov.items()},
                matching={s:{'held_contributors':len(v),'matched_contributors':len(match_base[s]),
                            'matched_weight_fraction':math.fsum(match_base[s])/math.fsum(v)} for s,v in all_base.items()},
                balanced_probe_windows={s:transfer(v) for s,v in windows.items()},max_projected_closure_gev=closure,
                status='simulation_diagnostic_not_atlas_joint_calibration')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('detector_dir');p.add_argument('truth');p.add_argument('lib');p.add_argument('output')
    a=p.parse_args()
    z=[process(Path(a.detector_dir)/f'detector-{k}.root',a.truth,k,a.lib) for k in PINS]
    Path(a.output).write_text(json.dumps(z,indent=2,sort_keys=True)+'\n')
