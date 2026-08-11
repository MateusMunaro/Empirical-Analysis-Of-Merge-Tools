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

    def test_known_filename_type_issues_remain_explicit(self):
        audit = audit_oracles(self.manifest)

        self.assertEqual(
            {
                "scenario_17/Person.java: public type PersonIdentity does not match Person.java",
                "scenario_26/Custumer.java: public type Customer does not match Custumer.java",
            },
            set(audit.issues),
        )


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
    def test_gate_passes_artifact_integrity_but_exposes_real_blockers(self):
        categories = {
            category.name: category.issues
            for category in phase2_gate_categories()
        }

        self.assertEqual((), categories["scenario artifact integrity"])
        self.assertEqual(2, len(categories["oracle technical audit"]))
        self.assertEqual(
            156, len(categories["independent oracle and label review"])
        )
        self.assertEqual(39, len(categories["manifest classification status"]))
        self.assertEqual(39, len(categories["manifest oracle status"]))
        self.assertEqual(39, len(categories["scenario tests"]))


if __name__ == "__main__":
    unittest.main()
