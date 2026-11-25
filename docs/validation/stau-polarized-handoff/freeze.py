"""Isolate hadronization and angularly correct native tau decays from shower RNG."""
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import random
import types
import statistics as st

import pythia8mc as py

M,CHI,TAU=280.,1.,1.77686
PSTAR=math.sqrt((M-CHI-TAU)*(M+CHI+TAU)*(M-CHI+TAU)*(M+CHI-TAU))/(2*M)
ET=math.hypot(PSTAR,TAU)
EC=math.hypot(PSTAR,CHI)
POL=2*M*PSTAR/(M*M-TAU*TAU-CHI*CHI)
ARCHIVE=Path("../pheno-stau-merge-closure-20261125")
SOURCE_SHA="81e1cb64e29b31709587599b9359438863e67ddc4902df7b4c3cc11026e9f368"


def boost(v,parent,mass):
    px,py,pz,e=v
    bx,by,bz,pe=parent
    u=(bx/mass,by/mass,bz/mass)
    d=sum(a*b for a,b in zip((px,py,pz),u))
    g=pe/mass
    return (*(a+b*(e+d/(g+1)) for a,b in zip((px,py,pz),u)),g*e+d)


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def rotate(v,z):
    ref=(0.,0.,1.) if abs(z[2])<.9 else (1.,0.,0.)
    x=cross(ref,z); m=math.sqrt(sum(t*t for t in x))
    x=tuple(t/m for t in x)
    y=cross(z,x)
    return (*(a*v[0]+b*v[1]+c*v[2] for a,b,c in zip(x,y,z)),v[3])


def vector(p):
    return (p.px(),p.py(),p.pz(),p.e())


def residual(p,children):
    return max(abs(x-math.fsum(q[j] for q in children)) for j,x in enumerate(p))/max(1.,p[3])


def gun(polarization, pion_only):
    g=py.Pythia("",False)
    settings=["ProcessLevel:all = off","Print:quiet = on","TauDecays:mode = 3",
       f"TauDecays:tauPolarization = {polarization:.16g}","15:m0 = 1.77686"]
    if pion_only:
        settings+=["15:onMode = off","15:onIfMatch = 16 -211"]
    for o in settings:
        if not g.readString(o): raise ValueError(o)
    if not g.init(): raise RuntimeError("tau gun init")
    return g


def tau_decay(g,pid,seed,z,parent):
    g.rndm.init(seed)
    g.event.reset()
    ix=g.event.append(pid,1,0,0,0.,0.,PSTAR,ET,TAU)
    if not g.moreDecays(): raise RuntimeError("tau gun failed")
    if g.event[ix].isFinal(): raise RuntimeError("tau survived")
    ev=g.event
    particles=[]
    for j in range(1,ev.size()):
        a=ev[j]
        if a.isFinal():
            vv=vector(a)
            particles.append((a.id(),vv,boost(rotate(vv,z),parent,M)))
    t=boost((*(PSTAR*a for a in z),ET),parent,M)
    if residual(t,[x[2] for x in particles])>1e-9:
        raise ValueError("tau vertex failed conservation")
    return particles


def pion_angle(parts):
    if sorted(abs(x[0]) for x in parts)!=[16,211]:
        raise ValueError("expected tau -> pi nu")
    v=next(q[1] for q in parts if abs(q[0])==211)
    pz=v[2]
    en=v[3]
    pzrest=(ET*pz-PSTAR*en)/TAU
    e_rest=(ET*en-PSTAR*pz)/TAU
    px,py=v[:2]
    return pzrest/math.sqrt(px*px+py*py+pzrest*pzrest)


def inspect_source():
    src=(ARCHIVE/"closure.py").read_bytes()
    if hashlib.sha256(src).hexdigest()!=SOURCE_SHA:
        raise ValueError("nominal source integrity")
    text=src.decode()
    old="def run(path, k, scale, seed, mode, stats=False, jets=True):"
    marker="        records.append((w,transitions))"
    if text.count(old)!=1 or text.count(marker)!=1: raise ValueError("hook locations")
    text=text.replace(old,old.replace("jets=True","jets=True, hook=None"))
    text=text.replace(marker,"        if hook is not None and w>0: hook(p, info.nSelected(), raw_pb, w, transitions)\n"+marker)
    m=types.ModuleType("validated_shower_with_hook")
    exec(compile(text,"closure.py","exec"),m.__dict__)
    return m


