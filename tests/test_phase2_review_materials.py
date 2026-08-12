import csv
import tempfile
import unittest
from pathlib import Path

from scripts.oracle_audit import audit_oracles
from scripts.prepare_oracle_review import prepare_review_packet
from scripts.phase2_gate import phase2_gate_categories
from scripts.scenario_metadata import load_manifest


class OracleTechnicalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_inventory_covers_every_declared_oracle_file(self):
        audit = audit_oracles(self.manifest)

        self.assertEqual(
            sum(len(scenario.expected_files) for scenario in self.manifest),
            len(audit.records),
        )
        self.assertTrue(all(len(record.sha256) == 64 for record in audit.records))

    def test_revised_oracles_pass_the_technical_audit(self):
        audit = audit_oracles(self.manifest)
        self.assertEqual((), audit.issues)


class ReviewPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_form_has_39_blinded_rows_with_no_prefilled_decision(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            packet = Path(temporary_directory) / "reviewer_A"
            prepare_review_packet(
                "reviewer_A", packet, self.manifest, include_artifacts=False
            )

            with (packet / "review_form.csv").open(
                "r", encoding="utf-8", newline=""
            ) as form_file:
                rows = list(csv.DictReader(form_file))

            self.assertEqual(39, len(rows))
            self.assertEqual({"reviewer_A"}, {row["reviewer_id"] for row in rows})
            self.assertEqual({"1"}, {row["review_round"] for row in rows})
            self.assertTrue(all(row["oracle_decision"] == "" for row in rows))
            self.assertTrue(all(row["assigned_mapping"] == "" for row in rows))
            self.assertTrue(
                all(row["assigned_change_type"] == "" for row in rows)
            )

            with (packet / "scenario_context.csv").open(
                "r", encoding="utf-8", newline=""
            ) as context_file:
                context = list(csv.DictReader(context_file))
            self.assertEqual(
                {"textual_structural_only"},
                {row["validation_scope"] for row in context},
            )
            self.assertNotIn("mapping", context[0])
            self.assertNotIn("change_type", context[0])

    def test_packet_contains_only_inputs_oracle_and_review_context(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            packet = Path(temporary_directory) / "reviewer_A"
            prepare_review_packet(
                "reviewer_A",
                packet,
                self.manifest[:1],
                include_artifacts=True,
            )

            scenario = packet / "artifacts" / "scenario_1"
            self.assertTrue((scenario / "base").is_dir())
            self.assertTrue((scenario / "left").is_dir())
            self.assertTrue((scenario / "right").is_dir())
            self.assertTrue((scenario / "proposed_oracle").is_dir())
            self.assertFalse((packet / "tool_outputs").exists())

    def test_later_round_can_target_only_revised_scenarios(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            packet = Path(temporary_directory) / "reviewer_A_round_2"
            prepare_review_packet(
                "reviewer_A",
                packet,
                self.manifest,
                include_artifacts=False,
                review_round=2,
                scenario_ids=("scenario_10", "scenario_17"),
            )

            with (packet / "review_form.csv").open(
                "r", encoding="utf-8", newline=""
            ) as form_file:
                rows = list(csv.DictReader(form_file))

            self.assertEqual(
                ["scenario_10", "scenario_17"],
                [row["scenario_id"] for row in rows],
            )
            self.assertEqual({"2"}, {row["review_round"] for row in rows})

            readme = (packet / "README.md").read_text(encoding="utf-8")
            self.assertIn("Round: `2`", readme)

    def test_existing_nonempty_packet_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            packet = Path(temporary_directory) / "reviewer_A"
            packet.mkdir()
            (packet / "existing.txt").write_text("keep", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                prepare_review_packet(
                    "reviewer_A",
                    packet,
                    self.manifest,
                    include_artifacts=False,
                )
            self.assertEqual(
                "keep", (packet / "existing.txt").read_text(encoding="utf-8")
            )


class Phase2GateTests(unittest.TestCase):
    def test_completed_phase2_gate_has_no_open_categories(self):
        categories = {
            category.name: category.issues
            for category in phase2_gate_categories()
        }

        self.assertTrue(categories)
        self.assertTrue(all(not issues for issues in categories.values()))


if __name__ == "__main__":
    unittest.main()
