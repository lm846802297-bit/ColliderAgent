"""Opt-in, exact check of Chang–Wan–Zhou arXiv:2611.26692v1 Eq. (18)."""
import argparse
from collections.abc import Mapping
from fractions import Fraction
import json
from pathlib import Path
import re

BASIS = "arxiv:2611.26692v1:appendix-D:rescaled-F-over-Lambda4"
SOURCE = "https://arxiv.org/html/2611.26692v1"
KEYS = ("F_M1", "F_M3", "F_M5", "F_M7")
UNITS = ("GeV^-4", "TeV^-4")
_NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee]([+-]?[0-9]+))?|[+-]?[0-9]+/[0-9]+")


def _rational(value):
    if type(value) is int and abs(value).bit_length() <= 425:
        return Fraction(value)
    if not isinstance(value, str) or len(value) > 128:
        raise ValueError("use an integer, exact decimal string, or rational string")
    match = _NUMBER.fullmatch(value)
    if match is None or (match[1] is not None and abs(int(match[1])) > 1000):
        raise ValueError("use an exact finite number with exponent magnitude at most 1000")
    return Fraction(value)


def check_eq18(payload):
    """Return a result for this constraint only; do not map or infer bases."""
    report = {"constraint": "CWZ-v1-Eq18", "source": SOURCE,
              "kind": "theory_screen_only", "status": "UNDETERMINED"}
    if not isinstance(payload, Mapping) or payload.get("basis_id") != BASIS:
        return {**report, "reason": "missing or incompatible coefficient convention"}
    unit = payload.get("unit")
    if unit not in UNITS:
        return {**report, "reason": "a supported common coefficient unit is required"}
    values = payload.get("coefficients")
    if not isinstance(values, Mapping) or set(values) != set(KEYS):
        return {**report, "reason": "supply exactly the four required F coefficients"}
    try:
        f1, f3, f5, f7 = (_rational(values[key]) for key in KEYS)
    except (ValueError, ZeroDivisionError) as error:
        return {**report, "reason": str(error)}

    a, b, c = f7 - 8*f1, -f5, -4*f3
    det = a*c - b*b
    failures = [name for name, value in (
        ("Ftilde13", a), ("-4 F_M3", c), ("determinant", det)
    ) if value < 0]
    status = "OUTSIDE" if failures else "BOUNDARY" if det == 0 else "INTERIOR"
    return {**report, "status": status, "coefficient_unit": unit,
            "hankel_matrix_exact": [[str(a), str(b)], [str(b), str(c)]],
            "determinant_exact": str(det), "failed_principal_minors": failures}


def _unique_object(items):
    obj = {}
    for key, value in items:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with basis_id, unit and coefficients")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_object)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(check_eq18(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
