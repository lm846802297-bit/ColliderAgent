"""Freeze finite mediator masses 100 and 50 MeV, rho=0.20 sensitivity."""
import csv,json
from pathlib import Path
import numpy as np
from elastic_limit import rate, M, BinwiseInference, independent_ul
data=np.genfromtxt('../paper-grid/limits.csv',delimiter=',',names=True)
lk=BinwiseInference.from_xenon1t_sr()
def finite_rate(e,m,mv):
    return rate(e,m)*(1+2*M*e*1e-6/mv**2)**-2
assert finite_rate(0,30,.05)==rate(0,30)
assert abs(finite_rate(10,30,1e5)/rate(10,30)-1)<1e-12
assert 0<finite_rate(10,30,.05)<finite_rate(10,30,.1)<rate(10,30)
rows=[]; cross=[]
for m,base in zip(data['m_chi_GeV'],data['independent_toy_cm2']):
    row=[m,base,base*.3/.2]
    for mv in [.1,.05]:
        lk.spectrum=lambda e:finite_rate(e,m,mv)
        exact=independent_ul(lk,1,False)
        native=lk.compute_ul(cl=.1,asymptotic=False)
        cross.append(abs(exact/native-1))
        row.append(exact*1e-45)
    rows.append(row)
assert max(cross)<.001,max(cross)
assert np.all(np.array(rows)[:,4]>np.array(rows)[:,3])
assert np.all(np.array(rows)[:,3]>np.array(rows)[:,1])
for m in [6.,30.,100.]:
    lk.spectrum=lambda e:rate(e,m)*(.2/.3)
    lhs=independent_ul(lk,1)*1e-45
    lk.spectrum=lambda e:rate(e,m)
    rhs=1.5*independent_ul(lk,1)*1e-45
    assert abs(lhs/rhs-1)<1e-10
with open('PhenoAgent_XENON1T_Fig5a_Parameter_Scan.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['m_chi_GeV','baseline_contact_rho_0p30_cm2','contact_rho_0p20_cm2','mV_100MeV_rho_0p30_cm2','mV_50MeV_rho_0p30_cm2']); w.writerows(rows)
Path('parameter_validation.json').write_text(json.dumps({'nodes':len(rows),'max_limit_solver_rel_diff':max(cross),'density_rescaling_controls_GeV':[6,30,100],'zero_transfer_and_contact_limits':'PASS'},indent=2)+'\n')
