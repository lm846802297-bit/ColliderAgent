import math
import unittest
from types import SimpleNamespace as T
import ROOT
from cutflow import dphi,m2,probabilities,HLT,LATE


def pt(px,py): return ROOT.TLorentzVector(px,py,0.,math.hypot(px,py))


class TestSelection(unittest.TestCase):
    def test_phi_wrap(self):
        self.assertAlmostEqual(dphi(math.pi-.1,-math.pi+.1),.2)

    def test_massless_no_upstream_pt(self):
        a,b=pt(70,0),pt(0,40)
        self.assertAlmostEqual(m2(a,b,-a-b),math.sqrt(2*70*40),places=6)
        self.assertLess(m2(a,b,pt(0,0)),1e-6)

    def test_strict_trigger_met(self):
        a,b=T(pt=99,tracks=1),T(pt=65,tracks=3)
        self.assertAlmostEqual(probabilities(True,a,b,139)[0],HLT*(1-LATE))
        self.assertAlmostEqual(probabilities(False,a,b,151)[0],HLT)
        self.assertEqual(probabilities(False,a,b,150)[0],0)

    def test_tight_nested(self):
        a,b=T(pt=99,tracks=1),T(pt=65,tracks=3)
        self.assertAlmostEqual(probabilities(True,a,b,139)[1],.8*.75)
        self.assertAlmostEqual(probabilities(False,a,b,151)[1],1-.2*.25)

if __name__=='__main__':
    unittest.main()
