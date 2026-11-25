import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0, str(TOOLS))
import loop_basis_verify as gate


def encode(o):
    return json.dumps(o, sort_keys=True).encode()


def case():
    # Independent hand-derived 2-state source:
    # J1=x I1; J2=r I2; r^2=x+y. dJ1=eps*dlog(x)*J1;
    # dJ2=2 eps*dlog(x+y)*J2. A = B - diag(dlog x,dlog r).
    return {
        "schema": "pheno-loop-source-v1", "variables": ["x","y"], "epsilon": "ep",
        "quadratic_root": {"name": "r", "radicand": "x+y"},
        "masters": ["I1", "I2"],
        "connections": {
            "x": [[0,0,"(ep-1)/x"], [1,1,"(2*ep-1/2)/(x+y)"]],
            "y": [[1,1,"(2*ep-1/2)/(x+y)"]],
        },
        "letters": {"x":"x", "xy":"x+y"},
    }, {
        "schema": "pheno-loop-proposal-v1",
        "transform": [[0,0,"x"],[1,1,"r"]],
        "inverse": [[0,0,"1/x"],[1,1,"r/(x+y)"]],
        "residues":{"x":[[0,0,1]],"xy":[[1,1,2]]},
    }


def check(case):
    s,p = case
    raw = encode(s)
    p.setdefault("source_sha256", gate.digest(raw))
    return gate.verify(raw, encode(p))


def check_exact():
    assert check(case())["status"] == "PASS"


FAILURES = [
    ("wrong_sign", "connection-identity"),
    ("noninvertible", "invalid-inverse"),
    ("pointwise", "connection-identity"),
    ("constant_field_pole", "invalid-input"),
    ("nonconstant_residue", "invalid-input"),
    ("bad_hash", "source-or-schema-mismatch"),
    ("malformed_function", "invalid-input"),
    ("missing_direction", "invalid-input"),
    ("square_radicand", "invalid-input"),
]

def check_reject(failure, wanted):
    s,p=case()
    if failure=="wrong_sign": p["residues"]["x"][0][2] = -1
    if failure=="noninvertible": p["transform"].pop()
    if failure=="pointwise": s["connections"]["x"][0][2] += "+(x-2)*(x-3)*(x-5)"
    if failure=="constant_field_pole": p["inverse"][1][2] = "(r*r-x-y)/(r*r-x-y)"
    if failure=="nonconstant_residue": p["residues"]["x"][0][2] = "ep"
    if failure=="bad_hash": p["source_sha256"] = "0"*64
    if failure=="malformed_function": p["transform"][1][2]="sqrt(x+y)"
    if failure=="missing_direction": del s["connections"]["y"]
    if failure=="square_radicand": s["quadratic_root"]["radicand"] = "(x+y)**2"
    v=check((s,p))
    assert (v["status"],v["reason"]) == ("REJECT",wanted),v


def check_all_directions_must_close():
    s,p=case()
    s["connections"]["y"][0][2] += "+ep"
    assert check((s,p))["direction"] == "y"


def check_nonflat_target():
    s = {"schema":"pheno-loop-source-v1","variables":["x","y"],"epsilon":"ep",
         "masters":["a","b"],"connections":{"x":[[0,1,"ep/x"]],"y":[[1,0,"ep/y"]]},
         "letters":{"x":"x","y":"y"}}
    p = {"schema":"pheno-loop-proposal-v1","transform":[[0,0,1],[1,1,1]],
         "inverse":[[0,0,1],[1,1,1]],"residues":{"x":[[0,1,1]],"y":[[1,0,1]]}}
    assert check((s,p))["reason"] == "nonflat-connection"


