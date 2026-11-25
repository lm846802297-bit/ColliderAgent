import unittest
from compare import era_flags,contrast

class Controls(unittest.TestCase):
    def test_threshold_boundaries(self):
        self.assertEqual(era_flags(95,75,150),dict(low_early=False,low_late=False,high_early=False,high_late=False))
        self.assertEqual(era_flags(96,75,151),dict(low_early=True,low_late=False,high_early=True,high_late=True))
    def test_identity_paired(self):
        a=[(1,{'source_index':0,'cut':True}),(2,{'source_index':1,'cut':False})]
        b=[(3,x) for w,x in a[:1]]+[(6,x) for w,x in a[1:]]
        r=contrast(a,b,lambda x:x['cut'])
        self.assertAlmostEqual(r['delta'],0)
        self.assertAlmostEqual(r['paired_event_mc_sigma'],0)

if __name__=='__main__': unittest.main()
