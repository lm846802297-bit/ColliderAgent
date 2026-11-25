import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
mpl.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelsize':11,'legend.frameon':False,'pdf.fonttype':42})
d=np.genfromtxt('limits.csv',delimiter=',',names=True)
x=d['mass_GeV']; c=d['coefficient_95_GeVminus2']; s=d['sigma_v_total_95_cm3_per_s']; v=d['sigma_v_visible_95_cm3_per_s']
f=plt.figure(figsize=(8.3,6.3))
f.subplots_adjust(left=.12,right=.96,top=.78,bottom=.15,wspace=.43)
ax=f.subplots(1,2)
f.text(.12,.92,'Fermi-LAT dwarf galaxies | Axial-lepton contact model',fontsize=16,weight='bold',color='#19314b')
f.text(.12,.864,r'Symmetric Dirac dark matter · 15 dwarf galaxies · six-year Pass 8 likelihood · prompt photons',fontsize=9.5,color='#455466')
ax[0].loglog(x,c,'o-',ms=3,color='#0b5c8b',lw=1.75)
top=c.max()*2.05
ax[0].fill_between(x,c,top,color='#d4eaf7',alpha=.7)
ax[0].set_ylim(c.min()*.63,top)
ax[0].annotate('Excluded within this EFT',xy=(.97,.90),xycoords='axes fraction',ha='right',fontsize=9,color='#0b5c8b')
ax[0].set(ylabel=r'Contact coefficient $|C|_{95}$ [GeV$^{-2}$]', title='(a) Model parameter limit')
ax[1].loglog(x,s,c='#0b5c8b',lw=1.9,label=r'Total ($\mu,\tau,\nu_{\mu},\nu_{\tau}$)')
ax[1].loglog(x,v,c='#ab5427',lw=1.7,ls='--',label=r'Charged leptons ($\mu,\tau$)')
ax[1].set(ylabel=r'Annihilation-rate upper bound [cm$^{3}$ s$^{-1}$]',title='(b) Rates at the same limit')
ax[1].legend(loc='upper left',fontsize=8.6)
for a in ax:
    a.set(xlim=(2,100),xlabel=r'Dark-matter mass $m_\chi$ [GeV]')
    a.set_xticks([2,5,10,20,50,100],labels=['2','5','10','20','50','100'])
    a.grid(axis='y',alpha=.22,which='major')
f.text(.12,.051,'Shown: a new interpretation of public data, not an official LAT contour or a light-mediator limit.',fontsize=8.8,color='#455466')
f.savefig('PhenoAgent_Fermi_Axial_Contact_95CL.pdf',metadata={'CreationDate':None,'ModDate':None})
