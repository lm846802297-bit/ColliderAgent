from recalc import *
import fitz
import json

RED=(.77,.08,.17)
BLUE=(.30,.15,.68)
# Calibrate exclusively from printed 10/10000 GeV and 10^-21/10^-27 ticks.
def pmap(x,y):
    return fitz.Point(140.5743866+(np.log10(x)-1)*(466.4164429-140.5743866)/3,
                      13.3989563-(np.log10(y)+21)*(248.5098877-13.3989563)/6)

def make():
    out=fitz.open()
    fields='channel mass_GeV published_table_cm3_per_s published_vector_cm3_per_s reconstructed_cm3_per_s relative_to_table relative_to_pdf fixed_J_cm3_per_s'.split()
    d=load()
    trials=np.genfromtxt('trial.log',dtype=None,encoding='utf-8')
    with open('Fermi_LAT_Fig1_Pointwise.csv','w') as fp:
        w=csv.writer(fp);w.writerow(fields)
        for ch in ('bb','tautau'):
            paper=fitz.open(BASE/'paper'/f'p302_6yr_source_composite_limit_data_plot_{ch}.pdf')
            p=paper[0]; curve=p.get_drawings()[5]
            assert curve['color']==(0.,0.,0.) and curve['dashes']=='[] 0'
            xy=[curve['items'][0][1]]+[seg[2] for seg in curve['items']]
            records=[row for row in trials if row[0]==ch]
            assert len(xy)==len(records)
            pts=[]; alt=[]
            for point,(_,m,calc,official,rel,_) in zip(xy,records):
                expect=pmap(m,official)
                assert abs(point.x-expect.x)<.002 and abs(point.y-expect.y)<.002
                v=10**(-21-(point.y-13.3989563)*6/(248.5098877-13.3989563))
                fixed=solve(targets(m,ch,*d,True))[0]*1e-26
                w.writerow([ch,m,official,v,calc,rel,calc/v-1,fixed])
                pts.append(pmap(m,calc)); alt.append(pmap(m,fixed))
            for variant in (False,True):
                pg=out.new_page(width=p.rect.width,height=p.rect.height+65)
                pg.show_pdf_page(p.rect,paper,0)
                pg.draw_polyline(pts,color=RED,dashes='[7 3] 0',width=1.2, lineCap=0)
                for a in pts[1:-1]:pg.draw_circle(a,2.5,color=RED,width=.95)
                if variant:
                    pg.draw_polyline(alt,color=BLUE,dashes='[2 2] 0',width=1.25)
                    for a in alt[1:-1]:
                        pg.draw_rect(fitz.Rect(a.x-2,a.y-2,a.x+2,a.y+2),color=BLUE,width=.8)
                pg.insert_text((12,328),'Fermi-LAT Fig. 1  |  Direct overlay on the original vector panel',fontsize=10,fontname='hebo')
                pg.draw_line((12,342),(35,342),color=RED,dashes='[7 3] 0',width=1.3)
                pg.draw_circle((24,342),2.5,color=RED,width=.9)
                pg.insert_text((42,345),'PhenoAgent: independent reconstruction, J factors profiled',fontsize=9.2,color=RED)
                pg.draw_line((12,356),(35,356),color=(0,0,0),width=1.5)
                pg.insert_text((42,359),'Fermi-LAT: original observed 6-year Pass 8 limit (solid black)',fontsize=9.2)
                if variant:
                    pg.draw_line((12,370),(35,370),color=BLUE,dashes='[2 2] 0',width=1.2)
                    pg.insert_text((42,373),'Control: fix J factors at the published central values',fontsize=9.2,color=BLUE)
            paper.close()
    out.save('Fermi_LAT_Fig1_Independent_Overlay.pdf',garbage=4,deflate=True,no_new_id=True)
if __name__=='__main__':make()
