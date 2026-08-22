import csv
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.core.analysis_units import DEFAULT_SCENARIO_IDS, DEFAULT_TOOLS
from scripts.workflows.phase5_analysis import (
    AnalysisError,
    build_diff_examples,
    build_tables,
    generate,
    validate_master,
)


FIELDS = (
    "tool_name",
    "scenario_id",
    "mapping",
    "change_type",
    "execution_status",
    "true_positives",
    "false_positives",
    "false_negatives",
    "precision",
    "recall",
    "f1_score",
    "sequence_agreement",
    "exact_oracle_match",
    "syntactic_valid",
    "complete_textual_resolution",
)


def _labels(scenario_id):
    number = int(scenario_id.rsplit("_", 1)[1])
    mapping_index = (number - 1) // 13
    position = (number - 1) % 13
    return ("1:1", "1:N", "N:N")[mapping_index], (
        "structural" if position < 10 else "behavioral"
    )


def make_rows():
    rows = []
    for tool in DEFAULT_TOOLS:
        for scenario in DEFAULT_SCENARIO_IDS:
            mapping, change_type = _labels(scenario)
            rows.append(
                {
                    "tool_name": tool,
                    "scenario_id": scenario,
                    "mapping": mapping,
                    "change_type": change_type,
                    "execution_status": "completed_clean",
                    "true_positives": "1",
                    "false_positives": "1",
                    "false_negatives": "0",
                    "precision": "0.5",
                    "recall": "1.0",
                    "f1_score": str(2 / 3),
                    "sequence_agreement": "0.5",
                    "exact_oracle_match": "False",
                    "syntactic_valid": "True",
                    "complete_textual_resolution": "False",
                }
            )
    return rows


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class Phase5AnalysisTests(unittest.TestCase):
    def test_builds_declared_tables_and_strata(self):
        tables = build_tables(make_rows())
        self.assertEqual(3, len(tables["tool_summary"]))
        self.assertEqual(18, len(tables["stratum_summary"]))
        self.assertEqual(9, len(tables["status_by_mapping"]))
        self.assertEqual(39, len(tables["master_outcome_matrix"]))
        self.assertEqual(117, len(tables["score_decomposition"]))
        self.assertEqual(1, len(tables["recurring_scores"]))
        self.assertEqual("0.67", tables["recurring_scores"][0]["f1_rounded_2"])

    def test_undefined_and_unavailable_scores_keep_explicit_denominators(self):
        rows = make_rows()
        fst_empty = next(
            row for row in rows
            if row["tool_name"] == "FSTMerge" and row["scenario_id"] == "scenario_1"
        )
        fst_empty.update(
            true_positives="0",
            false_positives="0",
            false_negatives="2",
            precision="",
            recall="0.0",
            f1_score="",
            sequence_agreement="0.0",
        )
        intelli_invalid = next(
            row for row in rows
            if row["tool_name"] == "IntelliMerge" and row["scenario_id"] == "scenario_1"
        )
        intelli_invalid.update(
            execution_status="invalid_output",
            true_positives="",
            false_positives="",
            false_negatives="",
            precision="",
            recall="",
            f1_score="",
            sequence_agreement="",
            syntactic_valid="",
        )
        summaries = {
            row["tool_name"]: row for row in build_tables(rows)["tool_summary"]
        }
        fst = summaries["FSTMerge"]
        self.assertEqual(39, fst["applicable_n"])
        self.assertEqual(38, fst["macro_precision_n"])
        self.assertEqual(39, fst["macro_recall_n"])
        self.assertEqual(38, fst["macro_f1_score_n"])
        self.assertTrue(math.isclose(0.5, fst["micro_precision"]))
        self.assertTrue(math.isclose(38 / 40, fst["micro_recall"]))
        intelli = summaries["IntelliMerge"]
        self.assertEqual(38, intelli["applicable_n"])
        self.assertTrue(
            math.isclose((38 * (2 / 3)) / 39, intelli["end_to_end_f1_zero_unavailable"])
        )

    def test_rejects_metric_inconsistent_with_counts(self):
        rows = make_rows()
        rows[0]["precision"] = "0.9"
        with self.assertRaisesRegex(AnalysisError, "precision is inconsistent"):
            validate_master(rows)

    def test_generation_writes_conceptual_tables_without_plot_dependency(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "master.csv"
            output = root / "analysis"
            write_rows(source, make_rows())
            with patch("scripts.phase5_analysis._save_figures"):
                summary = generate(source, output)
            self.assertEqual(117, summary["expected_observations"])
            self.assertTrue((output / "table_tool_summary.csv").is_file())
            self.assertTrue((output / "table_stratum_summary.csv").is_file())
            self.assertTrue((output / "table_master_outcome_matrix.csv").is_file())
            self.assertTrue((output / "table_score_decomposition.csv").is_file())
            self.assertTrue((output / "table_recurring_scores.csv").is_file())
            report = (output / "phase5_descriptive_analysis.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("scripts/", report)
            self.assertNotIn("evaluation_results/", report)

    def test_stable_figure_assets_can_be_exported_without_fixed_repository_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "master.csv"
            output = root / "analysis"
            assets = root / "movable_manuscript_assets"
            write_rows(source, make_rows())

            def fake_figures(_rows, _tables, destination):
                for name in (
                    "figure_method_flow.pdf",
                    "figure_outcome_heatmap.pdf",
                    "figure_execution_status.pdf",
                    "figure_f1_distribution.pdf",
                ):
                    (destination / name).write_bytes(b"pdf")

            with patch(
                "scripts.phase5_analysis._save_figures", side_effect=fake_figures
            ):
                generate(source, output, manuscript_assets=assets)
            self.assertEqual(b"pdf", (assets / "F0.pdf").read_bytes())
            self.assertEqual(b"pdf", (assets / "F1.pdf").read_bytes())
            self.assertEqual(b"pdf", (assets / "F2.pdf").read_bytes())
            self.assertEqual(b"pdf", (assets / "F3.pdf").read_bytes())

    def test_canonical_phase4_values_remain_frozen(self):
        root = Path(__file__).resolve().parents[1]
        master = (
            root
            / "evaluation_results"
            / "revised_experiment"
            / "canonical_run_3"
            / "scenario_tool_results.csv"
        )
        if not master.is_file():
            self.skipTest("canonical Phase 4 dataset is not present")
        with master.open(encoding="utf-8-sig", newline="") as source:
            rows = list(csv.DictReader(source))
        summaries = {
            row["tool_name"]: row for row in build_tables(rows)["tool_summary"]
        }
        self.assertTrue(
            math.isclose(
                0.46361121830998053,
                summaries["FSTMerge"]["macro_f1_score_mean"],
            )
        )
        self.assertTrue(
            math.isclose(
                0.711073323120824,
                summaries["IntelliMerge"]["macro_f1_score_mean"],
            )
        )
        self.assertIsNone(summaries["JDime"]["macro_f1_score_mean"])

    def test_canonical_diff_examples_use_only_logical_paths(self):
        root = Path(__file__).resolve().parents[1]
        run_root = (
            root / "evaluation_results" / "revised_experiment" / "canonical_run_3"
        )
        master = run_root / "scenario_tool_results.csv"
        oracle_root = root / "output"
        if not master.is_file():
            self.skipTest("canonical Phase 4 evidence is not present")
        with master.open(encoding="utf-8-sig", newline="") as source:
            rows = list(csv.DictReader(source))
        examples = build_diff_examples(rows, run_root, oracle_root)
        self.assertEqual(7, len(examples))
        by_key = {
            (row["tool_name"], row["scenario_id"]): row for row in examples
        }
        exact = by_key[("IntelliMerge", "scenario_6")]
        self.assertEqual("[]", exact["missing_line_examples_json"])
        self.assertEqual("[]", exact["extra_line_examples_json"])
        missing = by_key[("IntelliMerge", "scenario_23")]
        self.assertIn("EmailStrategy.java", missing["missing_line_examples_json"])
        for row in examples:
            self.assertNotIn(str(root), row["missing_line_examples_json"])
            self.assertNotIn(str(root), row["extra_line_examples_json"])


if __name__ == "__main__":
    unittest.main()
