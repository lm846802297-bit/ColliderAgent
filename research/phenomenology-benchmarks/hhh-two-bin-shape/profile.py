"""Point-versus-point Asimov profile statistic, native Poisson + Gaussian auxiliaries."""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logit, xlogy
N=np
def fit(n,s,b,ps,pb,ws,wb,two):
    def expectation(z):
        S=s*np.exp(.15*z[0]); B=b*np.exp(.20*z[1])
        if not two:return np.array([S+B])
        p=expit(logit(ps)+ws/(ps*(1-ps))*z[2])
        q=expit(logit(pb)+wb/(pb*(1-pb))*z[3])
        return np.array([S*(1-p)+B*(1-q),S*p+B*q])
    def jac(z):
        lam=expectation(z)
        S=s*np.exp(.15*z[0]); B=b*np.exp(.20*z[1])
        if two:
            pslope=ws/(ps*(1-ps)); p=expit(logit(ps)+pslope*z[2])
            pbslope=wb/(pb*(1-pb)); q=expit(logit(pb)+pbslope*z[3])
            d=np.array([[.15*S*(1-p),.15*S*p],[.20*B*(1-q),.20*B*q],
                        [-S*pslope*p*(1-p),S*pslope*p*(1-p)],[-B*pbslope*q*(1-q),B*pbslope*q*(1-q)]])
        else:d=np.array([[.15*S],[.20*B]])
        return 2*(d @ (1-n/lam)+z)
    def obj(z):
        lam=expectation(z)
        d=(lam-n)/n
        return 2*np.sum(n*(d-np.log1p(d)))+np.dot(z,z)
    dim=4 if two else 2
    z0=np.zeros(dim)
    r=minimize(obj,z0,method='L-BFGS-B',jac=jac,bounds=[(-8,8)]*dim,options={'ftol':1e-14,'gtol':1e-6})
    a=minimize(obj,z0,method='Powell',bounds=[(-8,8)]*dim,options={'ftol':1e-12,'xtol':1e-10})
    assert a.success and max(abs(jac(r.x)))<1e-5 and max(abs(r.x))<7 and abs(r.fun-a.fun)<1e-7,(r,a)
    return max(0.,float(r.fun))

def compare(st,sa,b,pt,pa,pb,ws,wb):
    n=np.array([st*(1-pt)+b*(1-pb),st*pt+b*pb])
    q1=fit(np.array([n.sum()]),sa,b,pa,pb,0,0,False)
    q2=fit(n,sa,b,pa,pb,ws,wb,True)
    assert q2>=q1-1e-8
    return dict(count=q1,shape=q2,gain=q2-q1,sqrt_shape=np.sqrt(q2))
def run():
    D=json.loads(Path('design.json').read_text())
    v=json.loads(Path('templates.json').read_text())
    a,c=v['A_red'],v['B_blue']
    # Identical common A*eff inside 400–1200, use the area under each source curve.
    # Keep exact equal selected totals as a separate pure-shape control.
    R=c['mu_inclusive_LO']*c['area_400_1200']/(a['mu_inclusive_LO']*a['area_400_1200'])
    rows=[]
    def one(mode,setting,ns,ratio,r,w):
        p,q=[r+(1-2*r)*v['fraction_high'] for v in (a,c)]
        vals={}
        for k,st,sa,pt,pa in [('A_true',ns,ns*ratio,p,q),('B_true',ns*ratio,ns,q,p)]:
            vals[k]=compare(st,sa,D['background_events'],pt,pa,D['background_high_fraction'],w,w)
        rows.append(dict(mode=mode,setting=setting,selected_A=ns,selected_B=ns*ratio,migration=r,shape_width=w,**vals))
    for mode,ratio in [('window_rate',R),('equal_selected_rate',1.)]:
        for r in D['migration']:
            for w in D['shape_width_scenarios']:
                one(mode,'shape_grid',D['signal_A_events'],ratio,r,w)
        for ns in D['additional_selected_signal_events']:
            one(mode,'yield_scan',ns,ratio,.1,.05)
    assert compare(30,30,100,.3,.3,.3,.05,.05)['shape']<1e-10
    q=compare(30,29,100,.3,.3,.3,.05,.05);assert abs(q['gain'])<1e-9
    n=np.array([85.,45.]); m=np.array([92.,38.]); t=n.sum(); m0=m.sum()
    assert abs(np.sum(m-n+xlogy(n,n/m))-(m0-t+t*math.log(t/m0)+sum(xlogy(n,(n/t)/(m/m0)))))<1e-12
    print(json.dumps(dict(window_ratio=R,rows=rows),indent=2))
if __name__=='__main__':run()
