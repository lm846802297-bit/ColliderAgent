import unittest
from filter_audit import defined_visible,event,pass_cut,measures


def tau(type_id=16):
    return {'p': [23.,0.,0.,23.], 'products':[[type_id,[10.,0.,0.,10.]],[211,[13.,0.,0.,13.]]]}


class TestFilters(unittest.TestCase):
    def test_visible_changes_threshold(self):
        t = [tau(),tau()]
        self.assertTrue(event(t)['parent'])
        self.assertFalse(event(t)['visible_all'])
        self.assertEqual(defined_visible(t[0]),(13.,0.,0.,13.))

    def test_strict_cuts(self):
        self.assertFalse(pass_cut((15.,0.,0.,15.)))
        self.assertFalse(pass_cut((16.,0.,200.,200.)))
        self.assertTrue(pass_cut((16.,0.,0.,16.)))

    def test_conservation_negative_control(self):
        t=tau()
        t['products'][0][1][3] += 1
        with self.assertRaisesRegex(ValueError,'reconstruction'):
            defined_visible(t)

    def test_unweighted_substitution_would_change_fraction(self):
        high={'p':[30.,0.,0.,30.],'products':[[16,[2.,0.,0.,2.]],[211,[28.,0.,0.,28.]]]}
        self.assertAlmostEqual(measures([(1.,event([high,high])),(3.,event([tau(),tau()]))])['cuts']['visible_all']['fraction'],0.25)

if __name__ == '__main__': unittest.main()
