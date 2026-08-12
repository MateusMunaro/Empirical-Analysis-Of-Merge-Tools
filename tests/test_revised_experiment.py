import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.analysis_units import ObservationStatus
from scripts.revised_experiment import (
    DEFAULT_LOCK,
    ProcessOutcome,
    ToolRuntime,
    classify_terminal_status,
    load_runtimes,
    normalize_java_output,
    run_attempt,
    run_process,
    sha256_file,
)
from scripts.scenario_metadata import load_manifest


class TerminalStatusTests(unittest.TestCase):
    def test_timeout_has_precedence_over_partial_output(self):
        status, _ = classify_terminal_status(
            process=ProcessOutcome(None, True, None, 1.0),
            output_valid=True,
            has_conflicts=True,
        )
        self.assertEqual(ObservationStatus.TIMEOUT, status)

    def test_setup_error_is_not_silently_converted_to_zero_score(self):
        status, detail = classify_terminal_status(
            process=ProcessOutcome(None, False, "missing jar", 0.0),
            output_valid=False,
            has_conflicts=False,
        )
        self.assertEqual(ObservationStatus.SETUP_ERROR, status)
        self.assertEqual("missing jar", detail)

    def test_crash_has_precedence_over_leftover_output(self):
        status, _ = classify_terminal_status(
            process=ProcessOutcome(2, False, None, 0.1),
            output_valid=True,
            has_conflicts=False,
        )
        self.assertEqual(ObservationStatus.CRASH, status)

    def test_valid_conflicted_output_is_explicit(self):
        status, _ = classify_terminal_status(
            process=ProcessOutcome(0, False, None, 0.1),
            output_valid=True,
            has_conflicts=True,
        )
        self.assertEqual(ObservationStatus.COMPLETED_CONFLICTED, status)

    def test_subprocess_timeout_is_captured(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            outcome = run_process(
                [sys.executable, "-c", "import time; time.sleep(2)"],
                root,
                1,
                root / "stdout.log",
                root / "stderr.log",
            )
            self.assertTrue(outcome.timed_out)
            self.assertIsNone(outcome.exit_code)


class OutputNormalizationTests(unittest.TestCase):
    def test_empty_output_is_invalid(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            raw = root / "raw"
            raw.mkdir()
            valid, detail = normalize_java_output(raw, root / "normalized")
            self.assertFalse(valid)
            self.assertIn("no Java", detail)

    def test_duplicate_basenames_are_rejected_instead_of_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            raw = root / "raw"
            (raw / "a").mkdir(parents=True)
            (raw / "b").mkdir()
            (raw / "a" / "Same.java").write_text("class Same {}", encoding="utf-8")
            (raw / "b" / "Same.java").write_text("class Same {}", encoding="utf-8")
            valid, detail = normalize_java_output(raw, root / "normalized")
            self.assertFalse(valid)
            self.assertIn("ambiguous", detail)

    def test_generated_prefix_is_removed_for_flat_declared_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            raw = root / "raw" / "tool" / "generated" / "prefix"
            raw.mkdir(parents=True)
            (raw / "A.java").write_text("class A {}", encoding="utf-8")
            normalized = root / "normalized"
            valid, _ = normalize_java_output(root / "raw", normalized)
            self.assertTrue(valid)
            self.assertTrue((normalized / "A.java").is_file())


class AttemptIntegrationTests(unittest.TestCase):
    def test_clean_exact_output_produces_metrics_and_logs(self):
        manifest = {scenario.scenario_id: scenario for scenario in load_manifest()}
        oracle = (
            Path(__file__).resolve().parent.parent
            / "output" / "IntelliMerge" / "expected" / "scenario_1"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            run_dir = Path(temporary_directory) / "run"
            run_dir.mkdir()

            def command_builder(scenario_id, attempt, raw, lock):
                source = oracle / "Client.java"
                program = (
                    "from pathlib import Path; "
                    f"p=Path({str(raw)!r}); p.mkdir(exist_ok=True); "
                    f"(p/'Client.java').write_bytes(Path({str(source)!r}).read_bytes())"
                )
                return [sys.executable, "-c", program], run_dir, raw

            executable = Path(sys.executable)
            runtime = ToolRuntime(
                "IntelliMerge", "test", executable, executable,
                sha256_file(executable), "raw_sha256", executable,
                executable.parent,
                command_builder,
            )
            environment = {
                "java_version": "test-java",
                "python_version": "test-python",
                "operating_system": "test-os",
                "architecture": "test-arch",
            }
            execution, result, observation = run_attempt(
                runtime, "scenario_1", run_dir, 10, manifest, environment
            )

            self.assertEqual(
                ObservationStatus.COMPLETED_CLEAN,
                observation.status,
                (run_dir / execution["stderr_path"]).read_text(
                    encoding="utf-8", errors="replace"
                ),
            )
            self.assertEqual("completed_clean", execution["execution_status"])
            self.assertTrue(result["exact_oracle_match"])
            self.assertEqual(1.0, result["f1_score"])
            self.assertTrue((run_dir / execution["stdout_path"]).is_file())
            self.assertEqual(
                json.loads(execution["command_json"])[0], sys.executable
            )


class FrozenCommandTests(unittest.TestCase):
    def test_jdime_directory_command_is_recursive_and_structured(self):
        _, runtimes = load_runtimes(DEFAULT_LOCK)
        runtime = runtimes["JDime"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            attempt = Path(temporary_directory)
            command, _, _ = runtime.command_builder(
                "scenario_1", attempt, attempt / "raw", {}
            )
        self.assertIn("--recursive", command)
        self.assertEqual("structured", command[command.index("--mode") + 1])


if __name__ == "__main__":
    unittest.main()
