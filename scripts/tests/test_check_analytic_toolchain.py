import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from scripts import check_analytic_toolchain as tool


def response(component, ok=True, version="fixture-kernel"):
    return (
        tool.BEGIN + json.dumps({
            "component": component, "ok": ok, "kernel_version": version,
        }) + tool.END
    )


class AnalyticToolchainTests(unittest.TestCase):
    @patch.object(tool.subprocess, "run")
    @patch.object(tool.shutil, "which", return_value="/private/bin/wolframscript")
    def test_path_discovery_never_executes_or_claims_native(self, which, run):
        report, code = tool.inspect("feynarts-feyncalc", "local")
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "UNVERIFIED")
        self.assertEqual(report["launcher"], "ON_PATH")
        self.assertEqual(report["feynarts_feyncalc_interface"], "NOT_RUN")
        self.assertNotIn("/private/", json.dumps(report))
        self.assertTrue(all(x["status"] == "NOT_RUN" for x in report["native_checks"].values()))
        which.assert_called_once_with("wolframscript")
        run.assert_not_called()

    @patch.object(tool.subprocess, "run")
    @patch.object(tool.shutil, "which", return_value=None)
    def test_missing_local_cli_is_reported_and_no_run_attempted(self, which, run):
        report, code = tool.inspect("feyncalc", "local", True)
        self.assertEqual((code, report["status"], report["reason"]),
                         (2, "BLOCKED", "WOLFRAMSCRIPT_NOT_ON_PATH"))
        run.assert_not_called()

    @patch.object(tool.subprocess, "run")
    @patch.object(tool.shutil, "which")
    def test_magnus_never_falls_back_to_local_tool(self, which, run):
        report, code = tool.inspect("feynarts", "magnus", True)
        self.assertEqual((code, report["launcher"], report["reason"]),
                         (2, "NOT_CHECKED", "ANALYTIC_MAGNUS_ADAPTER_NOT_IMPLEMENTED"))
        which.assert_not_called()
        run.assert_not_called()

    @patch.object(tool.subprocess, "run")
    @patch.object(tool.shutil, "which", return_value="/approved/wolframscript")
    def test_opt_in_known_good_reports_separate_package_smokes(self, which, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, response(component), "ignored")
            for component in ("Wolfram", "FeynArts", "FeynCalc")
        ]
        report, code = tool.inspect("feynarts-feyncalc", "local", True)
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "COMPONENTS_SMOKE_PASSED")
        self.assertEqual(report["scientific_validation"], "NOT_RUN")
        self.assertEqual(report["feynarts_feyncalc_interface"], "NOT_RUN")
        self.assertEqual(list(report["native_checks"]), ["Wolfram", "FeynArts", "FeynCalc"])
        for call, component in zip(run.call_args_list, report["native_checks"]):
            self.assertEqual(call.args[0][:3], ["/approved/wolframscript", "-local", "-code"])
            self.assertEqual(call.args[0][3], tool.probe_code(component))
            self.assertIs(call.kwargs["shell"], False)
            self.assertEqual(call.kwargs["timeout"], tool.TIMEOUT_SECONDS)
            self.assertEqual(call.kwargs["stdin"], subprocess.DEVNULL)

    @patch.object(tool.subprocess, "run")
    @patch.object(tool.shutil, "which", return_value="wolframscript")
    def test_blocked_package_does_not_promote_next_package(self, which, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, response("Wolfram"), ""),
            subprocess.CompletedProcess([], 0, response("FeynArts", False), ""),
        ]
        report, code = tool.inspect("feynarts-feyncalc", "local", True)
        self.assertEqual((code, report["reason"]), (2, "COMPONENT_SMOKE_FAILED"))
        self.assertEqual(report["native_checks"]["FeynCalc"]["status"], "NOT_RUN")
        self.assertEqual(run.call_count, 2)

    @patch.object(tool.subprocess, "run")
    def test_invalid_or_nonzero_native_receipt_can_never_pass(self, run):
        cases = [
            (1, response("Wolfram"), "NATIVE_EXIT_NONZERO"),
            (0, "nothing", "NATIVE_REPORT_MISSING_OR_AMBIGUOUS"),
            (0, response("Wolfram") * 2, "NATIVE_REPORT_MISSING_OR_AMBIGUOUS"),
            (0, response("FeynCalc"), "NATIVE_REPORT_INVALID"),
            (0, response("Wolfram", ok="yes"), "NATIVE_REPORT_INVALID"),
            (0, response("Wolfram", version=""), "NATIVE_REPORT_INVALID"),
            (0, tool.BEGIN + "not valid JSON" + tool.END, "NATIVE_REPORT_INVALID"),
        ]
        for returncode, stdout, reason in cases:
            with self.subTest(reason=reason, stdout=stdout):
                run.return_value = subprocess.CompletedProcess([], returncode, stdout, "private")
                self.assertEqual(tool.native_probe("wolframscript", "Wolfram"),
                                 {"status": "BLOCKED", "reason": reason})

    @patch.object(tool.subprocess, "run")
    def test_timeout_and_launch_errors_are_explicit_not_success(self, run):
        for error, reason in [(subprocess.TimeoutExpired([], 1), "TIMEOUT"),
                              (OSError("private path"), "LAUNCH_FAILED")]:
            with self.subTest(reason=reason):
                run.side_effect = error
                self.assertEqual(tool.native_probe("wolframscript", "Wolfram"),
                                 {"status": "BLOCKED", "reason": reason})

    @patch.object(tool.shutil, "which", return_value="wolframscript")
    def test_cli_serializes_discovery_machine_readably(self, which):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(tool.main(["--profile", "wolfram", "--backend", "local"]), 0)
        self.assertEqual(json.loads(buf.getvalue())["mode"], "DISCOVERY_ONLY")


if __name__ == "__main__":
    unittest.main()
