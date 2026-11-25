import math
import statistics as st
import unittest
from freeze import *


class FreezeTests(unittest.TestCase):
    def test_two_body_and_rotation(self):
        for unit in [(1.,0.,0.),(0.,0.,1.),(.6,0.,.8)]:
            q=rotate((0,0,1,2),unit)
            self.assertEqual(q,(*unit,2))
            p=(120.,40.,220.,math.hypot(280,120,40,220))
            a=boost((*(PSTAR*b for b in unit),ET),p,M)
            b=boost((*(-PSTAR*b for b in unit),EC),p,M)
            self.assertLess(residual(p,[a,b]),1e-13)

    def test_charge_conjugate_native_angular_controls(self):
        p=(0.,0.,0.,280.)
        z=(0.,0.,1.)
        for pol in (-1,0,1):
            g=gun(pol*POL,True)
            for pid in (-15,15):
                values=[pion_angle(tau_decay(g,pid,70100+i,z,p)) for i in range(256)]
                self.assertLess(abs(st.mean(values)-pol*POL/3),5*st.stdev(values)/16)
