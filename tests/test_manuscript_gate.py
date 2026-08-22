import json
import tempfile
import unittest
from pathlib import Path

from scripts.quality.manuscript_gate import manuscript_issues


VALID_TEXT = r"""
\section{Results}
117 tool--scenario observations
End-to-end F1
$TP=2076$ and $TP=883$
Only two of 117 cells
We report no primary significance test
controlled synthetic
.464 .452 .711 .310
\includegraphics{F0.pdf}
\includegraphics{F1.pdf}
\includegraphics{F2.pdf}
\includegraphics{F3.pdf}
"""


class ManuscriptGateTests(unittest.TestCase):
    def test_rejects_legacy_group_and_mutable_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manuscript = Path(temporary_directory) / "paper.tex"
            manuscript.write_text(
                VALID_TEXT + "\nGroup 1: Completely Correct\nscripts/legacy.py",
                encoding="utf-8",
            )
            issues = manuscript_issues(manuscript)
            self.assertTrue(any("legacy overlapping" in issue for issue in issues))
            self.assertTrue(any("mutable repository path" in issue for issue in issues))

    def test_requires_stable_figure_assets_when_requested(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manuscript = root / "paper.tex"
            manuscript.write_text(VALID_TEXT, encoding="utf-8")
            self.assertEqual(4, len(manuscript_issues(manuscript, require_assets=True)))
            for stable_id in ("F0", "F1", "F2", "F3"):
                (root / f"{stable_id}.pdf").write_bytes(b"pdf")
            self.assertEqual((), manuscript_issues(manuscript, require_assets=True))

    def test_summary_values_are_checked_without_repository_coupling(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manuscript = root / "paper.tex"
            manuscript.write_text(VALID_TEXT, encoding="utf-8")
            summary = root / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "tool_summary": [
                            {
                                "tool_name": "FSTMerge",
                                "macro_f1_score_mean": 0.46361121830998053,
                                "end_to_end_f1_zero_unavailable": 0.45172375117382718,
                            },
                            {
                                "tool_name": "IntelliMerge",
                                "macro_f1_score_mean": 0.711073323120824,
                                "end_to_end_f1_zero_unavailable": 0.30995503828343612,
                            },
                            {
                                "tool_name": "JDime",
                                "macro_f1_score_mean": None,
                                "end_to_end_f1_zero_unavailable": 0.0,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                (), manuscript_issues(manuscript, summary_path=summary)
            )

    def test_bibliography_must_cover_and_follow_first_citation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manuscript = Path(temporary_directory) / "paper.tex"
            manuscript.write_text(
                VALID_TEXT
                + "\nFirst \\cite{a}, then \\cite{b}.\n"
                + "\\begin{thebibliography}{00}\n"
                + "\\bibitem{b} B.\n\\bibitem{a} A.\n"
                + "\\end{thebibliography}\n",
                encoding="utf-8",
            )
            self.assertIn(
                "bibliography is not ordered by first citation",
                manuscript_issues(manuscript),
            )

    def test_current_manuscript_passes_when_available(self):
        workspace = Path(__file__).resolve().parents[2]
        manuscript = workspace / "article" / "access (4).tex"
        if not manuscript.is_file():
            self.skipTest("current manuscript is not present")
        summary = (
            Path(__file__).resolve().parents[1]
            / "evaluation_results"
            / "revised_experiment"
            / "canonical_run_3"
            / "phase5_analysis"
            / "analysis_summary.json"
        )
        self.assertEqual(
            (),
            manuscript_issues(
                manuscript, summary_path=summary, require_assets=True
            ),
        )


if __name__ == "__main__":
    unittest.main()
