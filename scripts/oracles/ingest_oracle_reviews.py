"""Validate and atomically append completed independent-review forms."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from pathlib import Path
from typing import Sequence

from scripts.oracles.oracle_validation import (
    DEFAULT_REVIEWS_PATH,
    REVIEW_COLUMNS,
    OracleReview,
    load_reviews,
)
from scripts.core.scenario_metadata import ScenarioMetadata, load_manifest


def validate_review_ingestion(
    existing: Sequence[OracleReview],
    incoming: Sequence[OracleReview],
    manifest: Sequence[ScenarioMetadata],
) -> tuple[OracleReview, ...]:
    if not incoming:
        raise ValueError("Incoming review form contains no completed records")

    expected_ids = {scenario.scenario_id for scenario in manifest}
    existing_keys = {
        (review.reviewer_id, review.scenario_id, review.review_round)
        for review in existing
    }
    prior_rounds: dict[tuple[str, str], list[int]] = {}
    for review in existing:
        prior_rounds.setdefault(
            (review.reviewer_id, review.scenario_id), []
        ).append(review.review_round)

    for review in incoming:
        if review.scenario_id not in expected_ids:
            raise ValueError(
                f"Incoming form references unexpected {review.scenario_id}"
            )
        full_key = (review.reviewer_id, review.scenario_id, review.review_round)
        if full_key in existing_keys:
            raise ValueError(
                "Review round already exists and cannot be overwritten: "
                f"{review.reviewer_id}/{review.scenario_id}/"
                f"round_{review.review_round}"
            )
        pair = (review.reviewer_id, review.scenario_id)
        previous = prior_rounds.get(pair, [])
        expected_round = max(previous) + 1 if previous else 1
        if review.review_round != expected_round:
            raise ValueError(
                f"{review.reviewer_id}/{review.scenario_id}: expected review "
                f"round {expected_round}, received {review.review_round}"
            )
    return tuple(existing) + tuple(incoming)


def write_reviews_atomically(
    reviews: Sequence[OracleReview], destination: Path
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            delete=False,
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            writer = csv.DictWriter(temporary_file, fieldnames=REVIEW_COLUMNS)
            writer.writeheader()
            writer.writerows(_review_row(review) for review in reviews)
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _review_row(review: OracleReview) -> dict[str, str | int]:
    return {
        "scenario_id": review.scenario_id,
        "reviewer_id": review.reviewer_id,
        "review_round": review.review_round,
        "oracle_decision": review.oracle_decision.value,
        "intent_preserved": "yes" if review.intent_preserved else "no",
        "complete_artifact_tree": (
            "yes" if review.complete_artifact_tree else "no"
        ),
        "no_unjustified_content": (
            "yes" if review.no_unjustified_content else "no"
        ),
        "syntactically_valid": "yes" if review.syntactically_valid else "no",
        "compilation_result": review.compilation_result.value,
        "tests_result": review.tests_result.value,
        "assigned_mapping": review.assigned_mapping.value,
        "assigned_change_type": review.assigned_change_type.value,
        "comments": review.comments,
        "reviewed_at_utc": review.reviewed_at_utc,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and append an independent oracle review form"
    )
    parser.add_argument("--form", type=Path, required=True)
    parser.add_argument(
        "--destination", type=Path, default=DEFAULT_REVIEWS_PATH
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Atomically append after validation; default is validation only",
    )
    args = parser.parse_args()

    existing = load_reviews(args.destination)
    incoming = load_reviews(args.form)
    combined = validate_review_ingestion(existing, incoming, load_manifest())
    reviewers = sorted({review.reviewer_id for review in incoming})
    print(
        f"Review form valid: {len(incoming)} record(s), reviewer(s): "
        f"{', '.join(reviewers)}"
    )
    if not args.commit:
        print("Dry run only; rerun with --commit to append the records")
        return 0
    write_reviews_atomically(combined, args.destination)
    print(
        f"Committed {len(incoming)} review record(s); destination now has "
        f"{len(combined)} record(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
