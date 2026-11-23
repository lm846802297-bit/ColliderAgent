#!/usr/bin/env python3
"""Distinguish Wolfram tool discovery from native analytic capability evidence."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess

PROFILES = {
    "wolfram": (),
    "feyncalc": ("FeynCalc",),
    "feynarts": ("FeynArts",),
    "feynarts-feyncalc": ("FeynArts", "FeynCalc"),
}
PACKAGE_PROBES = {
    "FeynCalc": 'Needs["FeynCalc`"]; NameQ["FeynCalc`DiracSimplify"]',
    "FeynArts": 'Needs["FeynArts`"]; NameQ["FeynArts`CreateTopologies"]',
}
BEGIN = "__COLLIDERAGENT_ANALYTIC_SMOKE_BEGIN__"
END = "__COLLIDERAGENT_ANALYTIC_SMOKE_END__"
TIMEOUT_SECONDS = 45


def probe_code(component: str) -> str:
    # Only these audited expressions are ever passed to the kernel.
    check = "IntegerQ[2+2] && 2+2 === 4" if component == "Wolfram" else PACKAGE_PROBES[component]
    return (
        'Module[{ok}, ok = TrueQ[Quiet[Check[(' + check + '), False]]]; '
        f'Print["{BEGIN}" <> ExportString[<|"component" -> "{component}", '
        '"kernel_version" -> $Version, "ok" -> ok|>, "RawJSON"] '
        f'<> "{END}"]; Quit[0]]'
    )


def native_probe(executable: str, component: str) -> dict:
    try:
        result = subprocess.run(
            [executable, "-local", "-code", probe_code(component)],
            shell=False, stdin=subprocess.DEVNULL, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"status": "BLOCKED", "reason": "TIMEOUT"}
    except OSError:
        return {"status": "BLOCKED", "reason": "LAUNCH_FAILED"}
    if result.returncode != 0:
        # Do not echo arbitrary startup messages, paths, or licensing output.
        return {"status": "BLOCKED", "reason": "NATIVE_EXIT_NONZERO"}
    stdout = result.stdout
    if stdout.count(BEGIN) != 1 or stdout.count(END) != 1:
        return {"status": "BLOCKED", "reason": "NATIVE_REPORT_MISSING_OR_AMBIGUOUS"}
    payload, delimiter, _ = stdout.split(BEGIN, 1)[1].partition(END)
    try:
        record = json.loads(payload) if delimiter else None
    except json.JSONDecodeError:
        record = None
    if (
        not isinstance(record, dict)
        or record.get("component") != component
        or not isinstance(record.get("ok"), bool)
        or not isinstance(record.get("kernel_version"), str)
        or not record["kernel_version"].strip()
    ):
        return {"status": "BLOCKED", "reason": "NATIVE_REPORT_INVALID"}
    if not record["ok"]:
        return {"status": "BLOCKED", "reason": "COMPONENT_SMOKE_FAILED"}
    return {"status": "PASS", "kernel_version": record["kernel_version"]}


def inspect(profile: str, backend: str, run_native: bool = False) -> tuple[dict, int]:
    checks = {name: {"status": "NOT_RUN"} for name in ("Wolfram", *PROFILES[profile])}
    report = {
        "schema": "collideragent-analytic-toolchain-v1",
        "mode": "NATIVE_SMOKE" if run_native else "DISCOVERY_ONLY",
        "backend": backend,
        "profile": profile,
        "launcher": "NOT_CHECKED",
        "native_checks": checks,
        "feynarts_feyncalc_interface": "NOT_RUN" if len(PROFILES[profile]) == 2 else "N/A",
        "scientific_validation": "NOT_RUN",
        "status": "UNVERIFIED",
    }
    if backend == "magnus":
        report.update(status="BLOCKED", reason="ANALYTIC_MAGNUS_ADAPTER_NOT_IMPLEMENTED")
        return report, 2
    executable = shutil.which("wolframscript")
    if executable is None:
        report.update(launcher="NOT_ON_PATH", status="BLOCKED", reason="WOLFRAMSCRIPT_NOT_ON_PATH")
        return report, 2
    report["launcher"] = "ON_PATH"
    if not run_native:
        return report, 0

    # Each component gets a fresh sequential kernel. This avoids conflating
    # independent package availability with the FeynArts conversion interface.
    for component in checks:
        checks[component] = native_probe(executable, component)
        if checks[component]["status"] != "PASS":
            report.update(status="BLOCKED", reason=checks[component]["reason"])
            return report, 2
    report["status"] = "COMPONENTS_SMOKE_PASSED"
    return report, 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=tuple(PROFILES))
    parser.add_argument("--backend", required=True, choices=("local", "magnus"))
    parser.add_argument("--native", action="store_true",
                        help="Explicitly run fixed smoke checks on the already authorized local kernel.")
    args = parser.parse_args(argv)
    report, code = inspect(args.profile, args.backend, args.native)
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
