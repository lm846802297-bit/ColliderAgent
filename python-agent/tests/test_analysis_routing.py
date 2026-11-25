import copy
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "analysis_routing", ROOT / "python-agent/tools/analysis_routing.py")
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)
CAT = json.loads((ROOT / "docs/pheno-analysis-catalog.v1.json").read_text())
STAU = "ATLAS-SUSY-2018-04@HEPData.92006.v2.r2"


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.model = {"facts": {
            "direct_stau_pair": True, "unmixed_degenerate_staus": True,
            "bino_lsp": True, "stau_to_tau_lsp_exclusive_prompt": True,
            "higgs_mass_gev": 125, "invisible_pair_mass_gev": 80,
        }}

    def test_stau_applicable_but_missing_detector(self):
        stau, h = router.route(CAT, self.model)["analyses"]
        self.assertEqual(stau["status"], "blocked_missing_evidence")
        self.assertIn("validated_detector_qcr1_qcr2_wcr", stau["missing_evidence"])
        self.assertEqual(h["status"], "not_applicable")
        self.assertIn("on-shell phase space closed", h["reasons"][0])

    def test_unknown_not_imputed_false(self):
        h = router.route(CAT, {"facts": {}})["analyses"][1]
        self.assertEqual(h["status"], "needs_model_facts")
        self.assertIn("higgs_mass_gev", h["missing_model_facts"])

    def test_threshold_inclusive_closure(self):
        self.model["facts"].update(invisible_pair_mass_gev=62.5)
        self.assertEqual(router.route(CAT, self.model)["analyses"][1]["status"],
                         "not_applicable")
        self.model["facts"].update(invisible_pair_mass_gev=62.49)
        self.assertEqual(router.route(CAT, self.model)["analyses"][1]["status"],
                         "needs_model_facts")

    def test_open_higgs_remains_mapping_only(self):
        self.model["facts"].update(invisible_pair_mass_gev=40,
                                   sm_like_vbf_production=True,
                                   invisible_identical_pair_channel=True)
        h = router.route(CAT, self.model)["analyses"][1]
        self.assertEqual(h["status"], "blocked_missing_evidence")
        self.assertEqual(h["route"], "published-branching-ratio-mapping-only")
        self.assertEqual(h["limit_status"], "not_run")

    def test_ready_is_not_science_pass_or_combination(self):
        self.model["evidence"] = {STAU: dict.fromkeys(CAT["analyses"][0]["requires_evidence"], "a"*64)}
        report = router.route(CAT, self.model)
        self.assertEqual(report["analyses"][0]["status"], "ready_for_review")
        self.assertEqual(report["analyses"][0]["limit_status"], "not_run")
        self.assertEqual(report["combination_status"], "not_attempted")
        self.assertEqual(report["catalog_scope"], "listed_releases_only")

    def test_wrong_release_cannot_fill_evidence(self):
        self.model["evidence"] = {STAU.replace(".v2.", ".v1."): dict.fromkeys(
            CAT["analyses"][0]["requires_evidence"], "b"*64)}
        self.assertEqual(router.route(CAT, self.model)["analyses"][0]["status"],
                         "blocked_missing_evidence")

    def test_reject_bad_fact_and_digest(self):
        self.model["evidence"] = {STAU: {"matched_model_and_spectrum": "yes"}}
        with self.assertRaisesRegex(ValueError, "invalid SHA-256"):
            router.route(CAT, self.model)
        del self.model["evidence"]
        for bad in (True, -1, float("inf"), float("nan"), "80"):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "finite nonnegative"):
                self.model["facts"]["invisible_pair_mass_gev"] = bad
                router.route(CAT, self.model)

    def test_reject_duplicate_record(self):
        cat = copy.deepcopy(CAT)
        cat["analyses"].append(cat["analyses"][0])
        with self.assertRaisesRegex(ValueError, "duplicate catalog"):
            router.route(cat, self.model)

    def test_reject_duplicate_input_key(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text('{"facts": {}, "facts": {}}')
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                router._read(path)

    def test_explicit_false_distinct_from_unknown(self):
        self.model["facts"]["direct_stau_pair"] = False
        stau = router.route(CAT, self.model)["analyses"][0]
        self.assertEqual(stau["status"], "not_applicable")
        self.assertEqual(stau["reasons"], ["model condition false: direct_stau_pair"])


if __name__ == "__main__":
    unittest.main()
