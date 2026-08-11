"""Technical, non-human audit and inventory of proposed oracle trees."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from scripts.evaluation_metrics import normalized_lines
from scripts.scenario_metadata import ScenarioMetadata, load_manifest


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY_PATH = REPO_ROOT / "data" / "oracle_inventory.csv"
CANONICAL_TOOL = "FSTMerge"

CONFLICT_MARKER = re.compile(r"^(<<<<<<<|=======|>>>>>>>|\|\|\|\|\|\|\|)(?:\s|$)")
TOP_LEVEL_PUBLIC_TYPE = re.compile(
    r"^public\s+(?:abstract\s+|final\s+)?(?:class|interface|enum|record)\s+"
    r"([A-Za-z_$][A-Za-z0-9_$]*)\b",
    flags=re.MULTILINE,
)

INVENTORY_COLUMNS = (
    "scenario_id",
    "relative_path",
    "sha256",
    "size_bytes",
    "normalized_line_count",
    "public_type",
    "conflict_marker_count",
    "technical_status",
)


@dataclass(frozen=True)
class OracleFileRecord:
    scenario_id: str
    relative_path: str
    sha256: str
    size_bytes: int
    normalized_line_count: int
    public_type: str
    conflict_marker_count: int
    technical_status: str

    def as_row(self) -> dict[str, str | int]:
        return {
            "scenario_id": self.scenario_id,
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "normalized_line_count": self.normalized_line_count,
            "public_type": self.public_type,
            "conflict_marker_count": self.conflict_marker_count,
            "technical_status": self.technical_status,
        }


@dataclass(frozen=True)
class OracleAudit:
    records: tuple[OracleFileRecord, ...]
    issues: tuple[str, ...]


def audit_oracles(
    manifest: Sequence[ScenarioMetadata],
    repo_root: Path = REPO_ROOT,
    canonical_tool: str = CANONICAL_TOOL,
) -> OracleAudit:
    """Audit encoding, paths, conflict markers, type names, and checksums.

    This is a technical precheck, not an oracle-acceptance decision and not a
    substitute for compilation, behavioral tests, or independent review.
    """

    records: list[OracleFileRecord] = []
    issues: list[str] = []
    for scenario in manifest:
        oracle_root = (
            repo_root / "output" / canonical_tool / "expected" / scenario.scenario_id
        )
        if not oracle_root.is_dir():
            issues.append(f"{scenario.scenario_id}: oracle directory is missing")
            continue

        actual_paths = tuple(
            sorted(
                path.relative_to(oracle_root).as_posix()
                for path in oracle_root.rglob("*.java")
                if path.is_file()
            )
        )
        if actual_paths != scenario.expected_files:
            issues.append(
                f"{scenario.scenario_id}: expected_files does not match oracle tree"
            )

        for relative_path in actual_paths:
            path = oracle_root / relative_path
            raw = path.read_bytes()
            file_issues: list[str] = []
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as error:
                issues.append(
                    f"{scenario.scenario_id}/{relative_path}: invalid UTF-8: {error}"
                )
                records.append(
                    OracleFileRecord(
                        scenario_id=scenario.scenario_id,
                        relative_path=relative_path,
                        sha256=hashlib.sha256(raw).hexdigest(),
                        size_bytes=len(raw),
                        normalized_line_count=0,
                        public_type="",
                        conflict_marker_count=0,
                        technical_status="fail",
                    )
                )
                continue

            lines = normalized_lines(text)
            if not lines or not any(line.strip() for line in lines):
                file_issues.append("oracle Java file is empty")
            marker_count = sum(bool(CONFLICT_MARKER.match(line)) for line in lines)
            if marker_count:
                file_issues.append(f"contains {marker_count} conflict marker(s)")

            public_types = TOP_LEVEL_PUBLIC_TYPE.findall(text)
            public_type = ";".join(public_types)
            expected_type = Path(relative_path).stem
            if len(public_types) != 1:
                file_issues.append(
                    f"expected one public top-level type, found {len(public_types)}"
                )
            elif public_types[0] != expected_type:
                file_issues.append(
                    f"public type {public_types[0]} does not match {expected_type}.java"
                )

            for issue in file_issues:
                issues.append(f"{scenario.scenario_id}/{relative_path}: {issue}")
            records.append(
                OracleFileRecord(
                    scenario_id=scenario.scenario_id,
                    relative_path=relative_path,
                    sha256=hashlib.sha256(raw).hexdigest(),
                    size_bytes=len(raw),
                    normalized_line_count=len(lines),
                    public_type=public_type,
                    conflict_marker_count=marker_count,
                    technical_status="fail" if file_issues else "pass",
                )
            )
    return OracleAudit(records=tuple(records), issues=tuple(issues))


def write_inventory(records: Sequence[OracleFileRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as inventory_file:
        writer = csv.DictWriter(inventory_file, fieldnames=INVENTORY_COLUMNS)
        writer.writeheader()
        writer.writerows(record.as_row() for record in records)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit and inventory proposed oracles")
    parser.add_argument(
        "--inventory", type=Path, default=DEFAULT_INVENTORY_PATH
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Do not rewrite the inventory"
    )
    args = parser.parse_args()

    audit = audit_oracles(load_manifest())
    if not args.check_only:
        write_inventory(audit.records, args.inventory)
        print(f"Wrote {len(audit.records)} oracle file records to {args.inventory}")
    if audit.issues:
        print(f"Oracle technical audit failed with {len(audit.issues)} issue(s):")
        for issue in audit.issues:
            print(f"- {issue}")
        return 1
    print(
        f"Oracle technical audit valid: {len(audit.records)} files across "
        f"{len({record.scenario_id for record in audit.records})} scenarios"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
