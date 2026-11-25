import unittest
from tau_met import project, summary

class Closure(unittest.TestCase):
    def test_rotated_axes(self):
        self.assertEqual(project((0,1),(3,4)),(4,-3))

    def test_negative_covariance(self):
        a=summary([(1,2,-2),(1,4,-4)])
        self.assertAlmostEqual(a['rho'],-1)
        self.assertAlmostEqual(a['met_plus_tau_sigma_gev'],0)

if __name__=='__main__': unittest.main()
