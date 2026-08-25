import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("route_task.py")


def run_cli(*args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


class RouteTaskTests(unittest.TestCase):
    def test_high_risk_security_routes_to_sol(self) -> None:
        result = run_cli("--task", "review authentication vulnerability", "--risk", "high")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "sol")

    def test_low_risk_cli_flags_route_to_luna(self) -> None:
        result = run_cli("--task", "format a README", "--kind", "formatting", "--complexity", "low", "--risk", "low")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "luna")

    def test_json_stdin_routes_non_sensitive_research_to_chat(self) -> None:
        result = run_cli(stdin=json.dumps({"task": "compare two approaches", "kind": "research"}))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "chatgpt")

    def test_sensitive_research_stays_in_codex_policy(self) -> None:
        result = run_cli("--json", '{"task":"summarize private notes","kind":"research","sensitive":true}')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "terra")

    def test_sensitive_simple_work_does_not_use_lightweight_route(self) -> None:
        result = run_cli("--task", "format private report", "--kind", "formatting", "--complexity", "low", "--risk", "low", "--sensitive")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "terra")

    def test_output_is_compact_and_has_no_telemetry_claims(self) -> None:
        result = run_cli("--task", "write a short document", "--kind", "docs", "--complexity", "low", "--risk", "low")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("token", result.stdout.lower())
        self.assertNotIn("weekly", result.stdout.lower())
        self.assertNotIn('\n\n', result.stdout)
        self.assertNotIn('": ', result.stdout)

    def test_invalid_input_is_compact_json_error(self) -> None:
        result = run_cli("--json", "[]")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr), {"error": "JSON input must be an object"})


if __name__ == "__main__":
    unittest.main()


class BoundaryTests(unittest.TestCase):
    def test_empty_task_rejected(self) -> None:
        result = run_cli("--json", '{"task": ""}')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "task must be a non-empty string")

    def test_whitespace_task_rejected(self) -> None:
        result = run_cli("--task", "   ")
        self.assertEqual(result.returncode, 2)

    def test_non_string_task_rejected(self) -> None:
        result = run_cli("--json", '{"task": 42}')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "task must be a non-empty string")

    def test_unicode_task_routes_normally(self) -> None:
        result = run_cli("--task", "résumer le document — 总结文件", "--kind", "research")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "chatgpt")

    def test_long_formatting_task_not_low_complexity(self) -> None:
        result = run_cli("--task", "format " + "x" * 120, "--kind", "formatting")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["route"], "terra")

    def test_json_and_flags_are_mutually_exclusive(self) -> None:
        result = run_cli("--json", '{"task": "x"}', "--task", "y")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "use --json or task flags, not both")

    def test_invalid_kind_rejected(self) -> None:
        result = run_cli("--task", "x", "--kind", "quantum")
        self.assertEqual(result.returncode, 2)

    def test_invalid_complexity_rejected(self) -> None:
        result = run_cli("--task", "x", "--complexity", "extreme")
        self.assertEqual(result.returncode, 2)

    def test_non_bool_sensitive_rejected(self) -> None:
        result = run_cli("--json", '{"task": "x", "sensitive": "yes"}')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "sensitive must be a boolean")

    def test_auth_keyword_infers_security(self) -> None:
        result = run_cli("--task", "fix authentication bug")
        self.assertEqual(json.loads(result.stdout)["route"], "sol")

    def test_consequential_overrides_everything(self) -> None:
        result = run_cli("--task", "format a README", "--kind", "formatting",
                         "--complexity", "low", "--risk", "low", "--consequential")
        self.assertEqual(json.loads(result.stdout)["route"], "sol")

    def test_network_research_stays_internal(self) -> None:
        result = run_cli("--task", "compare APIs live", "--kind", "research", "--requires-network")
        self.assertEqual(json.loads(result.stdout)["route"], "terra")

    def test_malformed_json_reports_position(self) -> None:
        result = run_cli("--json", '{"task": ')
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(result.stderr)["error"].startswith("invalid JSON:"))
