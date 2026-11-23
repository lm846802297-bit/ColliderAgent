import math
import unittest

from scripts import elastic_shm_reference as ref


class ElasticShmReferenceTests(unittest.TestCase):
    def test_fixed_grid_and_refinement(self):
        result = ref.run_benchmark()
        self.assertEqual(result["reference_status"], "PASS")
        self.assertEqual(result["native_ddcalc"], "NOT_RUN")
        self.assertGreaterEqual(len(result["points"]), 16)
        self.assertLessEqual(result["max_eta_abs_residual_s_per_km"], ref.ETA_ATOL)
        self.assertLessEqual(result["max_eta_refinement_s_per_km"], ref.ETA_ATOL)
        self.assertLessEqual(result["max_normalization_relative_residual"], ref.NORM_ATOL)

    def test_join_continuity_and_cutoff(self):
        halo = ref.Halo(220, 544, 232)
        join = halo.escape - halo.boost
        cutoff = halo.escape + halo.boost
        f = lambda v: ref.eta_analytic(v, halo)
        center = f(join)
        self.assertGreater(f(join - 1e-5), center)
        self.assertGreater(center, f(join + 1e-5))
        self.assertLess(abs(f(join - 1e-5) - f(join + 1e-5)), 2e-10)
        self.assertGreater(f(cutoff - 0.1), 0)
        self.assertEqual(f(cutoff), 0)
        self.assertEqual(f(cutoff + 0.1), 0)
        self.assertEqual(ref.eta_galactic_shell(cutoff, halo)[0], 0)

    def test_zero_boost_and_monotonicity(self):
        at_rest = ref.Halo(220, 544, 0)
        f = lambda v: ref.eta_analytic(v, at_rest)
        self.assertGreater(f(0), f(220))
        self.assertGreater(f(220), f(543))
        self.assertEqual(f(544), 0)
        self.assertLess(abs(f(0) - ref.eta_analytic(0, ref.Halo(220, 544, 0.01))), 1e-11)

    def test_elastic_unit_map_and_wrong_units_reject(self):
        vmin = ref.elastic_vmin_km_s(8.0, 122.0, 50.0)
        q_gev = math.sqrt(2 * 122 * 8e-6)
        reduced = 1 / (1 / 122 + 1 / 50)
        self.assertAlmostEqual(vmin, ref.C_KM_S * q_gev / (2 * reduced), places=12)
        self.assertAlmostEqual(ref.elastic_vmin_km_s(32.0, 122.0, 50.0), 2 * vmin)
        wrong = ref.elastic_vmin_km_s(8e6, 122.0, 50.0)
        self.assertAlmostEqual(wrong / vmin, 1e3)
        halo = ref.Halo(220, 544, 232)
        self.assertGreater(ref.eta_analytic(vmin, halo), 0)
        self.assertEqual(ref.eta_analytic(wrong, halo), 0)

    def test_bad_inputs_fail(self):
        with self.assertRaises(ValueError):
            ref.Halo(220, 544, 544)
        halo = ref.Halo(220, 544, 232)
        with self.assertRaises(ValueError):
            ref.eta_analytic(float("nan"), halo)
        with self.assertRaises(ValueError):
            ref.eta_galactic_shell(2, halo, panels=3)
        with self.assertRaises(ValueError):
            ref.elastic_vmin_km_s(8, 0, 50)


if __name__ == "__main__":
    unittest.main()
