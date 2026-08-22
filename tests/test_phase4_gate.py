import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.core.analysis_units import DEFAULT_SCENARIO_IDS, DEFAULT_TOOLS
from scripts.workflows.phase4_gate import HIGH_RISK_KEYS, phase4_issues
from scripts.workflows.revised_experiment import EXECUTION_FIELDS, RESULT_FIELDS


SHA = "a" * 64


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_valid_run(root: Path, run_kind: str = "canonical_release"):
    executions = []
    results = []
    for tool in DEFAULT_TOOLS:
        for scenario in DEFAULT_SCENARIO_IDS:
            execution = {field: "" for field in EXECUTION_FIELDS}
            execution.update(
                tool_name=tool,
                scenario_id=scenario,
                execution_status="completed_clean",
                status_detail="readable output",
                tool_artifact_sha256=SHA,
                oracle_checksum=SHA,
                normalized_output_checksum=SHA,
                input_checksums_json=json.dumps(
                    {"base": SHA, "left": SHA, "right": SHA}
                ),
            )
            executions.append(execution)
            result = {field: "" for field in RESULT_FIELDS}
            result.update(
                tool_name=tool,
                scenario_id=scenario,
                mapping="one-to-one",
                change_type="structural",
                execution_status="completed_clean",
                status_detail="readable output",
                expected_file_count="1",
                actual_file_count="1",
                missing_files="",
                extra_files="",
                expected_line_count="1",
                actual_line_count="1",
                true_positives="1",
                false_positives="0",
                false_negatives="0",
                precision="1.0",
                recall="1.0",
                f1_score="1.0",
                sequence_agreement="1.0",
                exact_oracle_match="True",
                syntactic_valid="True",
                complete_textual_resolution="True",
            )
            results.append(result)
    write_csv(root / "executions.csv", EXECUTION_FIELDS, executions)
    write_csv(root / "scenario_tool_results.csv", RESULT_FIELDS, results)
    (root / "run_metadata.json").write_text(
        json.dumps(
            {
                "run_kind": run_kind,
                "tools": list(DEFAULT_TOOLS),
                "scenarios": list(DEFAULT_SCENARIO_IDS),
            }
        ),
        encoding="utf-8",
    )
    return executions, results


class Phase4GateTests(unittest.TestCase):
    def test_complete_canonical_matrix_passes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            make_valid_run(root)
            self.assertEqual((), phase4_issues(root))

    def test_duplicate_and_missing_key_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executions, _ = make_valid_run(root)
            executions[-1] = executions[0].copy()
            write_csv(root / "executions.csv", EXECUTION_FIELDS, executions)
            issues = phase4_issues(root)
            self.assertTrue(any("duplicate keys" in issue for issue in issues))
            self.assertTrue(any("missing 1 expected keys" in issue for issue in issues))

    def test_inconsistent_denominator_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _, results = make_valid_run(root)
            results[0]["expected_line_count"] = "2"
            write_csv(root / "scenario_tool_results.csv", RESULT_FIELDS, results)
            self.assertTrue(
                any("expected_line_count != TP + FN" in issue for issue in phase4_issues(root))
            )

    def test_diagnostic_run_requires_explicit_allowance(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            make_valid_run(root, run_kind="diagnostic")
            self.assertIn(
                "run is diagnostic, not a canonical release", phase4_issues(root)
            )
            self.assertEqual((), phase4_issues(root, require_release=False))

    def test_undefined_precision_and_f1_are_valid_for_empty_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _, results = make_valid_run(root)
            results[0].update(
                actual_line_count="0",
                true_positives="0",
                false_positives="0",
                false_negatives="1",
                precision="",
                recall="0.0",
                f1_score="",
                sequence_agreement="0.0",
                exact_oracle_match="False",
                complete_textual_resolution="False",
            )
            write_csv(root / "scenario_tool_results.csv", RESULT_FIELDS, results)
            self.assertEqual((), phase4_issues(root))

    def test_explicitly_invalidated_run_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            make_valid_run(root)
            (root / "run_invalidation.json").write_text("{}", encoding="utf-8")
            self.assertIn(
                "run has been explicitly invalidated; see run_invalidation.json",
                phase4_issues(root),
            )

    def test_final_gate_requires_audit_and_determinism_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            make_valid_run(root)
            issues = phase4_issues(root, require_final_audit=True)
            self.assertTrue(any("manual_audit.csv" in issue for issue in issues))

    def test_completed_final_audit_passes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            make_valid_run(root)
            audit_rows = [
                {
                    "tool_name": tool,
                    "scenario_id": scenario,
                    "audit_decision": "evidence_consistent",
                    "auditor_id": "test_auditor",
                    "audit_notes": "retained evidence checked",
                    "audited_at_utc": "2026-08-12T00:00:00Z",
                }
                for tool in DEFAULT_TOOLS
                for scenario in DEFAULT_SCENARIO_IDS
            ]
            audit_path = root / "manual_audit.csv"
            write_csv(audit_path, list(audit_rows[0]), audit_rows)
            audit_path.write_text(
                audit_path.read_text(encoding="utf-8"), encoding="utf-8-sig"
            )
            determinism_rows = [
                {
                    "tool_name": tool,
                    "scenario_id": scenario,
                    "deterministic": "True",
                    "different_fields": "",
                }
                for tool, scenario in sorted(HIGH_RISK_KEYS)
            ]
            write_csv(
                root / "determinism_high_risk.csv",
                list(determinism_rows[0]),
                determinism_rows,
            )
            self.assertEqual(
                (), phase4_issues(root, require_final_audit=True)
            )


if __name__ == "__main__":
    unittest.main()
