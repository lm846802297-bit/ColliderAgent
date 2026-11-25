import json
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve()
sys.path.insert(0,str(HERE.parents[1]/"tools"))
from kira_pdb_export import convert


class NativeExport(unittest.TestCase):
    def setUp(self):
        self.base=HERE.parents[2]/"research/loop_basis/double_box_kira/native_discovery"
        self.target=(self.base/"sector30-targets.txt").read_text().splitlines()
        self.masters=self.target[:1]
        self.native=(self.base/"sector30-native.m").read_bytes()

    def test_real_rules_and_master_omitted(self):
        compared=json.loads((self.base/"sector30-normalized.json").read_text())
        self.assertEqual(convert(self.native,self.masters,self.target),compared)

    def test_unresolved_zero_not_implied(self):
        with self.assertRaisesRegex(ValueError,"unresolved"):
            convert(self.native,self.masters,self.target+["PDB[1,1,1,1,1,0,0,0,0]"])

    def test_native_names_and_unsupported_code(self):
        changed=self.native.replace(b"(s)*(1)",b"(q3sq)*(1)")
        coeff=convert(changed,self.masters,self.target)["rules"][self.target[1]][self.masters[0]]
        self.assertEqual(coeff,"(3 - d)/Q3sq")
        with self.assertRaises(ValueError):
            convert(changed.replace(b"q3sq",b"Run(34)"),self.masters,self.target)


if __name__=="__main__":
    unittest.main()
