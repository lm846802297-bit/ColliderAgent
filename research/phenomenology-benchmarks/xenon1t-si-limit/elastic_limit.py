import sys,csv,math,json,warnings
from pathlib import Path
import numpy as np
from scipy.special import erf,spherical_jn
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import chi2
from xe_likelihood import BinwiseInference
import wimprates as wr
import numericalunits as nu
warnings.simplefilter('ignore', DeprecationWarning)
RM=lambda a,b:a*b/(a+b)
A=131.293; amu=0.93149410242; M=A*amu; MP=.93827208816
V=299792.458; V0=220.; VE=232.; VESC=544.
Z=erf(VESC/V0)-2*VESC/V0/math.sqrt(math.pi)*math.exp(-(VESC/V0)**2)
HBARC=.197327
CV=(.3/1.782661921e-27)*1e-45*1e-6*V*V*1e5*1000*(365.25*86400)
RN=math.sqrt((1.23*A**(1/3)-.60)**2+7/3*math.pi**2*.52**2-5*.9**2)
def eta(v):
    z=VESC/V0
    if v>=VESC+VE: return 0.
    l=(v-VE)/V0
    if v<VESC-VE: return (erf((v+VE)/V0)-erf(l)-4*VE/(math.sqrt(math.pi)*V0)*math.exp(-z*z))/(2*Z*VE)
    return (erf(z)-erf(l)-2*(VESC+VE-v)/(math.sqrt(math.pi)*V0)*math.exp(-z*z))/(2*Z*VE)
def rate(e,m,scale=1):
    q=math.sqrt(2*M*e*1e-6)
    x=q*RN/HBARC
    helm=(3*spherical_jn(1,x)/x if x else 1.)**2*math.exp(-(q*.9/HBARC)**2)
    return scale*CV/m*A**2/(2*RM(m,MP)**2)*helm*eta(q/(2*RM(m,M))*V)
def independent_ul(lk,scale,asn=False):
    s=lk.spectrum_in_reconstructed_bins*scale
    if np.max(s)<=0: raise ValueError('No signal support')
    xs=lk.signal_expectations_bins
    lls=lk.likelihood_matrix[0]
    kmax=(xs[-1]/s.max())
    breaks=np.unique(np.r_[0,kmax,np.concatenate([xs/p for p in s if p>0])])
    breaks=breaks[breaks<=kmax]
    def ll(x): return sum(np.interp(x*p,xs,L) for p,L in zip(s,lls))
    ls=np.array([ll(x) for x in breaks]); at=int(np.argmin(ls)); lm=ls[at]
    threshold=lambda x: chi2(1).isf(.1) if asn else lk.threshold_function(x*s.sum())
    return brentq(lambda x:ll(x)-lm-threshold(x), breaks[at],kmax,xtol=1e-14)
def run():
    masses=np.unique(np.r_[np.geomspace(6,1000,40),[10,30,50,100,500]])
    selected=[10,30,50,100,500]
    probe_e=np.geomspace(.1,70,45)
    assert rate(5,30,0)==0
    assert eta(776)==0 and eta(0)>0
    err=[]
    for m in selected:
        ref=wr.rate_wimp(probe_e*nu.keV,m*nu.GeV/nu.c0**2,1e-45*nu.cm**2)*(nu.keV*1000*nu.kg*nu.year)
        this=np.array([rate(e,m) for e in probe_e])
        good=ref>ref.max()*1e-4
        err.append(float(np.max(abs(this[good]/ref[good]-1))))
    assert max(err)<.01,err
    L=BinwiseInference.from_xenon1t_sr()
    rows=[]
    binned=[]
    for m in masses:
        L.spectrum=lambda e:rate(e,m)
        row=[m]
        for asn in [False,True]:
            native=L.compute_ul(cl=.1,asymptotic=asn)
            own=independent_ul(L,1,asn)
            row +=[native*1e-45,own*1e-45,own/native-1]
        # convert cm^2 to GeV^-2 then solve sigma = mu_p^2 C^2 / pi
        row.append(math.sqrt(math.pi*row[2]/(.3893793721e-27))/RM(m,MP))
        rows.append(row)
        binned.append(L.spectrum_in_reconstructed_bins.tolist())
    neg=BinwiseInference.from_xenon1t_sr(); neg.spectrum=lambda e:rate(e,30,0)
    try: independent_ul(neg,1)
    except ValueError: pass
    else: raise AssertionError('zero-signal negative control')
    assert max(max(abs(r[3]),abs(r[6])) for r in rows)<.01,rows
    with open('limits.csv','w') as f:
        out=csv.writer(f)
        out.writerow(['m_chi_GeV','native_toy_cm2','independent_toy_cm2','delta_toy','native_asymptotic_cm2','independent_asymptotic_cm2','delta_asymptotic','C90_GeVminus2'])
        out.writerows(rows)
    Path('selected_signals_per_ref.json').write_text(json.dumps(dict(mass_GeV=masses.tolist(),reconstructed_keV_edges=L.reconstructed_energy_edges.tolist(),signal=binned),indent=2)+'\n')
    print(json.dumps(dict(rate_reference_masses=selected,rate_max_relative=err,limit_max_relative=max(max(abs(r[3]),abs(r[6])) for r in rows)),indent=2))
if __name__=='__main__':run()
