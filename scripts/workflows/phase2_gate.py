"""Fail-closed release gate for Phase 2 metadata and oracle validation."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from scripts.oracles.oracle_audit import audit_oracles
from scripts.oracles.oracle_validation import load_reviews, release_readiness_issues
from scripts.core.scenario_metadata import (
    ClassificationStatus,
    REPO_ROOT,
    ValidationScope,
    audit_scenario_artifacts,
    load_manifest,
)


DEFAULT_TECHNICAL_ISSUES_PATH = REPO_ROOT / "data" / "oracle_technical_issues.csv"


def documented_open_issue_rows(
    path: Path = DEFAULT_TECHNICAL_ISSUES_PATH,
) -> tuple[str, ...]:
    if not path.is_file():
        return ()
    with path.open("r", encoding="utf-8", newline="") as issue_file:
        rows = list(csv.DictReader(issue_file))
    return tuple(
        f"{row.get('scenario_id', '?')}/{row.get('relative_path', '?')}: "
        f"{row.get('issue', 'undocumented issue')}"
        for row in rows
        if (row.get("status") or "").startswith("open")
    )


@dataclass(frozen=True)
class GateCategory:
    name: str
    issues: tuple[str, ...]


def phase2_gate_categories() -> tuple[GateCategory, ...]:
    manifest = load_manifest()
    reviews = load_reviews()
    return (
        GateCategory(
            "scenario artifact integrity", audit_scenario_artifacts(manifest)
        ),
        GateCategory("oracle technical audit", audit_oracles(manifest).issues),
        GateCategory("documented oracle issue ledger", documented_open_issue_rows()),
        GateCategory(
            "two-pass oracle and label review",
            release_readiness_issues(reviews, manifest),
        ),
        GateCategory(
            "manifest classification status",
            tuple(
                f"{scenario.scenario_id}: {scenario.classification_status.value}"
                for scenario in manifest
                if scenario.classification_status
                is not ClassificationStatus.INDEPENDENTLY_CONFIRMED
            ),
        ),
        GateCategory(
            "manifest oracle status",
            tuple(
                f"{scenario.scenario_id}: {scenario.oracle_review_status.value}"
                for scenario in manifest
                if scenario.oracle_review_status
                is not ClassificationStatus.INDEPENDENTLY_CONFIRMED
            ),
        ),
        GateCategory(
            "validation evidence policy", validation_evidence_issues(manifest)
        ),
    )


def validation_evidence_issues(manifest) -> tuple[str, ...]:
    issues: list[str] = []
    for scenario in manifest:
        if scenario.validation_scope is ValidationScope.TEXTUAL_STRUCTURAL_ONLY:
            continue
        for raw_path in scenario.associated_tests.split(";"):
            path = REPO_ROOT / raw_path
            if not path.is_file():
                issues.append(
                    f"{scenario.scenario_id}: associated test is missing: {raw_path}"
                )
    return tuple(issues)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the Phase 2 release gate")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    categories = phase2_gate_categories()
    open_categories = [category for category in categories if category.issues]
    if not open_categories:
        print("PHASE 2 GATE: PASS")
        return 0

    total = sum(len(category.issues) for category in open_categories)
    print(f"PHASE 2 GATE: BLOCKED ({total} open check(s))")
    for category in categories:
        if not category.issues:
            print(f"- PASS: {category.name}")
            continue
        print(f"- BLOCKED: {category.name} ({len(category.issues)})")
        preview = category.issues if args.verbose else category.issues[:3]
        for issue in preview:
            print(f"  - {issue}")
        hidden = len(category.issues) - len(preview)
        if hidden:
            print(f"  - ... {hidden} additional issue(s); rerun with --verbose")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
