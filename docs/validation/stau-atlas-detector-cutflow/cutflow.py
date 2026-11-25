"""Apply ATLAS t17 order to native Delphes output with external exact weights."""
import argparse
from collections import Counter
from dataclasses import dataclass
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

import ROOT
from mt2 import mt2

LUMI = 139.
LATE = 58.5 / LUMI
HLT = 0.775
MED = {1: .75, 3: .60}
TIGHT = {1: .60, 3: .45}
BASE = ['Total','Generator filter','Baseline','Medium OS/third veto','b veto','Lepton veto','Z/H veto']
LOW = ['Trigger & offline cuts','75 < MET < 150','2 tight tau','Delta phi > 0.8','Delta R < 3.2','mT2 > 70']
HIGH = ['Trigger & offline cuts','At least 1 tight tau','Delta phi > 0.8','Delta R < 3.2','mT2 > 70']
SOURCE_SHA="ac20e8b056e16b98b19d566dc683f9658277393f321b21c864cc38241ea1614e"
REF_SHA="71c8ffa21d6163b35d13b8c1676f64bc5fe2d1f0a9dafa5eeeb7168ef628517b"


@dataclass
class Obj:
    v: object
    b: bool = False
    tracks: int = 0
    charge: int = 0

    @property
    def pt(self): return self.v.Pt()
    @property
    def eta(self): return self.v.Eta()


def require(ok, msg):
    if not ok: raise RuntimeError(msg)


def eta(p):
    pt=math.hypot(*p[:2])
    return math.asinh(p[2]/pt) if pt else math.inf


def dphi(a,b): return abs(math.remainder(a-b,2*math.pi))


def dr(a,b, y=False):
    diff = (a.v.Rapidity()-b.v.Rapidity()) if y else (a.eta-b.eta)
    return math.hypot(diff,dphi(a.v.Phi(),b.v.Phi()))


def obj(v): return Obj(v.P4())


def cutobjs(e):
    alltracks=[(obj(x),int(x.Charge)) for x in e.Track if x.PT > .5]
    tracks1=[(x,q) for x,q in alltracks if x.pt >= 1.]
    jts=[]; taus=[]
    for x in e.Jet:
        j=obj(x)
        j.b=bool(x.BTag)
        j.charge=int(x.Charge)
        if j.pt > 10 and abs(j.eta)<2.8:
            close=[q for t,q in tracks1 if dr(j,t)<=.2]
            j.tracks=len(close)
            if j.pt>20: jts.append(j)
            # Use only actual Delphes truth-matched reconstructed tau jets.
            # Medium/tight and electron rejection are added separately below.
            if (x.TauTag and j.pt>20 and abs(j.eta)<2.5 and
                not 1.37<=abs(j.eta)<=1.52 and j.tracks in MED and abs(j.charge)==1):
                require(j.charge==sum(close), 'track-count tag disagrees with saved tau charge')
                taus.append(j)
    el=[obj(x) for x in e.Electron if x.PT>17 and abs(x.Eta)<2.47]
    mu=[obj(x) for x in e.Muon if x.PT>14 and abs(x.Eta)<2.7]
    tau=[t for t in taus if not any(dr(t,l)<.2 for l in el+mu)]
    el=[x for x in el if not any(dr(x,m)<.01 for m in mu)]  # shared-track proxy
    jets=[j for j in jts if not (any(dr(j,l)<.2 for l in el) and not j.b)
          and not (j.tracks<3 and any(dr(j,l)<.2 for l in mu))]
    leps=[l for l in el+mu if not any(dr(l,j)<.4 for j in jets)]
    jets=[j for j in jets if not any(dr(j,t)<.2 for t in tau)]
    return sorted(tau,key=lambda x:-x.pt),jets,leps,len(alltracks)


def m2(a,b,met):
    return float(mt2(0.,a.Px(),a.Py(),0.,b.Px(),b.Py(),met.Px(),met.Py(),0.,0.,1e-9))


