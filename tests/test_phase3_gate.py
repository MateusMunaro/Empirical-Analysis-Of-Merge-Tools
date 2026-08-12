import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.phase3_gate import DEFAULT_LOCK, phase3_issues


class Phase3GateTests(unittest.TestCase):
    def test_repository_development_gate_passes(self):
        self.assertEqual((), phase3_issues())

    def test_fallback_policy_must_be_disabled(self):
        lock = json.loads(DEFAULT_LOCK.read_text(encoding="utf-8"))
        lock["execution_policy"]["jdime_fallback"] = "automatic"
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "tool_versions.lock"
            path.write_text(json.dumps(lock), encoding="utf-8")
            self.assertIn(
                "JDime fallback must remain disabled",
                phase3_issues(path),
            )

    def test_jdime_directory_merge_must_be_recursive(self):
        lock = json.loads(DEFAULT_LOCK.read_text(encoding="utf-8"))
        lock["execution_policy"]["jdime_recursive_directories"] = False
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "tool_versions.lock"
            path.write_text(json.dumps(lock), encoding="utf-8")
            self.assertIn(
                "JDime directory inputs must be merged recursively",
                phase3_issues(path),
            )

    def test_jdime_must_fail_instead_of_falling_back(self):
        lock = json.loads(DEFAULT_LOCK.read_text(encoding="utf-8"))
        lock["execution_policy"]["jdime_exit_on_error"] = False
        lock["tools"]["JDime"]["arguments"].remove("--exit-on-error")
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "tool_versions.lock"
            path.write_text(json.dumps(lock), encoding="utf-8")
            issues = phase3_issues(path)
            self.assertIn("JDime must exit on structured merge errors", issues)
            self.assertIn(
                "JDime locked arguments must disable automatic fallback", issues
            )

    def test_release_gate_exposes_incompatible_environment(self):
        with patch("scripts.phase3_gate.platform.system", return_value="Windows"):
            issues = phase3_issues(release=True)
        self.assertTrue(
            any("release execution requires Linux x86_64" in issue for issue in issues)
        )


if __name__ == "__main__":
    unittest.main()