def check_timing_protocol(tmp_path):
    s,p=case()
    src=tmp_path/"source.json"
    src.write_bytes(encode(s))
    p["source_sha256"]=gate.digest(src.read_bytes())
    bad=deepcopy(p)
    bad["residues"]["x"][0][2]=-1
    # Replay stub for both arms; this is deliberately not an AI search result.
    fixture=tmp_path/"producer.py"
    fixture.write_text("import sys\nif sys.argv[1]=='bad-first': print("+
                       repr(encode(bad).decode())+", flush=True)\nprint("+
                       repr(encode(p).decode())+", flush=True)\n")
    archive=tmp_path/"run"
    run=subprocess.run([sys.executable,str(TOOLS/"loop_basis_benchmark.py"),str(src),str(archive),
                        "--fixed",json.dumps([sys.executable,str(fixture),"valid"]),
                        "--agent",json.dumps([sys.executable,str(fixture),"bad-first"]),
                        "--budget-s","15","--expected-source-sha256",p["source_sha256"]],
                       capture_output=True)
    assert run.returncode == 0,run.stderr
    result=json.loads((archive/"comparison.json").read_text())
    by_arm={r["arm"]:r for r in result["results"]}
    assert [x["status"] for x in by_arm["agent"]["trials"]]==["REJECT","PASS"]
    assert by_arm["fixed"]["input_sha256"]==by_arm["agent"]["input_sha256"]==p["source_sha256"]
    assert all(x["time_to_first_pass_s"]>0 for x in by_arm.values())

class BasisGateTests(unittest.TestCase):
    def test_exact(self):
        check_exact()

    def test_reject(self):
        for failure, wanted in FAILURES:
            with self.subTest(failure=failure):
                check_reject(failure, wanted)

    def test_all_directions(self):
        check_all_directions_must_close()

    def test_nonflat(self):
        check_nonflat_target()

    def test_triangular_noncommuting_transform(self):
        # T=[[1,x],[0,1]], and A=T^-1(BT-T').
        src = {"schema":"pheno-loop-source-v1","variables":["x"],"epsilon":"ep",
               "masters":["a","b"],"letters":{"x":"x"},
               "connections":{"x":[[0,0,"ep/x"],[0,1,"-ep-1"],[1,1,"2*ep/x"]]}}
        p = {"schema":"pheno-loop-proposal-v1","transform":[[0,0,1],[0,1,"x"],[1,1,1]],
             "inverse":[[0,0,1],[0,1,"-x"],[1,1,1]],"residues":{"x":[[0,0,1],[1,1,2]]}}
        assert check((src,p))["status"] == "PASS"
        p["transform"],p["inverse"]=p["inverse"],p["transform"]
        assert check((src,p))["reason"] == "connection-identity"

    def test_size_37_five_directions(self):
        # A dimension/coverage stress fixture, not a CANON or IBP benchmark.
        n = 37
        xs = ["s", "t", "q3", "q4", "m2"]
        src = {"schema":"pheno-loop-source-v1","variables":xs,"epsilon":"ep",
               "masters":[f"I{i}" for i in range(n)],"letters":{x:x for x in xs},
               "connections":{x:[[i,i,f"(ep-1)/{x}"] for i in range(n)] if x=="s"
                              else [[i,i,f"ep/{x}"] for i in range(n)] for x in xs}}
        p = {"schema":"pheno-loop-proposal-v1","transform":[[i,i,"s"] for i in range(n)],
             "inverse":[[i,i,"1/s"] for i in range(n)],
             "residues":{x:[[i,i,1] for i in range(n)] for x in xs}}
        verdict = check((src,p))
        assert verdict["status"] == "PASS", verdict
        assert verdict["masters"] == 37 and verdict["directions"] == xs
        src["connections"]["m2"][-1][-1] += "+ep"
        del p["source_sha256"]
        verdict = check((src,p))
        assert (verdict["status"],verdict["direction"],verdict["row"]) == ("REJECT","m2",36)

    def test_timing(self):
        with tempfile.TemporaryDirectory() as tmp:
            check_timing_protocol(Path(tmp))


if __name__ == "__main__":
    unittest.main()