def probabilities(low,a,b,met):
    if low:
        p = HLT*( (1-LATE)*(a.pt>95 and b.pt>60) + LATE*(a.pt>95 and b.pt>75) )
        t = TIGHT[a.tracks]/MED[a.tracks] * TIGHT[b.tracks]/MED[b.tracks]
    else:
        p = HLT*(met>150)*((1-LATE)*(a.pt>50 and b.pt>40) + LATE*(a.pt>75 and b.pt>40))
        t = 1-(1-TIGHT[a.tracks]/MED[a.tracks])*(1-TIGHT[b.tracks]/MED[b.tracks])
    return p,t


def take(e,r):
    base=[1.]
    passes=all(math.hypot(*t['p'][:2])>15 and abs(eta(t['p']))<2.6 for t in r['taus'])
    base.append(float(passes))
    tau,jets,leps,nv=cutobjs(e)
    valid=passes and nv>=2 and len(tau)>=2 and tau[0].pt>50 and tau[1].pt>40
    base.append(float(valid))
    if not valid:
        return base+[0.]*4,[0.]*len(LOW),[0.]*len(HIGH),None
    a,b=tau[:2]
    base.append((.95**2*MED[a.tracks]*MED[b.tracks]) if len(tau)==2 and a.charge*b.charge<0 else 0.)
    base.append(base[-1]* (not any(j.b and abs(j.eta)<2.5 for j in jets)))
    base.append(base[-1]* (not leps))
    base.append(base[-1]* ((a.v+b.v).M()>120))
    v=e.MissingET.At(0).P4()
    val=v.Pt()
    p1,t1=probabilities(True,a,b,val)
    p2,t2=probabilities(False,a,b,val)
    one=base[-1]*p1
    two=base[-1]*p2
    dp=dphi(a.v.Phi(),b.v.Phi())>.8
    delta=dr(a,b,y=True)<3.2
    mt=m2(a.v,b.v,v) if ((one>0 and 75<val<150) or two>0) and dp and delta else None
    require(mt is None or math.isfinite(mt), 'nonfinite mT2')
    pm=mt is not None and mt>70
    l2=one*(75<val<150)
    l3=l2*t1
    h2=two*t2
    return base,[one,l2,l3,l3*dp,l3*dp*delta,l3*dp*delta*pm], [two,h2,h2*dp,h2*dp*delta,h2*dp*delta*pm],mt


def rows(rf):
    with gzip.open(rf,'rt') as f:
        yield from map(json.loads,f)


def validate_root_truth(e,r):
    actual=[p for p in e.Particle if abs(p.PID)==15 and p.Status==2]
    require(len(actual)==2,'reader lost tau history')
    taus={t['pid']:t for t in r['taus']}
    for q in actual:
        data=taus[int(q.PID)]
        require(q.D1>=0 and q.D2>=q.D1,'native tau daughter index')
        native=[e.Particle.At(i) for i in range(q.D1,q.D2+1)]
        a=sorted(data['products'],key=lambda x:(x[0],x[1][-1]))
        b=sorted(native,key=lambda p:(p.PID,p.E))
        require(len(a)==len(b),'native tau multiplicity changed')
        for (pid,mom),p in zip(a,b):
            require(pid==p.PID and max(abs(x-y)/max(1.,abs(x)) for x,y in zip(mom,[p.Px,p.Py,p.Pz,p.E])) < 2e-7,'daughter lost in detector reader')


