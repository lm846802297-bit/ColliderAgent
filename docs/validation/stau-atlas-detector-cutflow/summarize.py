"""Compare the fixed detector seeds with the HEPData cutflow, no rescaling."""
import csv
import json
from pathlib import Path

seeds=[34025,34026,34027]
r=[json.loads(Path(f'result-{s}.json').read_text()) for s in seeds]
fields=['region','stage','our_nominal_events','our_mc_sigma','atlas_events','atlas_mc_sigma',
        'our_conditional_eff','atlas_conditional_eff','our_ae','atlas_ae','our_contributors',
        'our_neff','other_seed_min_events','other_seed_max_events','nominal_yield_screen']
with open('comparison.csv','w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(fields)
    for region in ('common','low','high'):
        for j,a in enumerate(r[0]['cutflow'][region]):
            spread=[v['cutflow'][region][j]['ours'] for v in r[1:]]
            w.writerow([region,a['step'],a['ours'],a['mc_sigma'],a['atlas'],a['atlas_mc_sigma'],
                        a['step_eff'],a['atlas_step_eff'],a['our_acceptance'],a['atlas_acceptance'],
                        a['positive_contributors'],a['neff'],min(spread),max(spread),a['diagnostic_within_gate']])
