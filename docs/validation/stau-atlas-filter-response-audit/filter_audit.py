import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

SHA="ac20e8b056e16b98b19d566dc683f9658277393f321b21c864cc38241ea1614e"
T17_SHA='71c8ffa21d6163b35d13b8c1676f64bc5fe2d1f0a9dafa5eeeb7168ef628517b'
MODES=('parent','visible_all','parent_both_had','visible_both_had')
LABELS=('L0','R0','L1','R1','L2','R2')
INVIS={12,14,16,1000022}


def pass_cut(v):
    pt=math.hypot(v[0],v[1])
    return pt>15 and abs(math.asinh(v[2]/pt))<2.6


def visible(daughters):
    return tuple(math.fsum(p[j] for a,p in daughters if abs(a) not in INVIS) for j in range(4))


def defined_visible(x):
    direct=visible(x['products'])
    subtract=tuple(math.fsum([x['p'][j],*(-p[j] for a,p in x['products'] if abs(a) in INVIS)]) for j in range(4))
    if max(abs(p-q) for p,q in zip(direct,subtract))>=1e-7 or pass_cut(direct)!=pass_cut(subtract):
        raise ValueError("visible reconstruction or filter disagrees with parent-minus-invisible")
    return direct


def event(t):
    parent=[pass_cut(x['p']) for x in t]
    vis=[pass_cut(defined_visible(x)) for x in t]
    had=all(not any(abs(a) in (11,13) and abs(b) in (12,14) for a,_ in x['products'] for b,_ in x['products']) for x in t)
    return dict(parent=all(parent),visible_all=all(vis),parent_both_had=all(parent) and had,
                visible_both_had=all(vis) and had,had_pair=had,
                parent_pt_only=all(math.hypot(*x['p'][:2])>15 for x in t),
                parent_eta_only=all(math.hypot(*x['p'][:2])>0 and abs(math.asinh(x['p'][2]/math.hypot(*x['p'][:2])))<2.6 for x in t))


def measures(r):
    wsum=math.fsum(w for w,_ in r)
    d={}
    for m in (*MODES,'had_pair','parent_pt_only','parent_eta_only'):
        s=math.fsum(w for w,x in r if x[m]); p=s/wsum
        d[m]={'raw_pass':sum(x[m] for _,x in r),'sum_fb':s,'fraction':p,
              'conditional_sigma':math.sqrt(math.fsum((w*(x[m]-p))**2 for w,x in r))/wsum}
    d['difference']={}
    for name,a,b in [('parent_minus_visible','parent','visible_all'),
                     ('unrestricted_minus_had_parent','parent','parent_both_had')]:
        p=math.fsum(w*(x[a]-x[b]) for w,x in r)/wsum
        d['difference'][name]={'delta':p,'sigma':math.sqrt(math.fsum((w*(x[a]-x[b]-p))**2 for w,x in r))/wsum,
            'first_only':sum(x[a] and not x[b] for _,x in r),'second_only':sum(x[b] and not x[a] for _,x in r)}
    return {'events':len(r),'sum_fb':wsum,'cuts':d}


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('reference');p.add_argument('output');a=p.parse_args()
    with open(a.input,'rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==SHA
    ref=Path(a.reference).read_bytes()
    assert hashlib.sha256(ref).hexdigest()==T17_SHA
    t=json.loads(ref)['values']
    assert t[0]['x'][0]['value']=='Total events' and t[1]['x'][0]['value']=='Generator filter'
    paper_reference=float(t[1]['y'][2]['value'])/float(t[0]['y'][2]['value'])
    data={k:[] for k in LABELS}; seen=set()
    with gzip.open(a.input,'rt') as f:
        for x in map(json.loads,f):
            c,i=map(int,x['event_id'].split(':'))
            assert len(x['taus'])==2 and x['event_id'] not in seen
            assert {p for p,_ in x['parents']}==({-1000015,1000015} if c%2 else {-2000015,2000015})
            w=x['weight_fb']; assert w>0
            seen.add(x['event_id']); data[LABELS[c-1]].append((w,event(x['taus'])))
    assert len(seen)==4216
    universes={'all':sum(data.values(),[]),'L':sum([data[k] for k in LABELS[::2]],[]),'R':sum([data[k] for k in LABELS[1::2]],[]),**data}
    for i in range(3): universes[f'jet{i}']=data[f'L{i}']+data[f'R{i}']
    stat={k:measures(v) for k,v in universes.items()}
    controls={m:(5.8*stat['L']['cuts'][m]['fraction']+2.2*stat['R']['cuts'][m]['fraction'])/8 for m in MODES}
    out={'input_sha256':SHA,'atlas_t17_weighted_filter_ratio':paper_reference,'atlas_t17_sha256':T17_SHA,'independent_visible_four_vectors_checked':2*len(seen),
         'official_filter_exact_definition':'UNVERIFIED', 'data':stat, 'counterfactual_atlas_LR_xsec_mix_only':controls}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')


if __name__=='__main__': main()
