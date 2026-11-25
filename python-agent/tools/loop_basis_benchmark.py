"""Time to first exact PASS using trusted executables emitting JSONL proposals."""
from __future__ import annotations

import argparse
import json
import math
import queue
import random
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import loop_basis_verify as gate


def measure(label, command, frozen, seconds, archive):
    sha = gate.digest(frozen)
    archive.mkdir()
    common = archive / "source.json"
    common.write_bytes(frozen)
    # The producer receives a copy, not the source used by the checker.
    with tempfile.TemporaryDirectory(prefix="pheno-basis-verifier-") as tmp:
        pinned = Path(tmp) / "source.json"
        pinned.write_bytes(frozen)
        channel = queue.Queue(maxsize=1)
        started = time.perf_counter()
        deadline = started + seconds
        trials = []
        status = "NO_ACCEPTED_CANDIDATE"
        elapsed = None
        with (archive / "producer.stderr").open("wb") as log:
            try:
                proc = subprocess.Popen(
                    [*command, str(common.resolve())], stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=log,
                )
            except OSError as exc:
                return dict(arm=label, status="PRODUCER_ERROR", error=str(exc), trials=trials,
                            input_sha256=sha, time_to_first_pass_s=None)
            stop = threading.Event()

            def stream():
                while not stop.is_set():
                    line = proc.stdout.readline(gate.MAX_BYTES+2)
                    while not stop.is_set():
                        try:
                            channel.put(line, timeout=0.05)
                            break
                        except queue.Full:
                            pass
                    if not line or len(line) > gate.MAX_BYTES+1:
                        return
            reader = threading.Thread(target=stream, daemon=True)
            reader.start()
            try:
                while True:
                    remaining = deadline-time.perf_counter()
                    if remaining <= 0:
                        status = "TIMEOUT"
                        break
                    try:
                        raw = channel.get(timeout=remaining)
                    except queue.Empty:
                        status = "TIMEOUT"
                        break
                    if not raw:
                        try:
                            if proc.wait(timeout=max(0, deadline-time.perf_counter())):
                                status = "PRODUCER_ERROR"
                        except subprocess.TimeoutExpired:
                            status = "TIMEOUT"
                        break
                    if len(raw) > gate.MAX_BYTES+1:
                        status = "INVALID_STREAM"
                        break
                    out = archive / f"candidate-{len(trials)+1:04d}.json"
                    out.write_bytes(raw)
                    remaining = deadline-time.perf_counter()
                    if remaining <= 0:
                        status = "TIMEOUT"
                        break
                    try:
                        run = subprocess.run(
                            [sys.executable, str(Path(gate.__file__).resolve()), str(pinned),
                             str(out.resolve())], capture_output=True, timeout=remaining, check=False,
                        )
                    except subprocess.TimeoutExpired:
                        status = "TIMEOUT"
                        break
                    try:
                        report = json.loads(run.stdout)
                    except (UnicodeDecodeError, ValueError):
                        (archive/"verifier.stderr").write_bytes(run.stderr)
                        status = "VERIFIER_ERROR"
                        break
                    report["elapsed_s"] = time.perf_counter()-started
                    trials.append(report)
                    out.with_suffix(".receipt.json").write_text(json.dumps(report, sort_keys=True)+"\n")
                    if report["elapsed_s"] > seconds:
                        status = "TIMEOUT"
                        break
                    if (run.returncode == 0 and report.get("status") == "PASS"
                            and report.get("source_sha256") == sha
                            and report.get("proposal_sha256") == gate.digest(raw)):
                        status, elapsed = "PASS", report["elapsed_s"]
                        break
                    if run.returncode != 1 or report.get("status") != "REJECT":
                        status = "VERIFIER_ERROR"
                        break
            finally:
                stop.set()
                if proc.poll() is None:
                    proc.kill()
                proc.wait()
                reader.join(timeout=0.1)
                if not reader.is_alive():
                    proc.stdout.close()
        if not common.is_file() or gate.read(common) != frozen:
            status, elapsed = "SOURCE_MUTATED", None
    return dict(arm=label, status=status, input_sha256=sha,
                time_to_first_pass_s=elapsed, trials=trials)


def command(raw):
    value = json.loads(raw)
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise argparse.ArgumentTypeError("expected JSON array of operator-trusted argv strings")
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source")
    p.add_argument("archive", type=Path)
    p.add_argument("--fixed", required=True, type=command)
    p.add_argument("--agent", required=True, type=command)
    p.add_argument("--budget-s", required=True, type=float)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--expected-source-sha256", required=True)
    args = p.parse_args()
    if not math.isfinite(args.budget_s) or args.budget_s <= 0:
        p.error("budget must be finite and positive")
    frozen = gate.read(args.source)
    if gate.digest(frozen) != args.expected_source_sha256:
        p.error("frozen source hash mismatch")
    gate.prepare(gate.loads(frozen))  # preflight, outside both measurement windows
    args.archive.mkdir(parents=True)
    arms = [("fixed", args.fixed), ("agent", args.agent)]
    random.Random(args.seed).shuffle(arms)
    results = [measure(k, cmd, frozen, args.budget_s, args.archive/k) for k, cmd in arms]
    both = all(x["status"] == "PASS" for x in results)
    by_arm = {x["arm"]: x for x in results}
    report = dict(
        source_sha256=gate.digest(frozen),
        verifier_sha256=gate.digest(Path(gate.__file__).read_bytes()),
        runner_sha256=gate.digest(Path(__file__).read_bytes()),
        sympy_version=gate.sp.__version__, python_version=sys.version,
        budget_s=args.budget_s, seed=args.seed, execution_order=[x[0] for x in arms],
        results=results, agent_minus_fixed_s=(
            by_arm["agent"]["time_to_first_pass_s"] - by_arm["fixed"]["time_to_first_pass_s"]
        ) if both else None,
    )
    (args.archive/"comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    return 0 if both else 1


if __name__ == "__main__":
    raise SystemExit(main())
