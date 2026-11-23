"""Read the archived native LHE without changing generator output."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse(raw):
    # The tagged Git checkout puts four red ANSI alert lines in MG5ProcCard.
    # Only those observed pairs inside that one header card are allowed.
    if b"\x1b" in raw:
        a, b = raw.index(b"<MG5ProcCard>"), raw.index(b"</MG5ProcCard>")
        pre, card, post = raw[:a], raw[a:b], raw[b:]
        opening, closing = b"\x1b[1;31m", b"\x1b[1;0m"
        require(a < b and raw.count(b"<MG5ProcCard>") == raw.count(b"</MG5ProcCard>") == 1,
                "unexpected process header bounds")
        require(len(re.findall(re.escape(opening) + rb"[^\x1b\r\n]*" + re.escape(closing), card)) == 4
                and raw.count(b"\x1b") == 8, "unexpected ANSI outside known process header")
        view = pre + card.replace(opening, b"").replace(closing, b"") + post
    else:
        view = raw
    # The event region must be strictly XML (including particle block sizes).
    return ET.fromstring(view), view


def lines(node):
    return [line.split() for line in node.text.strip().splitlines() if line.strip()]


def analyze(path):
    packed = path.read_bytes()
    raw = gzip.decompress(packed)
    doc, view = parse(raw)
    require(doc.tag == "LesHouchesEvents" and doc.attrib.get("version") == "3.0",
            "unexpected LHE file envelope")
    init = doc.find("init")
    gen = init.find("generator")
    require(gen.attrib["name"] == "MadGraph5_aMC@NLO" and gen.attrib["version"] == "3.5.17",
            "unexpected generator")
    beam, norm = lines(init)
    require(beam[:2] == ["-11", "11"] and [float(x) for x in beam[2:4]] == [50.,50.]
            and beam[4:] == ["0","0","0","0","-4","1"] and norm[3] == "1",
            "wrong lepton beams, beam PDFs or weight scheme")
    sigma, error, _ = map(float, norm[:3])
    require(sigma > 0 and 0 < error < .01*sigma, "unusable reported integration uncertainty")
    seed = re.search(r"^\s*(\d+)\s*=\s*iseed\b", doc.find("header/MGRunCard").text, re.M)
    require(seed and seed[1] == "27183", "wrong archived seed")
    proc = doc.find("header/MG5ProcCard").text
    require("generate e+ e- > mu+ mu- / z" in proc, "wrong archived process")
    card = doc.find("header/slha").text
    inv_alpha = float(re.search(r"^\s*1\s+([0-9.Ee+-]+)\s+#\s*aewm1", card, re.M)[1])
    require(abs(inv_alpha - 137.035999084) < 1e-5, "wrong archived electromagnetic coupling")
    sigma_ref = 4*math.pi / (3*100.**2*inv_alpha**2) * 3.893793719e8
    sigma_delta = sigma - sigma_ref
    require(abs(sigma_delta) <= max(.005*sigma_ref, 5*error), "cross-section gate failed")
    event_nodes = doc.findall("event")
    require(len(event_nodes) == 5000, "wrong full event count")
    accepted = 0
    max_p = 0.
    weights = []
    for event in event_nodes:
        head, *rows = lines(event)
        require(len(head) == 6 and head[:2] == ["4", "1"] and len(rows) == 4
                and all(len(row) == 13 for row in rows), "wrong LHE event block length")
        require(all(math.isfinite(float(x)) for row in [head,*rows] for x in row), "non-finite event")
        require([(int(r[0]), int(r[1])) for r in rows] == [(-11,-1),(11,-1),(-13,1),(13,1)],
                "unexpected particle IDs or outgoing statuses")
        p = [[float(x) for x in r[6:11]] for r in rows]
        require(all(v[4] == 0. and abs(v[3]-50.) <= 2e-5
                    and abs(math.hypot(*v[:3])-v[3]) <= 2e-5 for v in p), "off-shell kinematics")
        require(all(abs(v[i]) <= 2e-5 for v in p[:2] for i in (0,1))
                and p[0][2] > 0 > p[1][2], "wrong beam axis")
        dp = max(abs(p[0][i]+p[1][i]-p[2][i]-p[3][i]) for i in range(4))
        require(dp <= 2e-5, "four-momentum conservation gate failed")
        max_p = max(max_p, dp)
        w = float(head[2])
        require(w > 0 and abs(w/sigma-1.) < 1e-10, "wrong average-convention weight")
        weights.append(w)
        mu, electron = p[3],p[1]
        c = sum(mu[i]*electron[i] for i in range(3))/(math.hypot(*mu[:3])*math.hypot(*electron[:3]))
        accepted += abs(c) < .8
    n = len(weights)
    frac = accepted/n
    target = 3*.8/4 + .8**3/4
    se = math.sqrt(target*(1-target)/n)
    require(abs(frac-target) <= 5*se, "angular acceptance gate failed")
    return dict(raw_gzip_sha256=hashlib.sha256(packed).hexdigest(),
                raw_lhe_sha256=hashlib.sha256(raw).hexdigest(),
                read_view_sha256=hashlib.sha256(view).hexdigest(),
                header_ansi_escapes_removed=raw.count(b"\x1b"), accepted=accepted,
                generated=n, acceptance=frac, analytic_acceptance=target,
                signed_acceptance_sigma=(frac-target)/se, sum_weights_pb=sum(weights),
                cross_section_pb=sigma, integration_sigma_pb=error, analytic_cross_section_pb=sigma_ref,
                signed_cross_section_delta_pb=sigma_delta, fiducial_cross_section_pb=frac*sigma,
                alpha_inverse=inv_alpha, max_conservation_residual_GeV=max_p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_lhe_gzip", type=Path)
    print(json.dumps(analyze(parser.parse_args().native_lhe_gzip), indent=2, allow_nan=False))
