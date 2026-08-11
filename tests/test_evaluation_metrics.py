import tempfile
import unittest
from pathlib import Path

from scripts.analysis_units import ObservationStatus
from scripts.evaluation_metrics import (
    evaluate_trees,
    is_complete_resolution,
    load_text_tree,
    normalized_lines,
)


class NormalizationTests(unittest.TestCase):
    def test_only_line_endings_and_one_terminal_separator_are_normalized(self):
        self.assertEqual(
            ("  alpha  ", "", "beta"),
            normalized_lines("  alpha  \r\n\r\nbeta\r\n"),
        )

    def test_empty_text_has_no_lines(self):
        self.assertEqual((), normalized_lines(""))


class TreeMetricTests(unittest.TestCase):
    def test_worked_example_counts_duplicates_order_and_tree_differences(self):
        expected = {
            "src/A.java": ("alpha", "beta", "beta", "gamma"),
            "src/B.java": ("omega",),
        }
        actual = {
            "src/A.java": ("beta", "alpha", "beta", "delta"),
            "src/C.java": ("omega",),
        }

        metrics = evaluate_trees(expected, actual)

        self.assertEqual(3, metrics.true_positives)
        self.assertEqual(2, metrics.false_positives)
        self.assertEqual(2, metrics.false_negatives)
        self.assertAlmostEqual(0.6, metrics.precision)
        self.assertAlmostEqual(0.6, metrics.recall)
        self.assertAlmostEqual(0.6, metrics.f1_score)
        self.assertAlmostEqual(0.4, metrics.sequence_agreement)
        self.assertEqual(("src/B.java",), metrics.missing_files)
        self.assertEqual(("src/C.java",), metrics.extra_files)
        self.assertFalse(metrics.exact_oracle_match)

    def test_duplicate_line_multiplicity_affects_false_negatives(self):
        metrics = evaluate_trees(
            {"A.java": ("same", "same")},
            {"A.java": ("same",)},
        )

        self.assertEqual(1, metrics.true_positives)
        self.assertEqual(0, metrics.false_positives)
        self.assertEqual(1, metrics.false_negatives)
        self.assertAlmostEqual(2 / 3, metrics.f1_score)

    def test_order_change_affects_sequence_but_not_content_f1(self):
        metrics = evaluate_trees(
            {"A.java": ("first", "second")},
            {"A.java": ("second", "first")},
        )

        self.assertEqual(1.0, metrics.f1_score)
        self.assertEqual(0.5, metrics.sequence_agreement)
        self.assertFalse(metrics.exact_oracle_match)

    def test_same_line_in_an_extra_file_does_not_cancel_missing_file(self):
        metrics = evaluate_trees(
            {"expected/A.java": ("same",)},
            {"actual/A.java": ("same",)},
        )

        self.assertEqual(0, metrics.true_positives)
        self.assertEqual(1, metrics.false_positives)
        self.assertEqual(1, metrics.false_negatives)

    def test_empty_actual_tree_leaves_precision_and_f1_not_applicable(self):
        metrics = evaluate_trees({"A.java": ("expected",)}, {})

        self.assertIsNone(metrics.precision)
        self.assertEqual(0.0, metrics.recall)
        self.assertIsNone(metrics.f1_score)
        self.assertEqual(0.0, metrics.sequence_agreement)

    def test_identical_empty_trees_are_exact_but_have_undefined_content_rates(self):
        metrics = evaluate_trees({}, {})

        self.assertTrue(metrics.exact_oracle_match)
        self.assertIsNone(metrics.precision)
        self.assertIsNone(metrics.recall)
        self.assertIsNone(metrics.f1_score)
        self.assertEqual(1.0, metrics.sequence_agreement)

    def test_tree_loader_preserves_relative_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "src" / "example"
            source.mkdir(parents=True)
            (source / "A.java").write_text("one\ntwo\n", encoding="utf-8")

            self.assertEqual(
                {"src/example/A.java": ("one", "two")},
                load_text_tree(root),
            )


class CompleteResolutionTests(unittest.TestCase):
    def setUp(self):
        self.exact_metrics = evaluate_trees(
            {"A.java": ("class A {}",)},
            {"A.java": ("class A {}",)},
        )

    def test_minimum_complete_resolution_requires_clean_exact_and_syntax(self):
        self.assertTrue(
            is_complete_resolution(
                execution_status=ObservationStatus.COMPLETED_CLEAN,
                metrics=self.exact_metrics,
                syntactic_valid=True,
            )
        )

    def test_f1_one_with_invalid_syntax_is_not_complete(self):
        self.assertEqual(1.0, self.exact_metrics.f1_score)
        self.assertFalse(
            is_complete_resolution(
                execution_status=ObservationStatus.COMPLETED_CLEAN,
                metrics=self.exact_metrics,
                syntactic_valid=False,
            )
        )

    def test_conflicted_execution_is_not_complete(self):
        self.assertFalse(
            is_complete_resolution(
                execution_status=ObservationStatus.COMPLETED_CONFLICTED,
                metrics=self.exact_metrics,
                syntactic_valid=True,
            )
        )

    def test_behavioral_claim_requires_compilation_and_tests(self):
        common = {
            "execution_status": ObservationStatus.COMPLETED_CLEAN,
            "metrics": self.exact_metrics,
            "syntactic_valid": True,
            "require_behavioral_evidence": True,
        }
        self.assertFalse(is_complete_resolution(**common))
        self.assertFalse(
            is_complete_resolution(
                **common, compiles=True, scenario_tests_pass=False
            )
        )
        self.assertTrue(
            is_complete_resolution(
                **common, compiles=True, scenario_tests_pass=True
            )
        )


if __name__ == "__main__":
    unittest.main()
