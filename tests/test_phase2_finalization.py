import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.finalize_phase2 import (
    documented_open_issue_rows,
    write_confirmed_manifest_atomically,
)
from scripts.ingest_oracle_reviews import (
    validate_review_ingestion,
    write_reviews_atomically,
)
from scripts.oracle_validation import (
    EvidenceResult,
    OracleDecision,
    OracleReview,
    load_reviews,
)
from scripts.scenario_metadata import (
    ChangeType,
    ClassificationStatus,
    MappingComplexity,
    load_manifest,
)


def review(
    reviewer_id="reviewer_A",
    scenario_id="scenario_1",
    review_round=1,
):
    return OracleReview(
        scenario_id=scenario_id,
        reviewer_id=reviewer_id,
        review_round=review_round,
        oracle_decision=OracleDecision.ACCEPT,
        intent_preserved=True,
        complete_artifact_tree=True,
        no_unjustified_content=True,
        syntactically_valid=True,
        compilation_result=EvidenceResult.NOT_RUN,
        tests_result=EvidenceResult.NOT_APPLICABLE,
        assigned_mapping=MappingComplexity.ONE_TO_ONE,
        assigned_change_type=ChangeType.STRUCTURAL,
        comments="",
        reviewed_at_utc="2026-08-10T23:00:00Z",
    )


class ReviewIngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_first_round_is_accepted_without_mutating_inputs(self):
        incoming = (review(),)
        combined = validate_review_ingestion((), incoming, self.manifest)

        self.assertEqual(incoming, combined)

    def test_existing_round_cannot_be_overwritten(self):
        existing = (review(),)
        with self.assertRaisesRegex(ValueError, "cannot be overwritten"):
            validate_review_ingestion(existing, (review(),), self.manifest)

    def test_review_round_cannot_skip_a_number(self):
        with self.assertRaisesRegex(ValueError, "expected review round 1"):
            validate_review_ingestion(
                (), (review(review_round=2),), self.manifest
            )

    def test_atomic_writer_round_trips_through_canonical_loader(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "reviews.csv"
            write_reviews_atomically((review(),), destination)

            self.assertEqual((review(),), load_reviews(destination))


class ManifestFinalizationTests(unittest.TestCase):
    def test_atomic_finalizer_changes_only_review_statuses(self):
        source = Path(__file__).resolve().parent.parent / "data" / "scenario_manifest.csv"
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "scenario_manifest.csv"
            shutil.copy2(source, target)

            write_confirmed_manifest_atomically(target)
            confirmed = load_manifest(target)

            self.assertEqual(
                {ClassificationStatus.INDEPENDENTLY_CONFIRMED},
                {scenario.classification_status for scenario in confirmed},
            )
            self.assertEqual(
                {ClassificationStatus.INDEPENDENTLY_CONFIRMED},
                {scenario.oracle_review_status for scenario in confirmed},
            )

    def test_open_issue_ledger_is_machine_readable(self):
        self.assertIsInstance(documented_open_issue_rows(), tuple)


if __name__ == "__main__":
    unittest.main()
