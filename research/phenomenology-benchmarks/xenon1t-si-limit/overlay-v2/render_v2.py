"""Overlay thicker full lines, preserving the original page as a PDF form."""
from pathlib import Path
import math,json,hashlib
import fitz
import numpy as np
base=Path('..')
source=base/'Fig5a_original.pdf'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='239cae7a8737d87434af65e97d33b4b8ef81cc19b107af05cfbbf5e49b492aac'
src=fitz.open(source); box=src[0].rect
a=json.loads((base/'overlay_validation.json').read_text())['original_axis_calibration']
dx,xa=np.polyfit(np.log10(a['x_tick_values_GeV']),a['x_ticks_pt'],1)
dy,ya=np.polyfit(np.log10(a['y_tick_values_cm2']),a['y_ticks_pt'],1)
assert abs(dx-251.142)<.001 and abs(dy+155.979)<.001
orig=np.genfromtxt(base/'PhenoAgent_XENON1T_Fig5a_Pointwise.csv',delimiter=',',names=True)
par=np.genfromtxt('PhenoAgent_XENON1T_Fig5a_Parameter_Scan.csv',delimiter=',',names=True)
m=orig['m_chi_GeV']
assert len(m)==50 and np.array_equal(m,par['m_chi_GeV'])
ox,oy=26,74
xmin,xmax=111.699997+ox,669.700012+ox
ymin,ymax=7.200012+oy,550.799988+oy
D=fitz.open()
ink=(.06,.10,.17); subdued=(.31,.37,.45)
blue=(.04,.16,.40); darkorange=(.70,.27,.02)
green=(0.,.42,.24); red=(.70,.08,.15); brown=(.57,.33,.04)
def banner(title,subtitle):
    p=D.new_page(width=box.width+52,height=box.height+208)
    p.show_pdf_page(box+(ox,oy,ox,oy),src,0,overlay=True)
    for name,file in [('HeaderOverlay','DejaVuSans-Bold.ttf'),('BodyOverlay','DejaVuSans.ttf')]:
        p.insert_font(fontname=name,fontfile='/usr/share/fonts/truetype/dejavu/'+file)
    p.insert_text((34,32),title,fontname='HeaderOverlay',fontsize=18,color=ink)
    p.insert_text((35,55),subtitle,fontname='BodyOverlay',fontsize=10.5,color=subdued)
    return p
def pt(x,y): return np.array([np.clip(xa+dx*np.log10(x)+ox,xmin,xmax),ya+dy*np.log10(y)+oy])
def clip_pairs(points):
    block=[]; all_blocks=[]
    for p,q in zip(points[:-1],points[1:]):
        slope=q[1]-p[1]
        if abs(slope)<1e-15:
            if not ymin<=p[1]<=ymax: continue
            low,high=0,1
        else:
            a,b=sorted(((ymin-p[1])/slope,(ymax-p[1])/slope))
            low,high=max(0,a),min(1,b)
        if low>=high: continue
        u=p+low*(q-p); v=p+high*(q-p)
        if len(block) and np.linalg.norm(block[-1]-u)>1e-7:
            all_blocks.append(block); block=[]
        if not len(block):block=[u]
        block.append(v)
    if len(block):all_blocks.append(block)
    return all_blocks
def trace(p,values,color,dash,symbol=None,offset=2,w=2.2):
    vv=[pt(a,b) for a,b in zip(m,values)]
    for block in clip_pairs(vv):
        pp=[fitz.Point(float(u[0]),float(u[1])) for u in block]
        p.draw_polyline(pp,color=color,width=w,dashes=dash)
    if symbol:
        for x,y in vv[offset:-2:7]:
            if not (xmin+5<x<xmax-5 and ymin+5<y<ymax-5): continue
            if symbol=='circle':p.draw_circle((x,y),3.2,color=color,fill=(1,1,1),width=1.25)
            else:p.draw_rect(fitz.Rect(x-2.65,y-2.65,x+2.65,y+2.65),color=color,fill=(1,1,1),width=1.25)
def label(p,x,y,text,color,dash,symbol=None):
    p.draw_line((x,y-4),(x+38,y-4),color=color,dashes=dash,width=2.2)
    if symbol=='circle':
        p.draw_circle((x+20,y-4),3.2,color=color,fill=(1,1,1),width=1.2)
    elif symbol=='square':
        p.draw_rect(fitz.Rect(x+17.35,y-6.65,x+22.65,y-1.35),color=color,fill=(1,1,1),width=1.2)
    p.insert_text((x+45,y),text,fontname='BodyOverlay',fontsize=11,color=ink)
def foot(p,lines,y):
    for z,s in enumerate(lines):p.insert_text((40,y+17*z),s,fontname='BodyOverlay',fontsize=10.2,color=subdued)
p=banner('XENON1T Fig. 5(a) | Original and independently reproduced',
         'The complete original panel is embedded unchanged. Dark dashed lines are our calculation.')
ash='[5 9] 6'; toy='[10 11] 0'
trace(p,orig['independent_asymptotic_cm2'],darkorange,ash,'square',offset=6,w=2.3)
trace(p,orig['independent_toy_cm2'],blue,toy,'circle',offset=2,w=2.55)
y=oy+box.height+23
label(p,40,y,'Our nonasymptotic result vs original magenta',blue,toy,'circle')
label(p,40,y+22,'Our asymptotic result vs original cyan',darkorange,ash,'square')
foot(p,["50 original mass nodes: maximum differences 0.33% and 0.39%, respectively.",
        "Black: 2018 full-likelihood result, retained for reference; not the curve reproduced here.",
        "Original: XENON Collaboration, arXiv:2210.07231v1, Fig. 5(a), CC BY 4.0."],y+47)
p=banner('XENON1T Fig. 5(a) | What changes the inferred limit?',
         'Same detector response and nonasymptotic likelihood. Each new curve changes one input only.')
for column,color,dash in [('mV_50MeV_rho_0p30_cm2',red,'[] 0'),
                           ('mV_100MeV_rho_0p30_cm2',green,'[8 5] 0'),
                           ('contact_rho_0p20_cm2',brown,'[2 4] 0')]:
    trace(p,par[column],color,dash,w=2.7)
trace(p,orig['independent_toy_cm2'],blue,toy,'circle',offset=2,w=2.15)
label(p,40,y,'Baseline: contact, density 0.30 GeV/cm3',blue,toy,'circle')
label(p,375,y,'Contact, density 0.20 GeV/cm3',brown,'[2 4] 0')
label(p,40,y+22,'Mediator 100 MeV, density 0.30 GeV/cm3',green,'[8 5] 0')
label(p,375,y+22,'Mediator 50 MeV, density 0.30 GeV/cm3',red,'[] 0')
foot(p,["New curves constrain the zero-momentum WIMP-nucleon cross section. Off-scale points are clipped.",
        "Sensitivity benchmarks, not published curves. All curves retain the original plotted range.",
        "Original: XENON Collaboration, arXiv:2210.07231v1, Fig. 5(a), CC BY 4.0."],y+47)
D.set_metadata({'title':'XENON1T Fig. 5(a) original-axis reproduction and parameter sensitivity'})
D.subset_fonts()
D.save('PhenoAgent_XENON1T_Fig5a_Reproduction_And_Variations.pdf',garbage=4,deflate=True)
