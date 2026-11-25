"""Independent stdlib reader for counts/weights and stable vectors in this format."""
import argparse
from collections import Counter
import gzip
from itertools import zip_longest
import json
import math
from pathlib import Path


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def events(path):
    expected, current, footer = None, None, False
    with open(path, encoding="ascii") as f:
        for line in f:
            a = line.split()
            if not a:
                continue
            typ = a[0]
            if typ == "HepMC::Asciiv3-END_EVENT_LISTING":
                footer = True
                break
            if typ == "E":
                if current is not None:
                    ensure(current["particles"] == expected, "particle count")
                    yield current
                number, vertices, expected = map(int, a[1:4])
                ensure(vertices == 5, "five vertices expected")
                current = {"key": number, "stable": Counter(), "particles": 0}
            elif current is not None:
                if typ == "W":
                    ensure(len(a) == 2 and "weight" not in current, "ambiguous weight")
                    current["weight"] = float(a[1])
                elif typ == "U":
                    ensure(a[1:] == ["GEV", "MM"], "wrong units")
                    current["units"] = True
                elif typ == "A" and a[1:3] == ["0", "source_id"]:
                    current["source_id"] = a[3]
                elif typ == "P":
                    current["particles"] += 1
                    if int(a[9]) == 1:
                        current["stable"][(int(a[3]), tuple(map(float, a[4:8])))] += 1
    ensure(footer and current is not None and current["particles"] == expected, "incomplete stream")
    yield current


def compare(input_path, hepmc_path):
    weights = []
    seen = set()
    with gzip.open(input_path,"rt",encoding="utf8") as f:
        for r, e in zip_longest(map(json.loads, f), events(hepmc_path)):
            ensure(r is not None and e is not None, "event count")
            a,b = map(int,r["event_id"].split(":"))
            ensure(e["source_id"] not in seen and (e["key"]//10000,e["key"]%10000)==(a,b)
                   and e["source_id"]==r["event_id"], "event ID")
            seen.add(e["source_id"])
            ensure(e["weight"] == r["weight_fb"] and e["units"], "changed weight or units")
            truth = Counter((x,tuple(p)) for x,p in r["other_particles"])
            for t in r["taus"]:
                truth[1000022,tuple(t["neutralino"])] += 1
                truth.update((x,tuple(p)) for x,p in t["products"])
            ensure(e["stable"] == truth, "modified stable four-vector or multiplicity")
            weights.append(e["weight"])
    return {"status":"PASS","events":len(weights),"total_weight_fb":math.fsum(weights),
            "independent_ascii_exact_stable_multisets":True}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input"); p.add_argument("hepmc"); p.add_argument("report")
    a=p.parse_args()
    Path(a.report).write_text(json.dumps(compare(a.input,a.hepmc),sort_keys=True,indent=2)+"\n")