def main():
    global ARCHIVE
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--per-channel",type=int,default=64)
    a.add_argument("--output",default="frozen-polarized.jsonl.gz")
    a.add_argument("--archive",type=Path,default=ARCHIVE)
    x=a.parse_args()
    ARCHIVE=x.archive
    reference=json.loads((ARCHIVE/"independent10k-rows.json").read_text())["30"]["41324"]
    lhe=ARCHIVE/"independent10k.lhe.gz"
    if hashlib.sha256(lhe.read_bytes()).hexdigest()!="614ba091937eb45849dd0c9dcc20267280c0f962fe4265f9e5224c6e2812b4cb": raise ValueError("LHE hash")
    c=inspect_source()
    sub=Path("lhe-split")
    sub.mkdir(exist_ok=True)
    counts=c.split(lhe,sub)
    all_guns={sign:gun(sign*POL,False) for sign in (-1,1)}
    pg={sign:gun(sign*POL,True) for sign in (-1,0,1)}
    acc={}
    angles={mode:[] for mode in ("expected","opposite","zero")}
    all_weights=[]
    records=0
    with open(x.output,"wb") as stream, gzip.GzipFile(filename="",mode="wb",mtime=0,fileobj=stream) as out:
        for k,N in sorted(counts.items()):
            kept=[]
            ref=reference[str(k)]
            baseline=[]
            def cb0(p,i,pb,w,dk):
                if x.per_channel and len(baseline)>=x.per_channel:return
                e=p.event
                baseline.append((i,pb,w,dk,tuple((e[j].id(),vector(e[j])) for j in range(e.size()) if e[j].isFinal())))
            raw0=c.run(sub/f"p{k}.lhe",k,30,41324,"combined",hook=cb0)
            def cb(p,i,pb,w,dk):
                if x.per_channel and len(kept)>=x.per_channel:return
                e=p.event
                unhad=tuple((e[j].id(),vector(e[j])) for j in range(e.size()) if e[j].isFinal())
                expected=baseline[len(kept)]
                if (i,pb,w,dk,unhad)!=expected:
                    raise ValueError(f"event correspondence changed for {k}:{i}")
                spins=1 if k%2==0 else -1
                state=p.rndm.getState()
                try:
                    if not p.forceHadronLevel(): raise RuntimeError("hadronization failed")
                finally:
                    p.rndm.setState(state)
                had=[(e[j].id(),vector(e[j])) for j in range(e.size()) if e[j].isFinal()]
                parents=[(pid,pv) for pid,pv in had if abs(pid) in (1000015,2000015)]
                if sorted(parents)!=sorted((pid,pv) for pid,pv in unhad if abs(pid) in (1000015,2000015)):
                    raise ValueError("hadronization changed stau momenta")
                other=[(pid,pv) for pid,pv in had if abs(pid) not in (1000015,2000015)]
                taus=[]
                for n,(pid,pv) in enumerate(sorted(parents)):
                    qpid=15 if pid>0 else -15
                    r=random.Random(10000000*k+10*i+n)
                    z0=r.uniform(-1,1);a=r.uniform(0,2*math.pi);s=math.sqrt(1-z0*z0)
                    z=(s*math.cos(a),s*math.sin(a),z0)
                    seed=r.randrange(1,900000000)
                    t=boost((*(PSTAR*b for b in z), ET),pv,M)
                    ch=boost((*(-PSTAR*b for b in z),EC),pv,M)
                    if residual(pv,[t,ch])>1e-10: raise ValueError("stau vertex")
                    for mode,sgn in (("expected",spins),("opposite",-spins),("zero",0)):
                        pion=tau_decay(pg[sgn],qpid,seed,z,pv)
                        angles[mode].append(spins*pion_angle(pion))
                    full=tau_decay(all_guns[spins],qpid,seed,z,pv)
                    taus.append(dict(pid=qpid,p=t,products=[(a,c) for a,_,c in full],neutralino=ch))
                finals=[p for _,p in other]+[v for t in taus for _,v in t["products"]]+[t["neutralino"] for t in taus]
                whole=tuple(math.fsum(v[j] for _,v in had) for j in range(4))
                before=tuple(math.fsum(v[j] for _,v in unhad) for j in range(4))
                hres=residual(before,[v for _,v in had])
                if hres>1e-8: raise ValueError(f"hadronization conservation: {hres}")
                err=residual(whole,finals)
                if err>1e-9: raise ValueError("frozen event final-state conservation")
                weight=pb*1000*w/N
                rec=dict(event_id=f"{k}:{i}",weight_fb=weight,kt=dk,parents=parents,
                         other_particles=other,taus=taus,residual=err,hadronization_residual=hres)
                out.write((json.dumps(rec,separators=(",",":"),allow_nan=False)+"\n").encode())
                kept.append((i,w,weight,err))
            raw=c.run(sub/f"p{k}.lhe",k,30,41324,"combined",hook=cb)
            if raw["records"]!=raw0["records"]: raise ValueError(f"shower stream changed for {k}")
            sigma=raw["rawpb"]*1000*math.fsum(w for w,_ in raw["records"])/N
            if abs(sigma-ref["sigma_fb"])>1e-12 or raw["selected"]!=N or len(kept)!=len(baseline):
                raise ValueError(f"weight or count disagreement {k} {sigma} {ref['sigma_fb']}")
            if not x.per_channel and not math.isclose(math.fsum(z[2] for z in kept),sigma,rel_tol=1e-13):
                raise ValueError("event output sum does not close")
            all_weights.append(sigma)
            records+=len(kept)
            acc[k]=dict(sigma_fb=sigma,written_events=len(kept),max_residual=max(z[-1] for z in kept))
    means={key:dict(mean=st.mean(v),se=st.stdev(v)/math.sqrt(len(v))) for key,v in angles.items()}
    for k,ori in (("expected",1),("opposite",-1),("zero",0)):
        if abs(means[k]["mean"]-ori*POL/3)>5*means[k]["se"]:
            raise ValueError(f"tau pion angular gate failed: {means}")
    print(json.dumps(dict(written_events=records,global_sigma_fb=math.fsum(all_weights),by_class=acc,
                          angles=means,spin_magnitude=POL,sha256=hashlib.sha256(Path(x.output).read_bytes()).hexdigest()),indent=2))

if __name__=="__main__":
    main()
