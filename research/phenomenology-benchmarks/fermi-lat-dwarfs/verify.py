import json, numpy as np
from scipy.optimize import minimize_scalar, brentq
from recalc import *

def numeric_profile(c,t,p,sig):
    good=p>0
    # Per-energy bin interpolation with no pre-combined amplitude knots.
    x=t[good,:,2]; y=t[good,:,3]-t[good,0,3,None]
    p=p[good]
    if c==0:return 0.0
    top=min(4.,np.log10(np.min(x[:,-1]/(p*c))))
    zgrid=np.linspace(-4,top,129)
    def f(z):
        a=c*10**z
        return sum(np.interp(a*pp,xx,yy) for pp,xx,yy in zip(p,x,y))-.5*(z/sig)**2
    vals=np.array([f(z) for z in zgrid])
    maxima=(np.flatnonzero((vals[1:-1]>=vals[:-2])&(vals[1:-1]>=vals[2:]))+1).tolist()
    if vals[0]>vals[1]:maxima+=[0]
    if vals[-1]>vals[-2]:maxima+=[len(vals)-1]
    trials=[vals[0],vals[-1]]
    for i in maxima:
        res=minimize_scalar(lambda z:-f(z),bounds=(zgrid[max(0,i-2)],zgrid[min(len(vals)-1,i+2)]),method='bounded',options={'xatol':1e-11})
        trials.append(-res.fun)
    return max(trials)

def run():
    tables,grid,data=load(); out=[]
    for ch, masses in [('bb',(6,100,1000)),('tautau',(2,100,1000))]:
        for m in masses:
            p=flux(m,ch,grid,data)
            a,b=solve(targets(m,ch,tables,grid,data))
            def f(c):return sum(numeric_profile(c,tables[k],p*10**(j-19),sig) for k,(j,sig) in J.items())
            other=brentq(lambda c:f(c)-max(f(0),f(b))+1.355,b,2*a,xtol=1e-10)
            err=abs(other/a-1)
            assert err<1e-4,(ch,m,err)
            for c0 in [0,.5*a,a,1.5*a]:
                residual=abs(f(c0)-sum(profile(c0,*row) for row in targets(m,ch,tables,grid,data)))
                assert residual<2e-5,(ch,m,c0,residual)
            out.append(dict(channel=ch,mass_GeV=m,limit_cms=a*1e-26,direct_per_bin_limit_cms=other*1e-26,relative_difference=err))
    try: amplitude_table(tables['draco'],np.zeros(24))
    except ValueError:pass
    else:raise AssertionError('zero signal accepted')
    assert profile(1e30,*targets(100,'bb',tables,grid,data,True)[0])==-np.inf
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
