import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.phase4_audit import compare_sample
from scripts.revised_experiment import EXECUTION_FIELDS, RESULT_FIELDS
from tests.test_phase4_gate import make_valid_run, write_csv


class SampleDeterminismTests(unittest.TestCase):
    def make_sample(self, root: Path):
        executions, results = make_valid_run(root, run_kind="diagnostic")
        scenarios = {
            "scenario_1", "scenario_5", "scenario_6", "scenario_10",
            "scenario_11", "scenario_17", "scenario_23", "scenario_30",
            "scenario_38",
        }
        executions = [row for row in executions if row["scenario_id"] in scenarios]
        results = [row for row in results if row["scenario_id"] in scenarios]
        write_csv(root / "executions.csv", EXECUTION_FIELDS, executions)
        write_csv(root / "scenario_tool_results.csv", RESULT_FIELDS, results)
        metadata = json.loads(
            (root / "run_metadata.json").read_text(encoding="utf-8")
        )
        metadata["scenarios"] = [
            "scenario_1", "scenario_5", "scenario_6", "scenario_10",
            "scenario_11", "scenario_17", "scenario_23", "scenario_30",
            "scenario_38",
        ]
        (root / "run_metadata.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )
        return executions, results

    def test_matching_diagnostic_subset_passes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            primary = root / "primary"
            repeat = root / "repeat"
            primary.mkdir()
            repeat.mkdir()
            make_valid_run(primary)
            self.make_sample(repeat)

            self.assertEqual(
                0, compare_sample(primary, repeat, root / "comparison.csv")
            )

    def test_normalized_output_change_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            primary = root / "primary"
            repeat = root / "repeat"
            primary.mkdir()
            repeat.mkdir()
            make_valid_run(primary)
            executions, _ = self.make_sample(repeat)
            executions[0]["normalized_output_checksum"] = "b" * 64
            write_csv(repeat / "executions.csv", EXECUTION_FIELDS, executions)

            output = root / "comparison.csv"
            self.assertEqual(1, compare_sample(primary, repeat, output))
            with output.open(encoding="utf-8", newline="") as source:
                rows = list(csv.DictReader(source))
            self.assertIn(
                "execution.normalized_output_checksum", rows[0]["different_fields"]
            )


if __name__ == "__main__":
    unittest.main()
