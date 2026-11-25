"""Factorized tau-ID/trigger composition audit on unchanged nominal Delphes."""
import argparse
from bisect import bisect_right
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

import ROOT
import cutflow as cf
from response_audit import ROOT_SHA

NAMES=('tau1_pt','tau2_pt','met','mt2')
GRID={'tau1_pt':(0,50,75,95,120,160,220,300,500),
      'tau2_pt':(0,40,50,60,75,95,120,160,220,500),
      'met':(0,75,110,150,200,250,350,500),
      'mt2':(0,40,60,70,80,100,150,200,300,500)}


def sha(p):
    with open(p,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def era_flags(a,b,met):
    return dict(low_early=a>95 and b>60,low_late=a>95 and b>75,
                high_early=a>50 and b>40 and met>150,
                high_late=a>75 and b>40 and met>150)


def stats(rows):
    norm=math.fsum(w for w,_ in rows)
    return dict(contributors=len(rows),weighted_fb=norm,
      weighted_events=norm*cf.LUMI,
      neff=norm**2/math.fsum(w*w for w,_ in rows),
      means={key:math.fsum(w*x[key] for w,x in rows)/norm for key in NAMES},
      prongs={str(i):math.fsum(w for w,x in rows if x['n3']==i)/norm for i in (0,1,2)},
      fractions={key:math.fsum(w for w,x in rows if p(x))/norm for key,p in {
        'met_window':lambda x:75<x['met']<150,
        'mt2_gt70':lambda x:x['mt2']>70,
        'tau2_60_to_75':lambda x:60<x['tau2_pt']<=75,
        'tau1_50_to_75':lambda x:50<x['tau1_pt']<=75}.items()})


def histogram(rows, grid, getter):
    weights=defaultdict(list)
    for w,x in rows:
        key=tuple(bisect_right(b, v)-1 for b,v in zip(grid,getter(x)))
        weights[key].append(w)
    return {k:(len(vals),math.fsum(vals)) for k,vals in weights.items()}


def contrast(a,b,p):
    na=math.fsum(w for w,_ in a); nb=math.fsum(w for w,_ in b)
    pa=math.fsum(w for w,x in a if p(x))/na
    pb=math.fsum(w for w,x in b if p(x))/nb
    ix=defaultdict(list)
    for w,x in a: ix[x['source_index']].append(-w*(p(x)-pa)/na)
    for w,x in b: ix[x['source_index']].append(w*(p(x)-pb)/nb)
    return dict(before=pa,after=pb,delta=pb-pa,paired_event_mc_sigma=math.sqrt(math.fsum(math.fsum(v)**2 for v in ix.values())))


def diagnostic(root,truth,lib,nominal,outdir):
    if sha(root)!=ROOT_SHA or sha(truth)!=cf.SOURCE_SHA:
        raise ValueError('wrong native inputs')
    if ROOT.gSystem.Load(lib)<0: raise ValueError('cannot load Delphes')
    source=ROOT.TFile.Open(root)
    native=source.Get('Delphes')
    raw=list(cf.rows(truth))
    assert len(raw)==int(native.GetEntries())==4216
    t17_expected=json.loads(Path(nominal).read_text())['cutflow']
    ds=defaultdict(list); original=defaultdict(list)
    for i,(e,r) in enumerate(zip(native,raw)):
        c,n=map(int,r['event_id'].split(':'))
        assert int(e.Event.At(0).Number)==10000*c+n
        w=r['weight_fb']
        bas,lo,hi,mt=cf.take(e,r)
        for key,cols in [('common',bas),('low',lo),('high',hi)]:
            for j,p in enumerate(cols): original[key,j].append(w*p)
        if not bas[2]>0: continue
        jets,_,_,_=cf.cutobjs(e)
        a,b=jets[:2]
        p=e.MissingET.At(0).P4()
        m2=cf.m2(a.v,b.v,p)
        assert math.isfinite(m2)
        x=dict(source_index=i,tau1_pt=a.pt,tau2_pt=b.pt,met=p.Pt(),mt2=m2,
               n3=int(a.tracks==3)+int(b.tracks==3))
        factors={'baseline':bas[2], 'medium_os':bas[3], 'common_final':bas[-1],
                 'low_trigger':lo[0], 'low_met':lo[1], 'low_tight':lo[2], 'low_pre_mt2':lo[-2],
                 'high_met_only':bas[-1]*(p.Pt()>150), 'high_trigger':hi[0], 'high_tight':hi[1], 'high_pre_mt2':hi[-2]}
        flags=era_flags(a.pt,b.pt,p.Pt())
        expect=lambda side:cf.HLT*((1-cf.LATE)*flags[side+'_early']+cf.LATE*flags[side+'_late'])
        assert abs(lo[0]-bas[-1]*expect('low'))<1e-14
        assert abs(hi[0]-bas[-1]*expect('high'))<1e-14
        for key in flags:
            factors[key+'_plateau']=bas[-1]*flags[key]
            if key.startswith('low'): factors[key+'_window']=bas[-1]*flags[key]*(75<p.Pt()<150)
        for name,f in factors.items():
            if f>0: ds[name].append((w*f,x))
    for k,values in original.items():
        name,j=k
        assert abs(math.fsum(values)*cf.LUMI-t17_expected[name][j]['ours'])<2e-12
    r={k:stats(v) for k,v in ds.items()}
    o=dict(status='diagnostic_not_atlas_response_calibration', nominal_sha=sha(nominal),
       contrasts={name:contrast(ds[a],ds[b],fun) for name,a,b,fun in [
           ('medium_mt2','baseline','medium_os',lambda x:x['mt2']>70),
           ('low_trigger_met_window','common_final','low_trigger',lambda x:75<x['met']<150),
           ('low_era_met_window','low_early_plateau','low_late_plateau',lambda x:75<x['met']<150),
           ('low_tight_mt2','low_met','low_tight',lambda x:x['mt2']>70),
           ('high_met_only_mt2','common_final','high_met_only',lambda x:x['mt2']>70),
           ('high_trigger_mt2','common_final','high_trigger',lambda x:x['mt2']>70),
           ('high_tight_mt2','high_trigger','high_tight',lambda x:x['mt2']>70)]},
       root_sha256=ROOT_SHA,truth_sha256=cf.SOURCE_SHA,nominal_cutflow_identity=True,stages=r)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'populations.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    for dims,fname in [([(k,) for k in NAMES],'spectra.csv'),
                         ([('tau2_pt','met'),('mt2','met')],'joint_spectra.csv')]:
        with (outdir/fname).open('w',newline='') as f:
            writer=csv.writer(f,lineterminator='\n')
            writer.writerow(['stage','variables','bin_low_gev','bin_high_gev','raw_contributors','weighted_fb','fraction_of_stage'])
            for keys in dims:
                g=[GRID[k] for k in keys]
                for stage,vals in sorted(ds.items()):
                    h=histogram(vals,g,lambda x:[x[k] for k in keys])
                    norm=r[stage]['weighted_fb']
                    assert abs(math.fsum(w for _,w in h.values())/norm-1)<1e-14
                    for b,(n,w) in sorted(h.items()):
                        assert min(b)>=0
                        low=[str(v[i]) for v,i in zip(g,b)]
                        high=[str(v[i+1]) if i+1<len(v) else 'inf' for v,i in zip(g,b)]
                        writer.writerow([stage,':'.join(keys),':'.join(low),':'.join(high),n,w,w/norm])


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ('root','truth','lib','nominal','outdir'): p.add_argument(k)
    diagnostic(*vars(p.parse_args()).values())
