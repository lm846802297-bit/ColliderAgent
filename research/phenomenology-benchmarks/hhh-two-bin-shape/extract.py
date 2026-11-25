import json, math
from pathlib import Path
import fitz
D=json.loads(Path('design.json').read_text())
doc=fitz.open('HLLHC_mix_m3h_YR5.pdf')
paths=doc[0].get_drawings()
x1,x2=57.367,264.734
def x(u):return 400+(u-x1)*800/(x2-x1)
def y(v):return .1*10**(-(v-54.676)/(219.066-54.676)*2)
c=json.loads(Path('anc/coeffs_14000.json').read_text())
def mu(a,b,t,u,v):
 return math.fsum((a-1)**int(k[1])*(b-1)**int(k[2])*r['value']*math.prod(z**i for z,i in zip((t,u,v),r['exponents'])) for k,terms in c['LHCHWG-2026-017'].items() for r in terms.values())
assert abs(mu(1,1,1,0,0)-1)<1e-10
out={}
for name,idx,ks in [('A_red',0,(1.5,10,1,0,1.8)),('B_blue',2,(.7,-60,1,0,-1)),('SM',-1,(1,1,1,0,0))]:
 color=tuple(.6666560173034668 if i==idx else 0. for i in range(3))
 d,=[d for d in paths if d['type']=='s' and d['color']==color and len(d['items'])==50]
 steps=[]
 for _,p,q in d['items']:
  if abs(p.y-q.y)>1e-7:continue
  m,n=sorted([x(p.x),x(q.x)])
  m,n=max(400,m),min(1200,n)
  if n>m+0.01:steps.append((m,n,y(p.y)))
 assert len(steps)==20 and all(abs(b-a-40)<.02 for a,b,_ in steps)
 def integ(a,b):return math.fsum(max(0,min(b,n)-max(a,m))*p/40 for m,n,p in steps)
 f=integ(400,1200); h=integ(D['cut_GeV'],1200); r=mu(*ks)
 # Independent grid midpoint test: 750 GeV is not at the middle of the merged bins.
 midpoint=[next(t for a,b,t in steps if a<=j+.5<b) for j in range(400,1200)]
 assert abs(sum(midpoint[350:])/sum(midpoint)-h/f)<5e-6
 out[name]={'kappas':ks,'mu_inclusive_LO':r,'sigma_inclusive_LO_fb':r*c['sigma_SM_fb'],'area_400_1200':f,'fraction_high':h/f,'steps':steps}
Path('templates.json').write_text(json.dumps(out,indent=2)+'\n')
for k,v in out.items():print(k,{k:v[k] for k in list(v)[:-1]})
