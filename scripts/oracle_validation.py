"""Independent oracle and scenario-classification review records."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from pathlib import Path
from typing import Callable, Sequence

from scripts.scenario_metadata import (
    ChangeType,
    DEFAULT_MANIFEST_PATH,
    MappingComplexity,
    ScenarioMetadata,
    load_manifest,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REVIEWS_PATH = REPO_ROOT / "data" / "oracle_reviews.csv"


class OracleDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    NEEDS_REVISION = "needs_revision"


class EvidenceResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_RUN = "not_run"
    NOT_APPLICABLE = "not_applicable"


REVIEW_COLUMNS = (
    "scenario_id",
    "reviewer_id",
    "review_round",
    "oracle_decision",
    "intent_preserved",
    "complete_artifact_tree",
    "no_unjustified_content",
    "syntactically_valid",
    "compilation_result",
    "tests_result",
    "assigned_mapping",
    "assigned_change_type",
    "comments",
    "reviewed_at_utc",
)


class ReviewValidationError(ValueError):
    """Raised when review records are malformed or incomplete."""


@dataclass(frozen=True)
class OracleReview:
    scenario_id: str
    reviewer_id: str
    review_round: int
    oracle_decision: OracleDecision
    intent_preserved: bool
    complete_artifact_tree: bool
    no_unjustified_content: bool
    syntactically_valid: bool
    compilation_result: EvidenceResult
    tests_result: EvidenceResult
    assigned_mapping: MappingComplexity
    assigned_change_type: ChangeType
    comments: str
    reviewed_at_utc: str


@dataclass(frozen=True)
class AgreementResult:
    reviewer_a: str
    reviewer_b: str
    field_name: str
    shared_scenarios: int
    observed_agreement: float
    cohens_kappa: float


def load_reviews(path: Path = DEFAULT_REVIEWS_PATH) -> tuple[OracleReview, ...]:
    with path.open("r", encoding="utf-8", newline="") as review_file:
        reader = csv.DictReader(review_file)
        if reader.fieldnames is None:
            raise ReviewValidationError("Oracle review file has no header")
        missing_columns = [
            column for column in REVIEW_COLUMNS if column not in reader.fieldnames
        ]
        if missing_columns:
            raise ReviewValidationError(
                f"Oracle review file is missing columns: {', '.join(missing_columns)}"
            )

        reviews: list[OracleReview] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                review = OracleReview(
                    scenario_id=_required(row, "scenario_id"),
                    reviewer_id=_required(row, "reviewer_id"),
                    review_round=_positive_integer(row, "review_round"),
                    oracle_decision=OracleDecision(
                        _required(row, "oracle_decision")
                    ),
                    intent_preserved=_boolean(row, "intent_preserved"),
                    complete_artifact_tree=_boolean(
                        row, "complete_artifact_tree"
                    ),
                    no_unjustified_content=_boolean(
                        row, "no_unjustified_content"
                    ),
                    syntactically_valid=_boolean(row, "syntactically_valid"),
                    compilation_result=EvidenceResult(
                        _required(row, "compilation_result")
                    ),
                    tests_result=EvidenceResult(
                        _required(row, "tests_result")
                    ),
                    assigned_mapping=MappingComplexity(
                        _required(row, "assigned_mapping")
                    ),
                    assigned_change_type=ChangeType(
                        _required(row, "assigned_change_type")
                    ),
                    comments=(row.get("comments") or "").strip(),
                    reviewed_at_utc=_required(row, "reviewed_at_utc"),
                )
                _validate_decision_consistency(review)
                reviews.append(review)
            except (TypeError, ValueError) as error:
                raise ReviewValidationError(
                    f"Invalid oracle review row {line_number}: {error}"
                ) from error

    _reject_duplicate_rounds(reviews)
    return tuple(reviews)


def latest_reviews(reviews: Sequence[OracleReview]) -> tuple[OracleReview, ...]:
    """Keep the highest review round for each reviewer-scenario pair."""

    latest: dict[tuple[str, str], OracleReview] = {}
    for review in reviews:
        key = (review.reviewer_id, review.scenario_id)
        previous = latest.get(key)
        if previous is None or review.review_round > previous.review_round:
            latest[key] = review
    return tuple(latest.values())


def review_coverage_issues(
    reviews: Sequence[OracleReview],
    manifest: Sequence[ScenarioMetadata],
    minimum_reviewers: int = 2,
) -> tuple[str, ...]:
    """Report scenarios lacking independent final reviews."""

    if minimum_reviewers < 1:
        raise ValueError("minimum_reviewers must be at least 1")

    expected_ids = {scenario.scenario_id for scenario in manifest}
    issues: list[str] = []
    reviewers_by_scenario: dict[str, set[str]] = {
        scenario_id: set() for scenario_id in expected_ids
    }

    for review in latest_reviews(reviews):
        if review.scenario_id not in expected_ids:
            issues.append(f"Review references unexpected {review.scenario_id}")
            continue
        reviewers_by_scenario[review.scenario_id].add(review.reviewer_id)

    for scenario_id in sorted(expected_ids, key=_scenario_number):
        reviewer_count = len(reviewers_by_scenario[scenario_id])
        if reviewer_count < minimum_reviewers:
            issues.append(
                f"{scenario_id} has {reviewer_count} independent reviewer(s); "
                f"{minimum_reviewers} required"
            )
    return tuple(issues)


def release_readiness_issues(
    reviews: Sequence[OracleReview],
    manifest: Sequence[ScenarioMetadata],
    minimum_confirmations: int = 2,
) -> tuple[str, ...]:
    """Require independent oracle approval and label confirmation."""

    if minimum_confirmations < 1:
        raise ValueError("minimum_confirmations must be at least 1")

    final_reviews = latest_reviews(reviews)
    reviews_by_scenario: dict[str, list[OracleReview]] = {
        scenario.scenario_id: [] for scenario in manifest
    }
    for review in final_reviews:
        if review.scenario_id in reviews_by_scenario:
            reviews_by_scenario[review.scenario_id].append(review)

    issues = list(
        review_coverage_issues(
            reviews, manifest, minimum_reviewers=minimum_confirmations
        )
    )
    for scenario in manifest:
        scenario_reviews = reviews_by_scenario[scenario.scenario_id]
        approvals = {
            review.reviewer_id
            for review in scenario_reviews
            if review.oracle_decision is OracleDecision.ACCEPT
        }
        mapping_confirmations = {
            review.reviewer_id
            for review in scenario_reviews
            if review.assigned_mapping is scenario.mapping
        }
        change_type_confirmations = {
            review.reviewer_id
            for review in scenario_reviews
            if review.assigned_change_type is scenario.change_type
        }

        if len(approvals) < minimum_confirmations:
            issues.append(
                f"{scenario.scenario_id} has {len(approvals)} independent "
                f"oracle approval(s); {minimum_confirmations} required"
            )
        if len(mapping_confirmations) < minimum_confirmations:
            issues.append(
                f"{scenario.scenario_id} has {len(mapping_confirmations)} "
                f"mapping confirmation(s); {minimum_confirmations} required"
            )
        if len(change_type_confirmations) < minimum_confirmations:
            issues.append(
                f"{scenario.scenario_id} has {len(change_type_confirmations)} "
                f"change-type confirmation(s); {minimum_confirmations} required"
            )
    return tuple(issues)


def pairwise_agreement(
    reviews: Sequence[OracleReview],
) -> tuple[AgreementResult, ...]:
    """Calculate pairwise agreement for decision and classification labels."""

    final_reviews = latest_reviews(reviews)
    reviewer_ids = sorted({review.reviewer_id for review in final_reviews})
    by_reviewer = {
        reviewer_id: {
            review.scenario_id: review
            for review in final_reviews
            if review.reviewer_id == reviewer_id
        }
        for reviewer_id in reviewer_ids
    }

    fields: tuple[tuple[str, Callable[[OracleReview], str]], ...] = (
        ("oracle_decision", lambda review: review.oracle_decision.value),
        ("assigned_mapping", lambda review: review.assigned_mapping.value),
        (
            "assigned_change_type",
            lambda review: review.assigned_change_type.value,
        ),
    )

    results: list[AgreementResult] = []
    for reviewer_a, reviewer_b in combinations(reviewer_ids, 2):
        shared_ids = sorted(
            set(by_reviewer[reviewer_a]) & set(by_reviewer[reviewer_b]),
            key=_scenario_number,
        )
        if not shared_ids:
            continue
        for field_name, getter in fields:
            labels_a = [
                getter(by_reviewer[reviewer_a][scenario_id])
                for scenario_id in shared_ids
            ]
            labels_b = [
                getter(by_reviewer[reviewer_b][scenario_id])
                for scenario_id in shared_ids
            ]
            observed, kappa = cohens_kappa(labels_a, labels_b)
            results.append(
                AgreementResult(
                    reviewer_a=reviewer_a,
                    reviewer_b=reviewer_b,
                    field_name=field_name,
                    shared_scenarios=len(shared_ids),
                    observed_agreement=observed,
                    cohens_kappa=kappa,
                )
            )
    return tuple(results)


def cohens_kappa(
    labels_a: Sequence[str], labels_b: Sequence[str]
) -> tuple[float, float]:
    if len(labels_a) != len(labels_b):
        raise ValueError("Label sequences must have the same length")
    if not labels_a:
        raise ValueError("At least one paired label is required")

    total = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / total
    categories = set(labels_a) | set(labels_b)
    expected = sum(
        (labels_a.count(category) / total)
        * (labels_b.count(category) / total)
        for category in categories
    )
    if expected == 1.0:
        kappa = 1.0 if observed == 1.0 else 0.0
    else:
        kappa = (observed - expected) / (1.0 - expected)
    return observed, kappa


def _validate_decision_consistency(review: OracleReview) -> None:
    if review.oracle_decision is not OracleDecision.ACCEPT:
        return
    human_checks = (
        review.intent_preserved,
        review.complete_artifact_tree,
        review.no_unjustified_content,
        review.syntactically_valid,
    )
    if not all(human_checks):
        raise ValueError("an accepted oracle must pass all four review criteria")
    if review.compilation_result is EvidenceResult.FAIL:
        raise ValueError("an oracle with failed compilation cannot be accepted")
    if review.tests_result is EvidenceResult.FAIL:
        raise ValueError("an oracle with failed tests cannot be accepted")


def _reject_duplicate_rounds(reviews: Sequence[OracleReview]) -> None:
    seen: set[tuple[str, str, int]] = set()
    for review in reviews:
        key = (review.reviewer_id, review.scenario_id, review.review_round)
        if key in seen:
            raise ReviewValidationError(
                "Duplicate review round for "
                f"{review.reviewer_id}/{review.scenario_id}/round_{review.review_round}"
            )
        seen.add(key)


def _required(row: dict[str, str | None], field: str) -> str:
    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"'{field}' must not be blank")
    return value.strip()


def _positive_integer(row: dict[str, str | None], field: str) -> int:
    value = int(_required(row, field))
    if value < 1:
        raise ValueError(f"'{field}' must be a positive integer")
    return value


def _boolean(row: dict[str, str | None], field: str) -> bool:
    value = _required(row, field).lower()
    if value == "yes":
        return True
    if value == "no":
        return False
    raise ValueError(f"'{field}' must be 'yes' or 'no'")


def _scenario_number(scenario_id: str) -> int:
    try:
        return int(scenario_id.removeprefix("scenario_"))
    except ValueError:
        return 10**9


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate independent oracle review records"
    )
    parser.add_argument(
        "--reviews",
        type=Path,
        default=DEFAULT_REVIEWS_PATH,
        help="Path to oracle_reviews.csv",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path to scenario_manifest.csv",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return an error until every scenario has two independent reviews",
    )
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    reviews = load_reviews(args.reviews)
    print(f"Review file valid: {len(reviews)} review record(s)")

    coverage_issues = review_coverage_issues(reviews, manifest)
    if coverage_issues:
        print(
            f"Independent review pending: {len(coverage_issues)} "
            "coverage issue(s)"
        )
    else:
        print("Independent review coverage valid for all 39 scenarios")

    readiness_issues = release_readiness_issues(reviews, manifest)
    if readiness_issues:
        print(
            f"Release readiness pending: {len(readiness_issues)} issue(s)"
        )
        if args.require_complete:
            for issue in readiness_issues:
                print(f"- {issue}")
            return 1
    else:
        print("All oracles and scenario labels are independently confirmed")

    for result in pairwise_agreement(reviews):
        print(
            f"{result.reviewer_a} vs {result.reviewer_b} "
            f"[{result.field_name}]: n={result.shared_scenarios}, "
            f"agreement={result.observed_agreement:.3f}, "
            f"kappa={result.cohens_kappa:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
