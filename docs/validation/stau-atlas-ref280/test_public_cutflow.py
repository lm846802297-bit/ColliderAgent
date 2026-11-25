import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from public_cutflow import audit, ROOT


class PublicCutflow(unittest.TestCase):
    def test_known_control_points_and_uncertainty(self):
        record=audit()
        hi=record["benchmarks"]["280_1"]["regions"]["high"]
        lo=record["benchmarks"]["280_1"]["regions"]["low"]
        self.assertEqual([lo["stages"][-1]["weighted"],hi["stages"][-1]["weighted"]],["6.08","14.35"])
        self.assertEqual([lo["stages"][-1]["stat"],hi["stages"][-1]["stat"]],["0.79","1.13"])
        self.assertEqual([lo["stages"][-1]["raw_count"],hi["stages"][-1]["raw_count"]],[278,691])

    def test_published_recast_not_confused_with_full_detector(self):
        record=audit()
        low=record["benchmarks"]["120_1"]["regions"]["low"]
        self.assertGreater(low["ma5_final_relative_difference"],.49)
        self.assertEqual(record["detector_validation"],"NOT_RUN")
        self.assertEqual(record["five_region_fitting"],"NOT_RUN")
        self.assertIn("no_signal_cutflow",record["published_t18"])

    def test_wrong_record_and_nonmonotone_rejected(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for p in ["atlas-t17.json","atlas-t18.json"]:
                (root/p).write_bytes((ROOT/p).read_bytes())
            p=root/"atlas-t17.json"
            j=json.loads(p.read_text())
            j["doi"]="10.17182/hepdata.92006.v1/t17"
            p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,"provenance"):
                audit(root)
            j["doi"]="10.17182/hepdata.92006.v2/t17"
            j["values"][13]["y"][2]["value"]="160"
            p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,"non-monotone"):
                audit(root)

    def test_region_order_distinguishes_same_label_cut(self):
        regions=audit()["benchmarks"]["280_1"]["regions"]
        self.assertEqual([regions[n]["stages"][-1]["id"] for n in ["low","high"]],[13,19])
        self.assertAlmostEqual(regions["low"]["atlas_eff_times_acc"],6.08/1147.71)
        self.assertAlmostEqual(regions["high"]["atlas_eff_times_acc"],14.35/1147.71)


if __name__=="__main__":
    unittest.main()
