import json
import math
from pathlib import Path
import unittest
from closure import kt_transitions, derive, edges_bin
from assess import assessed


class Tests(unittest.TestCase):
    def test_exclusive_hadronic_kt_known_vectors(self):
        d01,d12=kt_transitions([(12,0,0,12),(0,7,0,7)])
        self.assertAlmostEqual(d01,12)
        self.assertAlmostEqual(d12,7)
        d01,d12=kt_transitions([(10,0,0,10),(6,0,0,6)])
        self.assertAlmostEqual(d01,16)
        self.assertEqual(d12,0)
        self.assertEqual(kt_transitions([]),(0.,0.))
        self.assertEqual(edges_bin(20),2)

    def test_no_post_cut_double_count(self):
        args=dict(rawpb=.01,selected=5,sigmaGen_fb=0)
        e=dict(args,records=[(1.,None)]*2)
        s=dict(args,records=[(0.,None),(1.5,None)])
        c=dict(args,records=[(0.,None),(1.5,(20,0))])
        r=derive(e,s,c,5)
        self.assertAlmostEqual(r["sigma_fb"],3.)
        self.assertAlmostEqual(r["two_pass_sigma_fb"],3.)
        self.assertNotAlmostEqual(r["sigma_fb"],.01*1000*1.5/2)
        with self.assertRaisesRegex(ValueError,"nSelected"):
            derive(e,s,c,2)
        with self.assertRaisesRegex(ValueError,"or normalizations disagree"):
            derive(e,dict(args,records=[(0.,None),(1.,None)]),c,5)

    def test_frozen_outputs_fail_closed(self):
        rows=json.loads(Path("closure-rows.json").read_text())
        s=assessed(rows,json.loads(Path("pilot-endstat.json").read_text()))
        self.assertTrue(s["gate"]["normalization_parity"])
        self.assertTrue(s["gate"]["native_summary_reconciled"])
        self.assertFalse(s["gate"]["detector_handoff"])
        self.assertIsNone(s["gate"]["threshold_jet_bin_stability"])


    def test_independent_gate_and_reject_swapped_stats(self):
        rows=json.loads(Path("independent10k-rows.json").read_text())
        report=json.loads(Path("independent-endstat.json").read_text())
        self.assertTrue(assessed(rows,report)["gate"]["detector_handoff"])
        self.assertFalse(assessed(rows)["gate"]["native_summary_reconciled"])
        with self.assertRaisesRegex(ValueError,"not bound"):
            assessed(rows,json.loads(Path("pilot-endstat.json").read_text()))


if __name__=="__main__":
    unittest.main()
