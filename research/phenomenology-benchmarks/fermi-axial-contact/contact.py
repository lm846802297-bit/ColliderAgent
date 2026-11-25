from pathlib import Path
import sys, json, csv
import numpy as np

PARENT=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(PARENT))
from recalc import load, flux, J, amplitude_table, solve, profile
from verify import numeric_profile
from scipy.optimize import brentq

MELL={'mumu':.1056583755,'tautau':1.77686}
GEV2_TO_CM3_S=(1.973269804e-14)**2*2.99792458e10

def weights(m):
    if not np.isfinite(m) or m<=0: raise ValueError('invalid DM mass')
    return {c: (1-(ml/m)**2)**1.5 if m>ml else 0. for c,ml in MELL.items()}|{'numu':.5,'nutau':.5}

def partial_rates(m,C):
    if not np.isfinite(C): raise ValueError('invalid contact coefficient')
    return {k:C*C*m*m/np.pi*GEV2_TO_CM3_S*v for k,v in weights(m).items()}

def flux_per_ref(m,grid,spectral,dirac=True,model=True):
    w=weights(m)
    if not model:w={'mumu':0.,'tautau':1.}
    denom=sum(w.values())
    p=sum((w[k]/denom)*flux(m,k,grid,spectral) for k in MELL if w[k]>0)
    return p*(.5 if dirac else 1.)

def run_mass(m, tables, grid, spectral, crosscheck=False):
    p=flux_per_ref(m,grid,spectral)
    assert np.all(np.isfinite(p)) and np.all(p>=0)
    inp=[(*amplitude_table(tables[k],p*10**(j-19)),sig) for k,(j,sig) in J.items()]
    a,b=solve(inp)
    q=2*sum(profile(b,*r)-profile(a,*r) for r in inp)
    assert abs(q-2.71)<5e-7
    k=sum(partial_rates(m,1.).values())
    c=np.sqrt(a*1e-26/k)
    assert abs(sum(partial_rates(m,c).values())/(a*1e-26)-1.)<1e-12
    frac={key:v/k for key,v in partial_rates(m,1.).items()}
    row=dict(mass_GeV=m,coefficient_95_GeVminus2=c,contact_scale_95_GeV=1/np.sqrt(c),
             sigma_v_total_95_cm3_per_s=a*1e-26,sigma_v_visible_95_cm3_per_s=a*1e-26*(frac['mumu']+frac['tautau']),
             BR_mumu=frac['mumu'],BR_tautau=frac['tautau'],BR_numu=frac['numu'],BR_nutau=frac['nutau'],q=q)
    if crosscheck:
        def ff(c): return sum(numeric_profile(c,tables[k],p*10**(j-19),sig) for k,(j,sig) in J.items())
        ref=brentq(lambda c:ff(c)-max(ff(0),ff(b))+1.355,b,2*a,xtol=1e-10)
        row['independent_root_relative_difference']=abs(a/ref-1)
        assert abs(a/ref-1)<1e-5
    return row,p*a

def trace_check():
    # Explicit Clifford matrices, spin sums, two independent final directions.
    sig=[np.array(a,complex) for a in ([[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]])]
    eye=np.eye(2); z=np.zeros((2,2)); I=np.eye(4)
    g=[np.block([[eye,z],[z,-eye]])]+[np.block([[z,s],[-s,z]]) for s in sig]
    gamma5=1j*g[0]@g[1]@g[2]@g[3]
    metric=np.array([1,-1,-1,-1])
    def sl(p):return sum(x*a*b for x,a,b in zip(p,g,metric))
    errors=[]
    for m in (1.0,2.0,7.0,35.0):
        u=sl([m,0,0,0])+m*I; v=sl([m,0,0,0])-m*I
        ini=np.array([[np.trace(v@a@u@b)/4 for b in g] for a in g])
        for ch,w in weights(m).items():
            mf=MELL.get(ch,0.)
            if m<=mf:
                assert w==0.; continue
            k=np.sqrt(m*m-mf*mf); beta=k/m
            for nhat in (np.array([0.,0.,1.]),np.array([2.,-2.,1.])/3):
                p=sl([m,*(k*nhat)])+mf*I; q=sl([m,*(-k*nhat)])-mf*I
                verts=[a@(gamma5 if ch in MELL else (I-gamma5)/2)*s for a,s in zip(g,metric)]
                end=np.array([[np.trace(p@a@q@b) for b in verts] for a in verts])
                val=(np.sum(ini*end)*beta/(32*np.pi*m*m)).real
                assert abs(val/(m*m/np.pi*w)-1)<1e-12
                errors.append(abs(val/(m*m/np.pi*w)-1))
    return dict(tests=len(errors),max_relative_error=max(errors))

def main():
    t,grid,y=load(PARENT)
    trace=trace_check()
    assert weights(MELL['tautau'])['tautau']==0
    assert weights(MELL['tautau']*(1+1e-8))['tautau']>0
    assert sum(partial_rates(10.,0.).values())==0
    p=flux_per_ref(10.,grid,y)
    assert np.array_equal(2*p,flux_per_ref(10.,grid,y,False))
    assert np.array_equal(flux_per_ref(10.,grid,y,False,False),flux(10.,'tautau',grid,y))
    try:amplitude_table(t['draco'],p*sum(partial_rates(10.,0.).values()))
    except ValueError:pass
    else:raise AssertionError('zero-coupling template accepted')
    rows=[]; signals={}
    for m in np.geomspace(2,100,25):
        a,b=run_mass(m,t,grid,y);rows.append(a);signals[str(m)]=b.tolist()
    checks=[run_mass(m,t,grid,y,True)[0] for m in (3.7,17.,73.)]
    with open('limits.csv','w') as f:
        wr=csv.DictWriter(f,list(rows[0]));wr.writeheader();wr.writerows(rows)
    Path('signals.json').write_text(json.dumps(dict(energy_edges_MeV=grid.tolist(),label='Bin energy flux at limit, MeV cm^-2 s^-1, at J=1e19 GeV² cm^-5 before profiling',values=signals),indent=2)+'\n')
    Path('validation.json').write_text(json.dumps(dict(trace=trace,held_out=checks),indent=2)+'\n')
if __name__=='__main__': main()
