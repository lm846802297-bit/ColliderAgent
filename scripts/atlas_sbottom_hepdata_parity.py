"""Offline parity for one exact official HEPData HistFactory archive."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

ARCHIVE = "9089b0e5fabba335bea4c94545ccca8ddd21289feeab2f85e5bcc8bada37be70"
BASE = "RegionA/BkgOnly.json"
MEMBERS = {
    BASE: "9f308fb619d6fad7783c61ae7b99532c6154c9dcc30e37821024471b140d8b5b",
    "RegionA/patch.sbottom_1300_205_60.json":
        "1cc45828ad4c1ff31bdf826b140364f71051490fd0b469d96c12940d522bdb85",
    "RegionA/patch.sbottom_1300_230_100.json":
        "b87da244cfa08cca84f8e9b636937451f741d749cd821f7fd48f318d34236e13",
}
OBSERVED = (0.2444363799054463, 0.040766026035752724)
FIRST_OBSERVED_ALT = 0.24443627759085326
FIRST_BAND = (0.09022509053507759, 0.1937839194960632, 0.38432344933992,
              0.6557757334303531, 0.8910420971601081)
TOL = 5e-4


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_members(archive):
    """Read only the three known regular files, never extract tar paths."""
    from io import BytesIO
    with archive.open("rb") as stream:
        raw = stream.read(2036565)
    if len(raw) != 2036564 or sha(raw) != ARCHIVE:
        raise ValueError("wrong exact HEPData archive bytes")
    out = {}
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as handle:
        for member in handle:
            if member.name not in MEMBERS:
                continue
            if member.name in out or not member.isfile() or member.size > 3_000_000:
                raise ValueError("unexpected pinned archive member type or size")
            with handle.extractfile(member) as fp:
                data = fp.read()
            if sha(data) != MEMBERS[member.name]:
                raise ValueError(f"wrong member SHA-256: {member.name}")
            out[member.name] = data
    if out.keys() != MEMBERS.keys():
        raise ValueError("missing pinned member")
    return out


def replay(archive):
    import numpy
    import pyhf
    import scipy
    from jsonpatch import JsonPatch
    from platform import python_version

    if pyhf.__version__ != "0.7.6":
        raise ValueError("pyhf 0.7.6 required")
    pyhf.set_backend("numpy", "scipy", precision="64b")
    raw = load_members(archive)
    base = json.loads(raw[BASE])
    results = []
    for pos, member in enumerate(name for name in MEMBERS if name != BASE):
        ws = pyhf.Workspace(JsonPatch(json.loads(raw[member])).apply(base))
        model = ws.model()
        config = model.config
        data = ws.data(model)
        if config.poi_name is None or len(data) <= len(config.auxdata):
            raise ValueError("missing POI or physical bins")
        free_nuisance = sum(not fixed for fixed in config.suggested_fixed()) - 1
        if not config.auxdata or free_nuisance <= 0:
            raise ValueError("expected profiled nuisance parameters")
        obs, band = pyhf.infer.hypotest(
            1., data, model, calctype="asymptotics", test_stat="qtilde",
            return_expected_set=True,
        )
        obs, band = float(obs), [float(x) for x in band]
        if len(band) != 5 or not all(0. <= x <= 1. for x in [obs, *band]):
            raise ValueError("invalid CLs result")
        residuals = {"observed_minus_chep": obs - OBSERVED[pos]}
        if pos == 0:
            residuals["observed_minus_fairs"] = obs - FIRST_OBSERVED_ALT
            residuals["expected_minus_fairs"] = [x - y for x, y in zip(band, FIRST_BAND)]
        checks = [residuals["observed_minus_chep"]]
        if pos == 0:
            checks.extend([residuals["observed_minus_fairs"], *residuals["expected_minus_fairs"]])
        passed = max(map(abs, checks)) <= TOL and (obs < .05) == (OBSERVED[pos] < .05)
        results.append({"patch_member": member, "workspace_schema": ws.version,
                        "measurements": ws.measurement_names, "channels": config.channel_nbins,
                        "poi": config.poi_name, "data_bins": config.nmaindata,
                        "aux_data_count": len(config.auxdata),
                        "free_nuisance_count": free_nuisance, "observed_cls": obs,
                        "expected_cls_bands": band, "signed_residuals": residuals,
                        "published_target_gate_passed": passed})
    return {"archive_sha256": ARCHIVE, "member_sha256": MEMBERS, "poi_test": 1.,
            "test_stat": "qtilde", "calctype": "asymptotics", "tolerance": TOL,
            "runtime": {"pyhf": pyhf.__version__, "python": python_version(),
                        "numpy": numpy.__version__, "scipy": scipy.__version__,
                        "precision": pyhf.tensorlib.precision},
            "published_reference_parity": all(r["published_target_gate_passed"] for r in results),
            "results": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    output = replay(parser.parse_args().archive)
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(not output["published_reference_parity"])
