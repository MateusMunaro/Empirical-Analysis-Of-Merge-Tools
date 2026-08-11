"""Fail-closed release gate for Phase 2 metadata and oracle validation."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from scripts.oracle_audit import audit_oracles
from scripts.oracle_validation import load_reviews, release_readiness_issues
from scripts.scenario_metadata import (
    ClassificationStatus,
    audit_scenario_artifacts,
    load_manifest,
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
        GateCategory(
            "independent oracle and label review",
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
            "scenario tests",
            tuple(
                f"{scenario.scenario_id}: no executable acceptance test is defined"
                for scenario in manifest
                if scenario.associated_tests == "none_defined"
            ),
        ),
    )


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