def statistics_rows(aligned, groups, table):
    out={}
    for name,names,indices in groups:
        data=[]
        for j,(stage,idx) in enumerate(zip(names,indices)):
            x=[wt*e[name][j] for wt,e in aligned]
            y=math.fsum(x); rms=math.sqrt(math.fsum(v*v for v in x)); n=sum(z>0 for z in x)
            ref=table['values'][idx]['y'][2]
            ref_y=float(ref['value']); s_raw=ref.get('errors',[{'symerror':''}])[0]['symerror']; s=float(s_raw) if s_raw else None
            dat=dict(step=stage,hepdata_row=idx,ours=y,mc_sigma=rms,atlas=ref_y,atlas_mc_sigma=s,
                     positive_contributors=n,neff=(y/rms)**2 if rms else 0.,
                     our_acceptance=y/math.fsum(w for w,_ in aligned),atlas_acceptance=ref_y/float(table['values'][0]['y'][2]['value']))
            if j==0 and name!='common':
                before=math.fsum(w*e['common'][-1] for w,e in aligned)
                ref_before=float(table['values'][6]['y'][2]['value'])
            elif j:
                before=data[-1]['ours']; ref_before=data[-1]['atlas']
            else:
                before=y;ref_before=ref_y
            dat["step_eff"]=y/before if before else None
            dat["atlas_step_eff"]=ref_y/ref_before
            dat["yield_ratio"]=y/ref_y
            dat["diagnostic_within_gate"]=None if s is None else abs(y-ref_y)<=max(2*math.hypot(s,rms),.2*ref_y)
            data.append(dat)
        out[name]=data
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root');p.add_argument('truth');p.add_argument('reference');p.add_argument('output')
    p.add_argument('--lib',required=True);p.add_argument('--seed',required=True,type=int)
    a=p.parse_args()
    for f,h in [(a.truth,SOURCE_SHA),(a.reference,REF_SHA)]:
        with open(f,'rb') as b: require(hashlib.file_digest(b,'sha256').hexdigest()==h,f'wrong input {f}')
    with open(a.reference) as f: ref=json.load(f)
    ROOT.gROOT.SetBatch(True)
    require(ROOT.gSystem.Load(a.lib)>=0,'load native Delphes')
    rf=ROOT.TFile.Open(a.root); tr=rf.Get('Delphes')
    require(tr and tr.GetEntries()==4216,'native output lost input events')
    expected=list(rows(a.truth))
    require(len(expected)==tr.GetEntries(),'number mismatch')
    aligned=[]; overlaps=0; allmt=[]; truth_pass=0;weight_res=0.
    for j,e in enumerate(tr):
        r=expected[j];c,i=map(int,r['event_id'].split(':')); w=float(r['weight_fb'])
        require(len(e.Event)==1 and int(e.Event.At(0).Number)==10000*c+i,'native event ID mismatch')
        weight_res=max(weight_res,abs(float(e.Event.At(0).Weight)/w-1))
        require(weight_res<6e-8,'native event weight mismatch beyond f32')
        validate_root_truth(e,r); truth_pass+=1
        common,low,high,m=take(e,r)
        require(all(math.isfinite(x) and 0<=x<=1 for x in common+low+high),'invalid probability')
        require(all(u>=v for z in (common,[common[-1],*low],[common[-1],*high]) for u,v in zip(z,z[1:])),'non-monotonic cutflow')
        overlaps+=int(low[-1]>0 and high[-1]>0)
        if m is not None: allmt.append(m)
        aligned.append((w*LUMI,{'common':common,'low':low,'high':high}))
    require(overlaps==0,'signal regions overlap')
    grp=[('common',BASE,range(7)),('low',LOW,range(8,14)),('high',HIGH,range(15,20))]
    o=dict(status='DIAGNOSTIC_NATIVE_FAST_SIM_NOT_ATLAS_FULL_SIM',seed=a.seed,events=len(aligned),
           exact_source_weights=True,sum_weight_fb=math.fsum(w for w,_ in aligned)/LUMI,
           native_weight_float_relative_max=weight_res,native_decays_checked=2*truth_pass,
           signal_region_overlap=overlaps,reference_sha256=REF_SHA,root_version=ROOT.gROOT.GetVersion(),
           input_sha256=SOURCE_SHA, count_mt2=len(allmt),mt2_median_gev=statistics.median(allmt) if allmt else None,
           cutflow=statistics_rows(aligned,grp,ref),
           skipped=['full detector calibration','control regions','limit'])
    Path(a.output).write_text(json.dumps(o,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':
    main()
