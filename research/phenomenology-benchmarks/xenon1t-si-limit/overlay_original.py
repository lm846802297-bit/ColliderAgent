"""Use author PDF as immutable vector background, with original-axis overlay."""
from pathlib import Path
import csv, hashlib, json
import fitz
import numpy as np
src=Path('Fig5a_original.pdf')
origin=fitz.open(src)
assert len(origin)==1 and not origin[0].get_images()
p=origin[0]
drawings=p.get_drawings()
xb=[]; yb=[]
for d in drawings:
    if d['type']!='fs' or len(d['items'])!=1 or d['items'][0][0]!='l':continue
    _,a,b=d['items'][0]
    if abs(a.y-550.8)<.01 and abs(a.y-b.y-16)<.01:xb.append(a.x)
    if abs(a.x-111.7)<.01 and abs(b.x-a.x-16)<.01:yb.append(a.y)
xb=sorted(xb); yb=sorted(yb,reverse=True)
assert len(xb)==len(yb)==3
dx,xa=np.polyfit([1,2,3],xb,1)
dy,ya=np.polyfit([-46,-45,-44],yb,1)
assert max(abs(np.array(xb)-(xa+dx*np.arange(1,4))))<6e-5
assert max(abs(np.array(yb)-(ya+dy*np.arange(-46,-43))))<6e-5
def get_paper(color):
    d,=[d for d in drawings if d['type']=='s' and d['color']==color and len(d['items'])==49]
    pts=np.array([(a.x,a.y) for _,a,b in d['items']]+[(d['items'][-1][2].x,d['items'][-1][2].y)])
    return (pts[:,0]-xa)/dx,(pts[:,1]-ya)/dy
asx,asy=get_paper((0.,1.,1.)); nx,ny=get_paper((1.,0.,1.))
assert np.max(np.abs(asx-nx))<1e-7
data=np.genfromtxt('paper-grid/limits.csv',delimiter=',',names=True)
m=data['m_chi_GeV']
assert np.max(np.abs(np.log10(m)-nx))<1e-6, 'use original curve nodes; no new interpolated rate'
ours_n=data['independent_toy_cm2']; ours_a=data['independent_asymptotic_cm2']
pn=10**ny; pa=10**asy
rn=ours_n/pn-1; ra=ours_a/pa-1
with Path('PhenoAgent_XENON1T_Fig5a_Pointwise.csv').open('w',newline='') as f:
    out=csv.writer(f)
    out.writerow(['m_chi_GeV','paper_toy_cm2','independent_toy_cm2','relative_toy','paper_asymptotic_cm2','independent_asymptotic_cm2','relative_asymptotic'])
    out.writerows(zip(m,pn,ours_n,rn,pa,ours_a,ra))
meta={k:dict(max_abs_percent=float(max(abs(r))*100),mass_of_max_GeV=float(m[np.argmax(abs(r))]),rms_percent=float(np.sqrt(np.mean(r*r))*100)) for k,r in [('toy',rn),('asymptotic',ra)]}
meta.update(original_pdf_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),nodes=len(m),original_axis_calibration={'x_ticks_pt':xb,'y_ticks_pt':yb,'x_tick_values_GeV':[10,100,1000],'y_tick_values_cm2':[1e-46,1e-45,1e-44]})
Path('overlay_validation.json').write_text(json.dumps(meta,indent=2)+'\n')
doc=fitz.open()
P=doc.new_page(width=p.rect.width+32,height=p.rect.height+108)
ox,oy=16,46
P.show_pdf_page(p.rect+(ox,oy,ox,oy),origin,0,overlay=True)
P.insert_font(fontname="OverlayRegular",fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
P.insert_font(fontname="OverlayBold",fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
def place(x,y):return fitz.Point(xa+dx*np.log10(x)+ox,ya+dy*np.log10(y)+oy)
# Sparse open ticks let the original solid lines show through when they agree.
sty=[(ours_n,(.12,.16,.35),'[3 5] 0'),(ours_a,(.73,.34,.04),'[2 6] 4')]
for series,color,dashes in sty:
    P.draw_polyline([place(x,y) for x,y in zip(m,series)],color=color,width=1.2,dashes=dashes)
    for i in range(2,len(m)-1,5):
        pt=place(m[i],series[i])
        P.draw_circle(pt,2.15,color=color,width=.9)
P.insert_text((28,27),'XENON1T Fig. 5(a) | Independent limits over the original',fontname='OverlayBold',fontsize=17,color=(.07,.11,.19))
line_y=p.rect.height+oy+16
for x,color,txt in [(30,sty[0][1],'Navy markers: recomputed nonasymptotic'),(378,sty[1][1],'Orange markers: recomputed asymptotic')]:
    P.draw_line((x,line_y-3),(x+20,line_y-3),color=color,dashes='[3 4] 0',width=1.5)
    P.draw_circle((x+10,line_y-3),2,color=color,width=1.0)
    P.insert_text((x+25,line_y),txt,fontname='OverlayRegular',fontsize=11,color=color)
P.insert_text((30,line_y+20),'Original cyan, magenta, and black lines are unchanged; the log axes are unmodified.',fontname='OverlayRegular',fontsize=10)
P.insert_text((30,line_y+36),'Source: XENON Collaboration, arXiv:2210.07231v1, Fig. 5(a), CC BY 4.0. Added overlays.',fontname='OverlayRegular',fontsize=10)
doc.set_metadata(dict(title='XENON1T Fig. 5(a) original-axis overlay',subject='Independent reproduction compared at the original 50 vector nodes'))
doc.subset_fonts()
doc.save('PhenoAgent_XENON1T_Fig5a_Original_Axis_Overlay.pdf',garbage=4,deflate=True)
print(json.dumps(meta))
