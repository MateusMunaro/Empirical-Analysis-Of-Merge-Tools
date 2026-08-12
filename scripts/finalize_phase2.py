"""Atomically confirm Phase 2 manifest statuses after all evidence is valid."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from pathlib import Path
from typing import Sequence

from scripts.oracle_audit import audit_oracles
from scripts.oracle_validation import load_reviews, release_readiness_issues
from scripts.phase2_gate import (
    documented_open_issue_rows,
    validation_evidence_issues,
)
from scripts.scenario_metadata import (
    DEFAULT_MANIFEST_PATH,
    ClassificationStatus,
    ScenarioMetadata,
    audit_scenario_artifacts,
    load_manifest,
)


def phase2_finalization_issues(
    manifest: Sequence[ScenarioMetadata] | None = None,
) -> tuple[str, ...]:
    scenarios = tuple(manifest or load_manifest())
    issues: list[str] = []
    issues.extend(audit_scenario_artifacts(scenarios))
    issues.extend(audit_oracles(scenarios).issues)
    issues.extend(release_readiness_issues(load_reviews(), scenarios))
    issues.extend(validation_evidence_issues(scenarios))
    issues.extend(documented_open_issue_rows())
    return tuple(issues)


def write_confirmed_manifest_atomically(path: Path) -> None:
    with path.open("r", encoding="utf-8", newline="") as manifest_file:
        reader = csv.DictReader(manifest_file)
        if reader.fieldnames is None:
            raise ValueError("Scenario manifest has no header")
        fieldnames = tuple(reader.fieldnames)
        rows = list(reader)

    confirmed = ClassificationStatus.INDEPENDENTLY_CONFIRMED.value
    for row in rows:
        row["classification_status"] = confirmed
        row["oracle_review_status"] = confirmed

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            delete=False,
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            writer = csv.DictWriter(temporary_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Confirm Phase 2 statuses after independent review"
    )
    parser.add_argument(
        "--manifest", type=Path, default=DEFAULT_MANIFEST_PATH
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Write confirmed statuses; default is a dry-run readiness check",
    )
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    issues = phase2_finalization_issues(manifest)
    if issues:
        print(f"Phase 2 cannot be finalized: {len(issues)} open issue(s)")
        for issue in issues[:10]:
            print(f"- {issue}")
        if len(issues) > 10:
            print(f"- ... {len(issues) - 10} additional issue(s)")
        return 1

    print("Phase 2 evidence is complete and internally consistent")
    if not args.commit:
        print("Dry run only; rerun with --commit to confirm manifest statuses")
        return 0
    write_confirmed_manifest_atomically(args.manifest)
    load_manifest(args.manifest)
    print("Manifest oracle and classification statuses are independently_confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
