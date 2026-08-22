"""Prepare blinded, output-free material for an independent oracle reviewer."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path
from typing import Sequence

from scripts.oracles.oracle_validation import REVIEW_COLUMNS
from scripts.core.scenario_metadata import ScenarioMetadata, load_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_TOOL = "FSTMerge"

CONTEXT_COLUMNS = (
    "scenario_id",
    "title",
    "base_description",
    "left_description",
    "right_description",
    "merge_intent",
    "acceptance_criteria",
    "expected_files",
    "validation_scope",
    "associated_tests",
)


def prepare_review_packet(
    reviewer_id: str,
    output_directory: Path,
    manifest: Sequence[ScenarioMetadata] | None = None,
    repo_root: Path = REPO_ROOT,
    include_artifacts: bool = True,
    review_round: int = 1,
    scenario_ids: Sequence[str] | None = None,
) -> Path:
    """Create a blinded review packet without tool outputs or proposed labels."""

    reviewer_id = _validate_reviewer_id(reviewer_id)
    if review_round < 1:
        raise ValueError("review_round must be at least 1")
    scenarios = _select_scenarios(
        tuple(manifest or load_manifest()), scenario_ids
    )
    _require_empty_target(output_directory)
    output_directory.mkdir(parents=True)

    _write_review_form(
        reviewer_id,
        scenarios,
        output_directory / "review_form.csv",
        review_round,
    )
    _write_context(scenarios, output_directory / "scenario_context.csv")
    (output_directory / "README.md").write_text(
        _packet_readme(reviewer_id, include_artifacts, review_round),
        encoding="utf-8",
    )

    if include_artifacts:
        artifact_root = output_directory / "artifacts"
        for scenario in scenarios:
            target = artifact_root / scenario.scenario_id
            source = (
                repo_root
                / "scenarios_base"
                / CANONICAL_TOOL
                / scenario.scenario_id
            )
            for variant in ("base", "left", "right"):
                shutil.copytree(source / variant, target / variant)
            shutil.copytree(
                repo_root
                / "output"
                / CANONICAL_TOOL
                / "expected"
                / scenario.scenario_id,
                target / "proposed_oracle",
            )
    return output_directory


def _write_review_form(
    reviewer_id: str,
    manifest: Sequence[ScenarioMetadata],
    path: Path,
    review_round: int,
) -> None:
    with path.open("w", encoding="utf-8", newline="") as form_file:
        writer = csv.DictWriter(form_file, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for scenario in manifest:
            row = {column: "" for column in REVIEW_COLUMNS}
            row.update(
                {
                    "scenario_id": scenario.scenario_id,
                    "reviewer_id": reviewer_id,
                    "review_round": str(review_round),
                }
            )
            writer.writerow(row)


def _write_context(
    manifest: Sequence[ScenarioMetadata], path: Path
) -> None:
    with path.open("w", encoding="utf-8", newline="") as context_file:
        writer = csv.DictWriter(context_file, fieldnames=CONTEXT_COLUMNS)
        writer.writeheader()
        for scenario in manifest:
            writer.writerow(
                {
                    "scenario_id": scenario.scenario_id,
                    "title": scenario.title,
                    "base_description": scenario.base_description,
                    "left_description": scenario.left_description,
                    "right_description": scenario.right_description,
                    "merge_intent": scenario.merge_intent,
                    "acceptance_criteria": scenario.acceptance_criteria,
                    "expected_files": ";".join(scenario.expected_files),
                    "validation_scope": scenario.validation_scope.value,
                    "associated_tests": scenario.associated_tests,
                }
            )


def _packet_readme(
    reviewer_id: str, includes_artifacts: bool, review_round: int
) -> str:
    artifact_instruction = (
        "Inspect only `artifacts/<scenario>/base`, `left`, `right`, and "
        "`proposed_oracle`."
        if includes_artifacts
        else "Obtain the artifact trees from the study coordinator before review."
    )
    return f"""# Independent oracle review packet

Reviewer: `{reviewer_id}`  
Round: `{review_round}`

{artifact_instruction}

Do not inspect merge-tool outputs, scores, previous reviewer decisions, or the
proposed mapping/change-type labels. Apply the oracle-review and taxonomy rules
in the repository's main `README.md`, complete every field in
`review_form.csv`, and use an ISO 8601 UTC timestamp. A non-accept decision or
classification concern requires a substantive comment. Return the completed
form without modifying earlier rounds. The study coordinator validates and
appends it to `data/oracle_reviews.csv`.

For `validation_scope=textual_structural_only`, use `tests_result=not_applicable`.
Use `compilation_result=not_run` unless a documented compilation fixture was
actually executed; do not infer compilation from visual inspection.
"""


def _select_scenarios(
    manifest: Sequence[ScenarioMetadata], scenario_ids: Sequence[str] | None
) -> tuple[ScenarioMetadata, ...]:
    if scenario_ids is None:
        return tuple(manifest)
    requested = tuple(scenario_ids)
    if not requested:
        raise ValueError("scenario_ids must not be empty when provided")
    if len(set(requested)) != len(requested):
        raise ValueError("scenario_ids contains duplicates")
    by_id = {scenario.scenario_id: scenario for scenario in manifest}
    unexpected = [scenario_id for scenario_id in requested if scenario_id not in by_id]
    if unexpected:
        raise ValueError(
            "Unknown scenario_id(s): " + ", ".join(unexpected)
        )
    requested_set = set(requested)
    return tuple(
        scenario for scenario in manifest if scenario.scenario_id in requested_set
    )


def _validate_reviewer_id(reviewer_id: str) -> str:
    normalized = reviewer_id.strip()
    if not normalized or normalized != reviewer_id:
        raise ValueError("reviewer_id must be nonblank and have no outer whitespace")
    if any(character in normalized for character in ("/", "\\", "..")):
        raise ValueError("reviewer_id contains an unsafe path component")
    return normalized


def _require_empty_target(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Review packet target is not empty: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare an independent oracle review packet"
    )
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--round", type=int, default=1, dest="review_round")
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenario_ids",
        help="Limit the packet to a scenario ID; repeat for multiple IDs",
    )
    parser.add_argument(
        "--form-only",
        action="store_true",
        help="Create the form and context without copying artifact trees",
    )
    args = parser.parse_args()

    prepare_review_packet(
        reviewer_id=args.reviewer,
        output_directory=args.output,
        include_artifacts=not args.form_only,
        review_round=args.review_round,
        scenario_ids=args.scenario_ids,
    )
    print(f"Prepared independent review packet: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
