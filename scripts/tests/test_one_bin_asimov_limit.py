import io
import json
import unittest
from contextlib import redirect_stdout
from decimal import Decimal, localcontext
from importlib import metadata
from statistics import NormalDist
from unittest.mock import patch

from scripts import one_bin_asimov_limit as limit


class OneBinAsimovTests(unittest.TestCase):
    def test_reference_brackets_and_matches_high_precision_log_likelihood(self):
        ref = limit.reference()
        low, high = ref["bracket"]
        self.assertGreaterEqual(low["cls"], limit.LEVEL)
        self.assertLessEqual(high["cls"], limit.LEVEL)
        self.assertLessEqual(high["mu"] - low["mu"], 1e-12)
        target = NormalDist().inv_cdf(1 - limit.LEVEL / 2) ** 2
        with localcontext() as ctx:
            ctx.prec = 65
            b, s = Decimal("100"), Decimal("20")
            mu = Decimal(str(ref["mu95"]))
            independent_q = 2 * (mu * s - b * ((b + mu * s) / b).ln())
            self.assertAlmostEqual(float(independent_q), target, places=11)
        self.assertAlmostEqual(ref["cls_at_mu95"], limit.LEVEL, places=12)

    def test_limit_monotonic_scaling_and_small_signal(self):
        self.assertEqual(limit.cls(0, 100, 20), 1)
        sequence = [limit.cls(mu, 100, 20) for mu in (0.25, 0.5, 1, 2, 4)]
        self.assertTrue(all(a > b for a, b in zip(sequence, sequence[1:])))
        x = 2e-12
        self.assertAlmostEqual(limit.q_mu(1e-11, 100, 20) / (100 * x**2), 1.0, places=10)
        at_twice_signal = sum(limit.bisect_limit(100, 40, 0.05, 10)) / 2
        self.assertAlmostEqual(at_twice_signal, limit.reference()["mu95"] / 2, places=11)

    def test_invalid_domain_and_short_scan_fail(self):
        for args in [(-1, 100, 20), (1, 0, 20), (1, 100, 0), (float("inf"), 100, 20)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                limit.q_mu(*args)
        with self.assertRaises(ValueError):
            limit.bisect_limit(100, 20, 0.05, 0.5)
        with self.assertRaises(ValueError):
            limit.bisect_limit(100, 20, 1.0, 10)

    def test_histfactory_fixture_has_only_signal_normfactor_and_n_equals_b(self):
        spec = limit.workspace_spec()
        signal, background = spec["channels"][0]["samples"]
        self.assertEqual(signal["modifiers"], [{"name": "mu", "type": "normfactor", "data": None}])
        self.assertEqual(background["modifiers"], [])
        self.assertEqual(background["data"], spec["observations"][0]["data"])

    def test_native_parity_gate_rejects_wrong_tail_and_wrong_limit(self):
        ref = limit.reference()
        correct = [(row["cls"], row["cls"]) for row in ref["points"]]
        mu = ref["mu95"]
        self.assertEqual(limit.compare_native(ref, correct, (mu, mu))["status"], "PASS")
        # Omitting CL_b = 1/2 yields CL_s+b instead of CL_s. A one-sided
        # Gaussian 95% cutoff sets a smaller, incompatible limit.
        omit_clb = [(a / 2, b / 2) for a, b in correct]
        self.assertEqual(limit.compare_native(ref, omit_clb, (mu, mu))["status"], "FAIL")
        wrong_mu = sum(limit.bisect_limit(100, 20, 0.1, 10)) / 2
        self.assertEqual(limit.compare_native(ref, correct, (wrong_mu, wrong_mu))["status"], "FAIL")
        self.assertEqual(limit.compare_native(ref, correct[:-1], (mu, mu))["reason"],
                         "INVALID_NATIVE_OUTPUT")
        self.assertEqual(limit.compare_native(ref, correct, (mu, float("nan")))["status"], "FAIL")

    @patch.object(limit, "native_replay")
    def test_cli_default_has_explicit_not_run(self, native):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(limit.main([]), 0)
        native.assert_not_called()
        report = json.loads(buf.getvalue())
        self.assertEqual(report["native_pyhf"]["status"], "NOT_RUN")
        self.assertIn("NOT_AN_EXPERIMENTAL_LIMIT", report["scope"])

    @patch.object(limit.metadata, "version")
    def test_optional_missing_or_wrong_version_stays_not_run(self, version):
        version.side_effect = metadata.PackageNotFoundError("pyhf")
        self.assertEqual(limit.native_replay(limit.reference())["reason"], "PYHF_NOT_INSTALLED")
        version.side_effect = None
        version.return_value = "0.7.0"
        self.assertEqual(limit.native_replay(limit.reference())["reason"], "PYHF_VERSION_NOT_PINNED")


if __name__ == "__main__":
    unittest.main()
