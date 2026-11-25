import unittest
from migration import transfer

class TransferTest(unittest.TestCase):
    def test_identity(self):
        r=transfer([(3,True,True),(2,False,False)])
        self.assertEqual(r['paired_delta_fraction'],0)
        self.assertEqual(r['paired_se'],0)

    def test_equal_count_not_equal_weight(self):
        r=transfer([(3,True,False),(1,False,True),(1,True,True)])
        self.assertEqual((r['lost_n'],r['gained_n']),(1,1))
        self.assertAlmostEqual(r['paired_delta_fraction'],-.4)
        self.assertAlmostEqual(r['net_yield_delta_139'],-278)

    def test_equal_totals_can_have_migration(self):
        r=transfer([(1,True,False),(1,False,True)])
        self.assertEqual(r['paired_delta_fraction'],0)
        self.assertGreater(r['paired_se'],0)

if __name__=='__main__': unittest.main()
