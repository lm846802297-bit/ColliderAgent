import numpy as np
from scipy.special import lambertw
from scipy.optimize import brentq, minimize_scalar
from pathlib import Path
import csv

J=dict(bootes_I=(18.8,.22),canes_venatici_II=(17.9,.25),carina=(18.1,.23),coma_berenices=(19,.25),draco=(18.8,.16),fornax=(18.2,.21),hercules=(18.1,.25),leo_II=(17.6,.18),leo_IV=(17.9,.28),sculptor=(18.6,.18),segue_1=(19.5,.29),sextans=(18.4,.27),ursa_major_II=(19.3,.28),ursa_minor=(18.8,.19),willman_1=(19.1,.31))
M=[2,4,6,8,10,25,50,80.3,91.2,100,150,176,200,250,350,500,750,1000,1500,2000,3000,5000,7000,10000]
X=np.linspace(-9.98,-.02,250)
CHAN={'bb':1, 'tautau':3,'mumu':6}
BASE=Path(__file__).resolve().parent
LN10=np.log(10)
def load(root=BASE):
    tables={k:np.loadtxt(root/'official'/f'like_{k}.txt').reshape(24,25,4) for k in J}
    grid=tables['draco'][:,0,:2]
    assert all(np.array_equal(t[:,:,0],np.broadcast_to(grid[:,0,None],(24,25))) and np.array_equal(t[:,:,1],np.broadcast_to(grid[:,1,None],(24,25))) and np.all(np.diff(t[:,:,2],axis=1)>0) and np.all(t[:,0,2]==0) for t in tables.values())
    return tables,grid,np.loadtxt(root/'gammamc_dif.dat.pin').reshape(12,24,250)

def flux(m,ch,grid,data):
    if not 2<=m<=10000 or ch not in CHAN: raise ValueError("Unsupported mass or channel")
    w=np.array([np.interp(m,M,d) for d in data[CHAN[ch]].T])
    nodes,weights=np.polynomial.legendre.leggauss(4)
    out=[]
    for lo,hi in grid:
        hi=min(hi,1e3*m)
        if hi<=lo:out.append(0.);continue
        knots=1e3*m*10**X
        # Include all interpolation breakpoints and the physical endpoint.
        edge=np.r_[lo,knots[(knots>lo)&(knots<hi)],hi]
        mid=(edge[1:]+edge[:-1])/2
        d=np.diff(edge)/2
        xy=np.log10((mid[:,None]+d[:,None]*nodes)/(1e3*m))
        ww=np.interp(xy,X,w)
        tail=xy>X[-1]
        ww[tail]=w[-1]+(xy[tail]-X[-1])*(w[-1]-w[-2])/(X[-1]-X[-2])
        out.append(float(d @ (ww @ weights)))
    return np.array(out)*(1e-26*1e19/(8*np.pi*m*m))

def amplitude_table(t,p):
    good=p>0
    if not good.any():raise ValueError("zero in-band signal")
    x=t[good,:,2]/p[good,None]
    xy=np.unique(x[x<=min(x[:,-1])])
    y=np.sum([np.interp(xy,xx,yy-yy[0]) for xx,yy in zip(x,t[good,:,3])],axis=0)
    return xy,y

def profile(c,x,y,sig):
    if c==0:return y[0]
    if sig==0:
        if not x[0]<=c<=x[-1]:return -np.inf
        return np.interp(c,x,y)
    z=np.log10(x[1:]/c)
    ymax=np.max(y[1:]-.5*(z/sig)**2)
    slopes=np.diff(y)/np.diff(x)
    warg=-sig**2*LN10**2*c*slopes
    roots=[]
    for k in (0,-1):
        h=(warg>=-1/np.e)&((warg<0) if k==-1 else True)
        zs=-lambertw(warg[h],k).real/LN10
        zz=c*10**zs
        ok=(zz>=x[:-1][h])&(zz<=x[1:][h])
        if ok.any():
            v=np.interp(zz[ok],x,y)-.5*(zs[ok]/sig)**2
            roots.append(v.max())
    return max([ymax]+roots)

def solve(inputs, engine=profile):
    def f(c):return sum(engine(c,*row) for row in inputs)
    # Explicit grid before local maximization, including the physical null.
    qs=np.r_[0,np.geomspace(1e-5,1e8,100)]
    ys=np.array([f(q) for q in qs]); j=np.argmax(ys)
    if j==len(qs)-1:raise ValueError("MLE outside scan")
    if j==0: best=0.;mx=ys[0]
    else:
        opt=minimize_scalar(lambda c:-f(c),bounds=(qs[j-1],qs[j+1]),method='bounded',options={'xatol':1e-11})
        best=opt.x;mx=-opt.fun
    d=f(best)-mx+1.355
    assert abs(d-1.355)<1e-10
    idx=np.flatnonzero((qs>best)&(ys<mx-1.355))
    if not len(idx):raise ValueError("missing upper crossing")
    return brentq(lambda c:f(c)-mx+1.355,best,qs[idx[0]],xtol=1e-10),best

def targets(m,ch,tables,grid,data,fixj=False):
    p=flux(m,ch,grid,data)
    return [(*amplitude_table(tables[k],p*10**(j-19)),0 if fixj else sig) for k,(j,sig) in J.items()]

if __name__=='__main__':
    data=load()
    for ch in CHAN:
        rows=np.loadtxt(BASE/'official'/f'limits_{ch}.txt')
        for m,*vals in rows:
            a,b=solve(targets(m,ch,*data))
            print(ch,m,a*1e-26,vals[-1],a*1e-26/vals[-1]-1,b,flush=True)
