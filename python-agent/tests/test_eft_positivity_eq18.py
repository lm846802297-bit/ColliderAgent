from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from eft_positivity_eq18 import BASIS, KEYS, check_eq18


def payload(values, basis=BASIS, unit="TeV^-4"):
    return {"basis_id": basis, "unit": unit,
            "coefficients": dict(zip(KEYS, (str(v) for v in values)))}


def vector_f(g1, g2, scale):
    # Eq. (20) matching (display directly below it); lambda = 1/(f² M_V²).
    return (-scale*g1*g1, -4*scale*g2*g2, 8*scale*g1*g2, -4*scale*g1*g1)


def numerical(values):
    f1, f3, f5, f7 = map(Fraction, values)
    matrix = np.array([[float(f7)-8*float(f1), -float(f5)],
                       [-float(f5), -4*float(f3)]])
    matrix /= np.max(np.abs(matrix)) or 1.0
    least = np.linalg.eigvalsh(matrix)[0]
    return "OUTSIDE" if least < -1e-13 else "INTERIOR" if least > 1e-13 else "BOUNDARY"


class Eq18Tests(unittest.TestCase):
    def test_heavy_vector_boundary_both_signs_and_axes(self):
        for g1, g2 in [(2, 3), (2, -3), (0, 3), (2, 0), (0, 0)]:
            with self.subTest(couplings=(g1, g2)):
                scale = Fraction(1, 81)
                values = vector_f(g1, g2, scale)
                result = check_eq18(payload(values))
                self.assertEqual(result["status"], "BOUNDARY")
                self.assertEqual(result["status"], numerical(values))
                matrix = list(map(lambda row: list(map(Fraction, row)),
                                  result["hankel_matrix_exact"]))
                # Independent signed Gram vector; this probes the off-diagonal sign.
                v = [2*g1, -4*g2]
                self.assertEqual(matrix, [[scale*x*y for y in v] for x in v])
                if g1 and g2:
                    null = [values[2], values[3]-8*values[0]]
                    self.assertEqual([sum(x*y for x, y in zip(row, null))
                                      for row in matrix], [0, 0])

    def test_cone_and_diagonal_controls(self):
        for values, expected in [
            ((0, -1, 1, 4), "INTERIOR"), ((0, -1, 5, 4), "OUTSIDE"),
            ((0, 1, 0, -4), "OUTSIDE"), ((0, -1, 1, 0), "OUTSIDE"),
            ((0, -1, 0, -1), "OUTSIDE"), ((0, 1, 0, 1), "OUTSIDE"),
        ]:
            with self.subTest(values=values):
                self.assertEqual(check_eq18(payload(values))["status"], expected)
                self.assertEqual(numerical(values), expected)

    def test_exact_sign_not_float_tolerance(self):
        for shift, expected in [(1, "OUTSIDE"), (-1, "INTERIOR"), (0, "BOUNDARY")]:
            mix = Fraction(4) + shift*Fraction(1, 10**60)
            self.assertEqual(check_eq18(payload((0, -1, mix, 4)))["status"], expected)

    def test_homogeneity(self):
        values = vector_f(2, -3, Fraction(2, 81))
        self.assertEqual(check_eq18(payload(values))["status"],
                         check_eq18(payload(
                             [v/Fraction(10**12) for v in values], unit="GeV^-4"))["status"])

    def test_incompatible_or_incomplete_input(self):
        good = payload((0, -1, 1, 4))
        for data in (None, {}, {**good, "basis_id": "unrescaled_Eboli"},
                     {**good, "unit": {"F_M1": "TeV^-4"}},
                     {**good, "coefficients": {"F_M1": "0"}},
                     {**good, "coefficients": {**good["coefficients"], "f_M5": "1"}}):
            self.assertEqual(check_eq18(data)["status"], "UNDETERMINED")

    def test_invalid_numbers(self):
        good = payload((0, -1, 1, 4))
        for x in (True, None, 1.0, "NaN", "inf", "1/0", "1e1001", "1 + 2"):
            good["coefficients"]["F_M1"] = x
            self.assertEqual(check_eq18(good)["status"], "UNDETERMINED")

    def test_large_finite_numbers_are_exact(self):
        self.assertEqual(check_eq18(payload(("0", "-1e1000", "0", "1e1000")))["status"],
                         "INTERIOR")

    def test_cli_and_duplicate_keys(self):
        entry = Path(__file__).resolve().parents[1] / "tools/eft_positivity_eq18.py"
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "p.json"
            f.write_text(json.dumps(payload((0, -1, 1, 4))), encoding="utf-8")
            out = subprocess.check_output([sys.executable, str(entry), str(f)], text=True)
            self.assertEqual(json.loads(out)["determinant_exact"], "15")
            f.write_text('{"basis_id": 1, "basis_id": 2}', encoding="utf-8")
            run = subprocess.run([sys.executable, str(entry), str(f)],
                                 text=True, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("duplicate JSON key", run.stderr)
