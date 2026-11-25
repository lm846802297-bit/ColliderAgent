"""Replay source-locked SimpleAnalysis pieces, not a detector response."""
import hashlib
from bisect import bisect_left
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile

PIN='b11c683f12618c2543ac9de9cc8c5aef2ab02759'
EX={
 'METSignificanceCalculator.cxx':'852378dd43288153a1eb158acfd74eaab89edebdad2f34e04d68d6640c0bd8fc',
 'ObjectResolutions.cxx':'3275c45918fe7c351301870b80b5423e9b816b81ea35056809bd81b1b5dc4443',
 **{f'tauRes1p0nBin{i}.h':s for i,s in enumerate((
  '380595ce444af1ae5f1632c81475b70ce065e1ac32e0714eb769e1285392b043',
  '1f750b19dd307ee8e39f7a4338e662a62f29d54e8debbfa01c93d198c09fe7ae',
  '2a9137f560e38704c4209b579ac7773c772c42b67cbe6a9b721c8328aec9e972',
  'c3f91415609c529ef90db8e271bb4787005eb25ca7b893b6c8fc41068d4fa7eb',
  '48d07ccdd77374fe4a94181498c3e80bc062650c50f5470f1d9479442db97828'))}}
ETA=(.3,.8,1.3,1.6)


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def table(base,i):
    s=(base/f'tauRes1p0nBin{i}.h').read_text()
    s=re.sub(r'//[^\n]*','',s)
    a=[float(x.strip()) for x in s.split('{',1)[1].split('}',1)[0].split(',') if x.strip()]
    nx,ny=map(int,a[:2]); assert ny==1 and len(a)==2+nx+1+ny+1+nx
    x=a[2:nx+3]; y=a[nx+3:nx+5]; vals=a[nx+5:]
    assert y[0]<=0<y[1] and all(l<r for l,r in zip(x,x[1:]))
    assert all(math.isfinite(v) and v>0 for v in vals)
    return x,vals


def interp(base,pt,eta_value,track_count=1,neutral_pions=0):
    if track_count!=1 or neutral_pions!=0: raise ValueError('not the source 1p0n calibration topology')
    if not (math.isfinite(pt) and math.isfinite(eta_value) and abs(eta_value)<2.5): raise ValueError('fiducial')
    x,h=table(base,bisect_left(ETA,abs(eta_value))); centers=[(left+right)/2 for left,right in zip(x,x[1:])]
    y=1000*pt
    if not centers[0]<=y<=min(499000.,x[-1]-1.): raise ValueError('outside safe lookup domain')
    if y>=x[-2]: return h[-1]  # upstream stops interpolation on entering the last bin
    j=bisect_left(centers,y)
    if j==len(centers): return h[-1]
    if centers[j]==y: return h[j]
    f=(y-centers[j-1])/(centers[j]-centers[j-1])
    return (1-f)*h[j-1]+f*h[j]


def cov_ref(radial,angular,phis):
    out=[100.,0.,100.]
    for a,b,phi in zip(radial,angular,phis):
        X=(math.cos(phi),math.sin(phi)); Y=(-X[1],X[0])
        out[0]+=a*a*X[0]**2+b*b*Y[0]**2
        out[1]+=a*a*X[0]*X[1]+b*b*Y[0]*Y[1]
        out[2]+=a*a*X[1]**2+b*b*Y[1]**2
    return out


def main(base=Path.cwd()):
    for p,h in EX.items(): assert digest(base/p)==h
    obj=(base/'ObjectResolutions.cxx').read_text()
    met=(base/'METSignificanceCalculator.cxx').read_text()
    lookup=obj[obj.index('static double getHistValue'):obj.index('static double getJetPtResolution')]
    tau=obj[obj.index('static double getTauPtResolution'):obj.index('void getObjectResolution')]
    rot=met[met.index('static void rotateXY'):met.index('double calcMETSignificance')]
    code='''#include <cmath>
#include <iostream>
#include <iomanip>
#include <algorithm>
struct AnalysisObject {double pt,eta; double Pt(){return pt;} double Eta(){return eta;}};
struct TMatrix {double a[2][2]{}; double &operator()(int i,int j){return a[i][j];}};
'''+''.join(f'#include "tauRes1p0nBin{i}.h"\n' for i in range(5))+lookup+tau+rot+'''
int main(){
 std::cout<<std::setprecision(17); double a,b,phi; char mode;
 while(std::cin>>mode>>a>>b>>phi){
  if(mode=='T'){AnalysisObject t{a,b}; std::cout<<getTauPtResolution(t)<<"\\n";}
  else {TMatrix x,rot; x(0,0)=a*a;x(1,1)=b*b;rotateXY(x,rot,phi);
    std::cout<<rot(0,0)<<" "<<rot(0,1)<<" "<<rot(1,1)<<"\\n";}
 }
}
'''
    etas=(0.,.3,.301,.8,.801,1.3,1.301,1.6,1.601,2.48)
    pts=(15.5,16.,22.85,49.,80.,150.,250.,499.)
    tests=[(pt,eta,interp(base,pt,eta)) for eta in etas for pt in pts if pt<=min(499.,table(base,bisect_left(ETA,eta))[0][-1]/1000-.001)]
    phis=(.3,-1.7,1.2)
    radial=(4.,7.,15.)
    angular=(.8,1.5,5.)
    data=''.join(f'T {e} {a} 0\n' for e,a,_ in tests)+''.join(f'R {a} {b} {p}\n' for a,b,p in zip(radial,angular,phis))
    with tempfile.TemporaryDirectory() as tmp:
        c=Path(tmp)/'fixture.cc'; c.write_text(code)
        exe=Path(tmp)/'run'; subprocess.run(['c++','-std=c++17','-O2','-I',str(base),str(c),'-o',str(exe)],check=True)
        vals=subprocess.check_output([str(exe)],input=data,text=True).splitlines()
    assert len(vals)==len(tests)+len(phis)
    residual=max(abs(float(v)-x[2]) for v,x in zip(vals,tests))
    assert residual<1e-14
    native=[float(x)+math.fsum(float(v.split()[j]) for v in vals[len(tests):]) for j,x in enumerate((100,0,100))]
    independent=cov_ref(radial,angular,phis)
    assert max(abs(a-b) for a,b in zip(native,independent))<1e-12
    l,lt,t=native
    ratio=94./math.sqrt(l*(1-lt*lt/(l*t)))
    schur=94.*math.sqrt(t/(l*t-lt**2))
    assert abs(ratio-schur)<1e-14
    out=dict(commit=PIN,hashes=EX,native_test_points=len(tests),max_fractional_resolution_absdiff=residual,
      two_by_two_native=native,two_by_two_independent=independent,fixture_significance=ratio,
      fixture_met_gev=94., source_first_bin_domain_under_15p5gev='excluded_by_guard_not_native_tested',
      values=[dict(pt_gev=pt,abs_eta=eta,fractional_pt_resolution=x) for pt,eta,x in tests],
      status='source_math_gates_passed_not_detector_calibration')
    (base/'result.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')


if __name__=='__main__': main()
