import unittest
from collections import Counter

from scripts.scenario_metadata import (
    ChangeType,
    ClassificationStatus,
    MappingComplexity,
    ValidationScope,
    audit_scenario_artifacts,
    load_manifest,
)
from scripts.oracle_validation import load_reviews, release_readiness_issues


class ScenarioManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_manifest_contains_exactly_39_unique_scenarios(self):
        scenario_ids = [scenario.scenario_id for scenario in self.manifest]

        self.assertEqual(39, len(scenario_ids))
        self.assertEqual(39, len(set(scenario_ids)))
        self.assertEqual(
            {f"scenario_{number}" for number in range(1, 40)},
            set(scenario_ids),
        )

    def test_manifest_preserves_balanced_mapping_design(self):
        counts = Counter(scenario.mapping for scenario in self.manifest)

        self.assertEqual(13, counts[MappingComplexity.ONE_TO_ONE])
        self.assertEqual(13, counts[MappingComplexity.ONE_TO_MANY])
        self.assertEqual(13, counts[MappingComplexity.MANY_TO_MANY])

    def test_manifest_declares_30_structural_and_9_behavioral_scenarios(self):
        counts = Counter(scenario.change_type for scenario in self.manifest)

        self.assertEqual(30, counts[ChangeType.STRUCTURAL])
        self.assertEqual(9, counts[ChangeType.BEHAVIORAL])

    def test_labels_are_not_prematurely_marked_as_confirmed(self):
        statuses = {scenario.classification_status for scenario in self.manifest}
        if release_readiness_issues(load_reviews(), self.manifest):
            self.assertNotIn(ClassificationStatus.INDEPENDENTLY_CONFIRMED, statuses)
        else:
            self.assertEqual({ClassificationStatus.INDEPENDENTLY_CONFIRMED}, statuses)

    def test_oracles_are_not_prematurely_marked_as_confirmed(self):
        statuses = {scenario.oracle_review_status for scenario in self.manifest}
        if release_readiness_issues(load_reviews(), self.manifest):
            self.assertNotIn(ClassificationStatus.INDEPENDENTLY_CONFIRMED, statuses)
        else:
            self.assertEqual({ClassificationStatus.INDEPENDENTLY_CONFIRMED}, statuses)

    def test_manifest_contains_auditable_scope_and_acceptance_metadata(self):
        for scenario in self.manifest:
            with self.subTest(scenario=scenario.scenario_id):
                self.assertTrue(scenario.base_description)
                self.assertTrue(scenario.left_description)
                self.assertTrue(scenario.right_description)
                self.assertTrue(scenario.merge_intent)
                self.assertIn("workflow-confirmed oracle", scenario.acceptance_criteria)
                self.assertGreaterEqual(scenario.artifact_file_count, 1)
                self.assertGreaterEqual(scenario.logical_element_count, 1)
                self.assertTrue(scenario.expected_files)
                self.assertEqual(
                    ValidationScope.TEXTUAL_STRUCTURAL_ONLY,
                    scenario.validation_scope,
                )
                self.assertEqual("not_applicable", scenario.associated_tests)

    def test_all_tool_scenario_artifacts_exist_and_are_consistent(self):
        self.assertEqual((), audit_scenario_artifacts(self.manifest))


if __name__ == "__main__":
    unittest.main()
