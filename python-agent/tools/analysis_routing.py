"""Deterministic experimental routing from reviewed model facts, without executing a fit."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re


def _unique(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ValueError(f"duplicate key: {key}")
        out[key] = value
    return out


def _reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique,
                      parse_constant=_reject_constant)


def _string_list(items, field):
    if (not isinstance(items, list) or
            any(not isinstance(x, str) or not x for x in items) or
            len(items) != len(set(items))):
        raise ValueError(f"{field} must be a list of unique nonempty strings")
    return items


def _mass(facts, key):
    if key not in facts:
        return None
    value = facts[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{key} must be a finite nonnegative mass in GeV")
    try:
        if math.isfinite(value):
            return value
    except OverflowError:
        pass
    raise ValueError(f"{key} must be a finite nonnegative mass in GeV")


def route(catalog, model):
    if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        raise ValueError("unsupported catalog schema version")
    version = catalog["catalog_version"]
    if not isinstance(version, str) or not version:
        raise ValueError("missing catalog version")
    facts, evidence = model["facts"], model.get("evidence", {})
    if not isinstance(facts, dict) or not isinstance(evidence, dict):
        raise ValueError("facts and evidence must be objects")
    seen, reports = set(), []
    for entry in catalog["analyses"]:
        ident, release = entry["id"], entry["release"]
        if any(not isinstance(x, str) or not x or "@" in x for x in (ident, release)):
            raise ValueError("invalid analysis or release identity")
        identity = f"{ident}@{release}"
        if identity in seen:
            raise ValueError(f"duplicate catalog entry: {identity}")
        seen.add(identity)
        reasons, unknown = [], set()
        for key in _string_list(entry["requires_true"], "requires_true"):
            if key not in facts:
                unknown.add(key)
            elif type(facts[key]) is not bool:
                raise ValueError(f"{key} must be boolean")
            elif not facts[key]:
                reasons.append(f"model condition false: {key}")

        for condition in entry["thresholds"]:
            parent, daughter, n = (condition[k] for k in ("parent", "daughter", "multiplicity"))
            if type(n) is not int or n < 1:
                raise ValueError("threshold multiplicity must be a positive integer")
            mp, md = _mass(facts, parent), _mass(facts, daughter)
            unknown.update(key for key in (parent, daughter) if key not in facts)
            if mp is not None and md is not None and mp <= n * md:
                reasons.append(f"on-shell phase space closed: {parent} <= {n} * {daughter}")

        record = evidence.get(identity, {})
        if not isinstance(record, dict):
            raise ValueError(f"invalid evidence object for {identity}")
        missing = []
        for key in _string_list(entry["requires_evidence"], "requires_evidence"):
            if key not in record:
                missing.append(key)
            elif not isinstance(record[key], str) or not re.fullmatch("[0-9a-f]{64}", record[key]):
                raise ValueError(f"{identity}: invalid SHA-256 reference for {key}")
        status = (
            "not_applicable" if reasons else
            "needs_model_facts" if unknown else
            "blocked_missing_evidence" if missing else
            "ready_for_review"
        )
        reports.append(dict(analysis_id=ident, release=release, family=entry["family"],
                            sources=_string_list(entry["sources"], "sources"),
                            route=entry["route"], status=status, reasons=reasons,
                            missing_model_facts=sorted(unknown),
                            missing_evidence=missing if not reasons else [],
                            limit_status="not_run"))
    return dict(catalog_version=version, catalog_scope="listed_releases_only",
                combination_status="not_attempted", analyses=reports)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("catalog", type=Path)
    p.add_argument("model_facts", type=Path)
    a = p.parse_args()
    try:
        result = route(_read(a.catalog), _read(a.model_facts))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
