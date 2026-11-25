import unittest
from pathlib import Path
from sai import interp,table,cov_ref

class Contract(unittest.TestCase):
    def test_cannot_use_other_prong(self):
        for kwargs in (dict(track_count=3),dict(neutral_pions=1)):
            with self.assertRaisesRegex(ValueError,'topology'):
                interp(Path.cwd(),40,.8,**kwargs)
    def test_guard_edges(self):
        for p in (15.,15.49,500.,-1):
            with self.assertRaisesRegex(ValueError,'domain'):
                interp(Path.cwd(),p,.3)
    def test_exact_last_bin_behavior(self):
        a,b=table(Path.cwd(),3)
        self.assertAlmostEqual(interp(Path.cwd(),a[-2]/1000.,1.4),b[-1])
    def test_rotated_components(self):
        x=cov_ref([12.],[3.],[0.])
        self.assertEqual(x,[244.,0.,109.])

if __name__=='__main__': unittest.main()
