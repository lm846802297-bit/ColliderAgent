import model MSSM_SLHA2-full
define p = g u c d s b u~ c~ d~ s~ b~
define j = p
generate p p > ta1- ta1+ / h01 h2 h3 QED==2 QCD==0
add process p p > ta2- ta2+ / h01 h2 h3 QED==2 QCD==0
add process p p > ta1- ta1+ j / h01 h2 h3 QED==2 QCD==1
add process p p > ta2- ta2+ j / h01 h2 h3 QED==2 QCD==1
add process p p > ta1- ta1+ j j / h01 h2 h3 QED==2 QCD==2
add process p p > ta2- ta2+ j j / h01 h2 h3 QED==2 QCD==2
output mg5-stau012 -f
quit
