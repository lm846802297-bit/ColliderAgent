from pathlib import Path
import sys
import unittest

import sympy as sp

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "scripts"))
from sunrise_basis_smoke import audit_basis, compare_basis_reports, models, run, time_exact_replay, z, eps


class IntegralBasisTest(unittest.TestCase):
    def test_published_block_and_alternative(self):
        q, _, _ = run()
        a, b = q["fixed_lowest_dot"], q["ai_weighted_derivative"]
        self.assertEqual((a["nonzero_entries"], b["nonzero_entries"]), (5, 4))
        self.assertEqual((a["apparent_infinity_pole_order"], b["apparent_infinity_pole_order"]), (1, 3))
        self.assertEqual((a["epsilon_factorized"], b["epsilon_factorized"]), (False, False))
        self.assertEqual(q["structural_decision"]["recommendation"], "KEEP_BASELINE")

    def test_singular_candidate_is_rejected(self):
        a, ref, _, _ = models()
        with self.assertRaisesRegex(ValueError, "singular"):
            audit_basis(a, sp.zeros(3), z, eps, ref)

    def test_bad_source_sign_is_rejected(self):
        a, _, t, ref = models()
        ref[1, 2] *= -1
        with self.assertRaisesRegex(ValueError, "independent"):
            audit_basis(a, t, z, eps, ref)

    def test_missing_derivative_of_basis_is_rejected(self):
        a, _, t, _ = models()
        wrong = t*a*t.inv()
        with self.assertRaisesRegex(ValueError, "independent"):
            audit_basis(a, t, z, eps, wrong)

    def test_only_linear_epsilon_classifies(self):
        for v, expect in [(eps/z, True), (eps**2/z, False), (1/z, False), (eps/(1-2*eps), False)]:
            f = sp.Matrix([[v]])
            with self.subTest(v=v):
                _, report = audit_basis(f, sp.eye(1), z, eps, f)
                self.assertEqual(report["epsilon_factorized"], expect)

    def test_new_finite_pole_refuses_promotion(self):
        a = sp.zeros(1)
        _, base = audit_basis(a, sp.eye(1), z, eps, a)
        _, candidate = audit_basis(a, sp.Matrix([[z-2]]), z, eps, sp.Matrix([[1/(z-2)]]))
        self.assertEqual(compare_basis_reports(base, candidate)["recommendation"], "KEEP_BASELINE")

    def test_replay_is_not_ibp_and_rejects_singular_points(self):
        a = sp.Matrix([[1/z]])
        counter = iter(range(100))
        v = time_exact_replay([a,a], [[(z,1)]], repetitions=3, timer=lambda: next(counter))
        self.assertEqual(v["samples_ns"], [[1,1,1],[1,1,1]])
        self.assertIn("no native IBP", v["scope"])
        with self.assertRaisesRegex(ValueError, "singular"):
            time_exact_replay([a,a], [[(z,0)]])


if __name__ == "__main__":
    unittest.main()
