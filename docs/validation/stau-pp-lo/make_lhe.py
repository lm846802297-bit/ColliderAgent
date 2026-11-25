"""Weighted proposal pool -> equal-weight smoke-test LHE. Not a production sample."""
import argparse
from contextlib import ExitStack
import json
import math
from pathlib import Path
import random
from integrate_pp import PDF, channel_weights, LMIN, S
from stau_born import M_STAU, M_TAU, M_CHI, decay, direction, rest_momentum, boost

BEAM = 6500.


def zboost(p,y):
    c,s=math.cosh(y),math.sinh(y)
    return (c*p[0]+s*p[3],p[1],p[2],s*p[0]+c*p[3])


def longitudinal(parent, tau, y):
    # Spin eigenaxis in parent rest frame, then exact boost to the incoming beam frame.
    pstar=rest_momentum(M_STAU,M_TAU,M_CHI)
    estar=math.hypot(pstar,M_TAU)
    u=[v/M_STAU for v in parent[1:]]
    # Inverse parent boost; only the angular components are needed.
    factor=sum(x*a for x,a in zip(tau[1:],u))/(1+parent[0]/M_STAU)-tau[0]
    unit=[(x+a*factor)/pstar for x,a in zip(tau[1:],u)]
    pure=zboost(boost((pstar/M_TAU,*(estar*x/M_TAU for x in unit)),parent),y)
    lab=zboost(tau,y)
    norm=math.sqrt(sum(x*x for x in lab[1:]))
    p=2*M_STAU*pstar/(M_STAU**2-M_TAU**2-M_CHI**2)
    val=p*M_TAU*pure[0]/norm
    if abs(val)>1+1e-9: raise ValueError("unphysical longitudinal spin component")
    return min(1.,max(-1.,val))


def line(pid,status,mom,cols,p,m,spin):
    e,x,y,z=p
    return f"{pid} {status} {mom[0]} {mom[1]} {cols[0]} {cols[1]} {x:.16e} {y:.16e} {z:.16e} {e:.16e} {m:.16e} 0.0 {spin}"


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count",type=int,default=2048)
    ap.add_argument("--pool",type=int,default=16384)
    a=ap.parse_args()
    pdf=PDF("pdf_bridge.so",".")
    result=json.loads(Path("pp-result.json").read_text())
    if not result["accepted"]: raise ValueError("quadrature not accepted")
    rng=random.Random(740641)
    cumulative,points=[],[]
    sw,sw2=0.,0.
    for _ in range(a.pool):
        l=LMIN*rng.random()
        y=-l*(rng.random()-.5)
        t=math.exp(l)
        x1,x2=math.exp(l/2+y),math.exp(l/2-y)
        terms=[(state,pid,ori,val) for state in "LR"
              for pid,ori,val in channel_weights(pdf,x1,x2,400.,t*S,state)]
        w=sum(v[-1] for v in terms)*LMIN*l
        sw+=w
        sw2+=w*w
        cumulative.append(sw)
        points.append((y,x1,x2,t,terms))
    sigma=sum(result["final_total_fb"])
    sd=math.sqrt(max(0.,(sw2-sw*sw/a.pool)/(a.pool*(a.pool-1))))
    if abs(sw/a.pool-sigma)>5*sd: raise ValueError("proposal total outside 5 SE")
    idxs=rng.choices(range(a.pool),cum_weights=cumulative,k=a.count)
    diagnostics=[]
    with ExitStack() as stack:
        files=[(nm,stack.enter_context(open(nm+".lhe","w"))) for nm in ("longitudinal","reversed","no_tag")]
        for _,f in files:
            f.write(f'<LesHouchesEvents version="1.0">\n<header></header>\n<init>\n2212 2212 6500 6500 0 0 0 0 3 1\n{sigma/1000:.16e} 0.0 1.0 1\n</init>\n')
        for ii in idxs:
            y,x1,x2,t,terms=points[ii]
            state,ip,ori,_=rng.choices(terms,weights=[p[-1] for p in terms])[0]
            ip=ip if ori==0 else -ip
            e=math.sqrt(t*S)
            while True:
                c=rng.uniform(-1,1)
                if rng.random()<1-c*c: break
            p=tuple(rest_momentum(e,M_STAU,M_STAU)*d for d in direction(c,rng.uniform(0,2*math.pi)))
            staus=[(e/2,*p),(e/2,*(-x for x in p))]
            decays=[decay(s,rng) for s in staus]
            hel=[]
            for i,(s,(tau,chi)) in enumerate(zip(staus,decays)):
                pol=longitudinal(s,tau,y)*(1 if state=="R" else -1)*(1 if i==0 else -1)
                hel.append((pol,1 if rng.random()<(1+pol)/2 else -1))
            diagnostics.extend(abs(x[0]) for x in hel)
            c1,c2=((501,0),(0,501)) if ip>0 else ((0,501),(501,0))
            sid=1000015 if state=="L" else 2000015
            fixed=[line(ip,-1,(0,0),c1,(BEAM*x1,0,0,BEAM*x1),0,9),
                   line(-ip,-1,(0,0),c2,(BEAM*x2,0,0,-BEAM*x2),0,9)]
            fixed.extend(line(pid,2,(1,2),(0,0),zboost(s,y),M_STAU,9)
                         for pid,s in zip((sid,-sid),staus))
            for nm,f in files:
                f.write(f'<event>\n8 1 1.0 400.0 {1/128:.16e} 0.130\n')
                for row in fixed: f.write(row+'\n')
                for k,(tau,chi) in enumerate(decays):
                    h=hel[k][1] if nm=="longitudinal" else (-hel[k][1] if nm=="reversed" else 9)
                    f.write(line(15 if k==0 else -15,1,(k+3,k+3),(0,0),zboost(tau,y),M_TAU,h)+'\n')
                    f.write(line(1000022,1,(k+3,k+3),(0,0),zboost(chi,y),M_CHI,9)+'\n')
                f.write('</event>\n')
        for _,f in files: f.write('</LesHouchesEvents>\n')
    print(json.dumps(dict(n_events=a.count,pool=a.pool,seed=740641,
        sigma_pool_fb=sw/a.pool,sigma_pool_stderr_fb=sd,reference_fb=sigma,
        unique_pool_kinematics=len(set(idxs)),proposal_effective_count=sw**2/sw2,
        helicity_magnitude_bounds=[min(diagnostics),max(diagnostics)]),indent=2))


if __name__=="__main__":
    main()
