import unittest

from scripts.oracles.oracle_validation import (
    EvidenceResult,
    OracleDecision,
    OracleReview,
    cohens_kappa,
    pairwise_agreement,
    release_readiness_issues,
    review_coverage_issues,
)
from scripts.core.scenario_metadata import (
    ChangeType,
    MappingComplexity,
    load_manifest,
)


def accepted_review(scenario, reviewer_id):
    return OracleReview(
        scenario_id=scenario.scenario_id,
        reviewer_id=reviewer_id,
        review_round=1,
        oracle_decision=OracleDecision.ACCEPT,
        intent_preserved=True,
        complete_artifact_tree=True,
        no_unjustified_content=True,
        syntactically_valid=True,
        compilation_result=EvidenceResult.NOT_RUN,
        tests_result=EvidenceResult.NOT_RUN,
        assigned_mapping=scenario.mapping,
        assigned_change_type=scenario.change_type,
        comments="",
        reviewed_at_utc="2026-07-24T18:30:00Z",
    )


class OracleReviewCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_empty_review_file_leaves_all_scenarios_pending(self):
        issues = review_coverage_issues((), self.manifest)

        self.assertEqual(39, len(issues))

    def test_two_independent_reviewers_complete_coverage(self):
        reviews = [
            accepted_review(scenario, reviewer_id)
            for scenario in self.manifest
            for reviewer_id in ("reviewer_A", "reviewer_B")
        ]

        self.assertEqual(
            (), review_coverage_issues(tuple(reviews), self.manifest)
        )
        self.assertEqual(
            (), release_readiness_issues(tuple(reviews), self.manifest)
        )

    def test_two_rounds_by_same_reviewer_are_not_independent_reviews(self):
        scenario = self.manifest[0]
        first_round = accepted_review(scenario, "reviewer_A")
        second_round = OracleReview(
            **{
                **first_round.__dict__,
                "review_round": 2,
            }
        )

        issues = review_coverage_issues(
            (first_round, second_round), self.manifest
        )

        self.assertIn(
            f"{scenario.scenario_id} has 1 independent reviewer(s); 2 required",
            issues,
        )

    def test_coverage_does_not_imply_oracle_approval(self):
        reviews = []
        for scenario in self.manifest:
            for reviewer_id in ("reviewer_A", "reviewer_B"):
                review = accepted_review(scenario, reviewer_id)
                reviews.append(
                    OracleReview(
                        **{
                            **review.__dict__,
                            "oracle_decision": OracleDecision.NEEDS_REVISION,
                            "comments": "Oracle must be revised",
                        }
                    )
                )

        self.assertEqual(
            (), review_coverage_issues(tuple(reviews), self.manifest)
        )
        readiness = release_readiness_issues(tuple(reviews), self.manifest)
        self.assertEqual(39, len(readiness))
        self.assertIn("0 independent oracle approval(s)", readiness[0])


class AgreementTests(unittest.TestCase):
    def test_cohens_kappa_for_known_example(self):
        observed, kappa = cohens_kappa(
            ("A", "A", "B", "B"),
            ("A", "B", "B", "B"),
        )

        self.assertAlmostEqual(0.75, observed)
        self.assertAlmostEqual(0.5, kappa)

    def test_pairwise_agreement_reports_three_label_dimensions(self):
        manifest = load_manifest()
        reviews = [
            accepted_review(scenario, reviewer_id)
            for scenario in manifest
            for reviewer_id in ("reviewer_A", "reviewer_B")
        ]

        results = pairwise_agreement(tuple(reviews))

        self.assertEqual(3, len(results))
        self.assertEqual(
            {
                "oracle_decision",
                "assigned_mapping",
                "assigned_change_type",
            },
            {result.field_name for result in results},
        )
        for result in results:
            self.assertEqual(39, result.shared_scenarios)
            self.assertEqual(1.0, result.observed_agreement)
            self.assertEqual(1.0, result.cohens_kappa)


if __name__ == "__main__":
    unittest.main()
