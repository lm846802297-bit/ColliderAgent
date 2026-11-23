import io
import json
import unittest
from contextlib import redirect_stdout
from fractions import Fraction as F

from scripts import qed_tree_reference as ref


class QedTreeReferenceTests(unittest.TestCase):
    def test_trace_matches_mandelstam_and_angular_formulas_exactly(self):
        for point in ref.POINTS:
            with self.subTest(point=point):
                out = ref.reference_point(*point)
                t, u, z = (out[key] for key in ("t_over_s", "u_over_s", "cos_theta"))
                value = out["spin_averaged_M2_over_e4"]
                self.assertEqual(1 + t + u, 0)
                self.assertEqual((t, u), (-F(1 - z, 2), -F(1 + z, 2)))
                self.assertEqual(value, 2 * (t**2 + u**2))
                self.assertEqual(value, 1 + z**2)
                self.assertTrue(out["electron_ward_tensor_zero"])
                self.assertTrue(out["muon_ward_tensor_zero"])

    def test_orientation_differential_shape_and_energy_scaling(self):
        forward = ref.reference_point(5, 4, 3)
        self.assertEqual((forward["t_over_s"], forward["u_over_s"]), (F(-1, 5), F(-4, 5)))
        value = "spin_averaged_M2_over_e4"
        self.assertEqual(forward[value], F(34, 25))
        self.assertEqual(ref.reference_point(5, 4, -3)[value], forward[value])
        self.assertEqual(ref.reference_point(5, 5, 0)[value], 1)
        self.assertEqual(ref.reference_point(5, 0, 5)[value], 2)
        large = ref.reference_point(10, 8, 6)
        self.assertEqual(large[value], forward[value])
        self.assertEqual(F(forward["s_GeV2"], large["s_GeV2"]), F(1, 4))

    def test_bad_kinematics_rejected_and_report_does_not_claim_native(self):
        for point in ((5, 4, 4), (5, -4, 3), (0, 0, 0)):
            with self.assertRaises(ValueError):
                ref.reference_point(*point)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ref.main()
        report = json.loads(buf.getvalue())
        self.assertEqual(report["scope"], "PYTHON_EXACT_TRACE_REFERENCE_ONLY")
        self.assertEqual(report["wolfram_interoperability"], "NOT_RUN")
        self.assertEqual(len(report["points"]), 6)


if __name__ == "__main__":
    unittest.main()
