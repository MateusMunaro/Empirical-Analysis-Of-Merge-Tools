"""Canonical scenario metadata and replication-package integrity checks."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence

from scripts.core.analysis_units import (
    DEFAULT_SCENARIO_IDS,
    DEFAULT_TOOLS,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "data" / "scenario_manifest.csv"


class MappingComplexity(str, Enum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "N:N"


class ChangeType(str, Enum):
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"


class ScenarioOrigin(str, Enum):
    SYNTHETIC_CONTROLLED = "synthetic_controlled"
    REAL_PROJECT = "real_project"


class ClassificationStatus(str, Enum):
    PENDING_INDEPENDENT_REVIEW = "pending_independent_review"
    INDEPENDENTLY_CONFIRMED = "independently_confirmed"
    REQUIRES_REVISION = "requires_revision"


class ValidationScope(str, Enum):
    TEXTUAL_STRUCTURAL_ONLY = "textual_structural_only"
    BEHAVIORAL_EVIDENCE = "behavioral_evidence"


REQUIRED_COLUMNS = (
    "scenario_id",
    "title",
    "mapping",
    "change_type",
    "origin",
    "base_description",
    "left_description",
    "right_description",
    "merge_intent",
    "acceptance_criteria",
    "base_files",
    "left_files",
    "right_files",
    "expected_files",
    "artifact_file_count",
    "logical_element_count",
    "logical_elements",
    "dependency_scope",
    "validation_scope",
    "associated_tests",
    "mapping_basis",
    "change_type_basis",
    "oracle_review_status",
    "classification_status",
)


@dataclass(frozen=True)
class ScenarioMetadata:
    scenario_id: str
    title: str
    mapping: MappingComplexity
    change_type: ChangeType
    origin: ScenarioOrigin
    base_description: str
    left_description: str
    right_description: str
    merge_intent: str
    acceptance_criteria: str
    base_files: tuple[str, ...]
    left_files: tuple[str, ...]
    right_files: tuple[str, ...]
    expected_files: tuple[str, ...]
    artifact_file_count: int
    logical_element_count: int
    logical_elements: str
    dependency_scope: str
    validation_scope: ValidationScope
    associated_tests: str
    mapping_basis: str
    change_type_basis: str
    oracle_review_status: ClassificationStatus
    classification_status: ClassificationStatus


class ManifestValidationError(ValueError):
    """Raised when scenario metadata violates the declared study design."""


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> tuple[ScenarioMetadata, ...]:
    with path.open("r", encoding="utf-8", newline="") as manifest_file:
        reader = csv.DictReader(manifest_file)
        if reader.fieldnames is None:
            raise ManifestValidationError("Scenario manifest has no header")
        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in reader.fieldnames
        ]
        if missing_columns:
            raise ManifestValidationError(
                f"Scenario manifest is missing columns: {', '.join(missing_columns)}"
            )

        rows: list[ScenarioMetadata] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                rows.append(
                    ScenarioMetadata(
                        scenario_id=_required_text(row, "scenario_id", line_number),
                        title=_required_text(row, "title", line_number),
                        mapping=MappingComplexity(
                            _required_text(row, "mapping", line_number)
                        ),
                        change_type=ChangeType(
                            _required_text(row, "change_type", line_number)
                        ),
                        origin=ScenarioOrigin(
                            _required_text(row, "origin", line_number)
                        ),
                        base_description=_required_text(
                            row, "base_description", line_number
                        ),
                        left_description=_required_text(
                            row, "left_description", line_number
                        ),
                        right_description=_required_text(
                            row, "right_description", line_number
                        ),
                        merge_intent=_required_text(
                            row, "merge_intent", line_number
                        ),
                        acceptance_criteria=_required_text(
                            row, "acceptance_criteria", line_number
                        ),
                        base_files=_file_list(row, "base_files", line_number),
                        left_files=_file_list(row, "left_files", line_number),
                        right_files=_file_list(row, "right_files", line_number),
                        expected_files=_file_list(
                            row, "expected_files", line_number
                        ),
                        artifact_file_count=_positive_integer(
                            row, "artifact_file_count", line_number
                        ),
                        logical_element_count=_positive_integer(
                            row, "logical_element_count", line_number
                        ),
                        logical_elements=_required_text(
                            row, "logical_elements", line_number
                        ),
                        dependency_scope=_required_text(
                            row, "dependency_scope", line_number
                        ),
                        validation_scope=ValidationScope(
                            _required_text(row, "validation_scope", line_number)
                        ),
                        associated_tests=_required_text(
                            row, "associated_tests", line_number
                        ),
                        mapping_basis=_required_text(
                            row, "mapping_basis", line_number
                        ),
                        change_type_basis=_required_text(
                            row, "change_type_basis", line_number
                        ),
                        oracle_review_status=ClassificationStatus(
                            _required_text(
                                row, "oracle_review_status", line_number
                            )
                        ),
                        classification_status=ClassificationStatus(
                            _required_text(
                                row, "classification_status", line_number
                            )
                        ),
                    )
                )
            except ValueError as error:
                raise ManifestValidationError(
                    f"Invalid scenario manifest row {line_number}: {error}"
                ) from error

    validate_manifest(rows)
    return tuple(rows)


def validate_manifest(rows: Sequence[ScenarioMetadata]) -> None:
    scenario_ids = [row.scenario_id for row in rows]
    duplicates = sorted(
        scenario_id
        for scenario_id in set(scenario_ids)
        if scenario_ids.count(scenario_id) > 1
    )
    if duplicates:
        raise ManifestValidationError(
            f"Duplicate scenario IDs: {', '.join(duplicates)}"
        )

    expected = set(DEFAULT_SCENARIO_IDS)
    observed = set(scenario_ids)
    missing = sorted(expected - observed, key=_scenario_number)
    unexpected = sorted(observed - expected, key=_scenario_number)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing={','.join(missing)}")
        if unexpected:
            details.append(f"unexpected={','.join(unexpected)}")
        raise ManifestValidationError(
            "Manifest must contain exactly scenario_1 through scenario_39 ("
            + "; ".join(details)
            + ")"
        )

    for row in rows:
        artifact_files = (
            set(row.base_files)
            | set(row.left_files)
            | set(row.right_files)
            | set(row.expected_files)
        )
        if row.artifact_file_count != len(artifact_files):
            raise ManifestValidationError(
                f"{row.scenario_id}: artifact_file_count={row.artifact_file_count} "
                f"but {len(artifact_files)} distinct Java paths are declared"
            )
        if (
            row.validation_scope is ValidationScope.TEXTUAL_STRUCTURAL_ONLY
            and row.associated_tests != "not_applicable"
        ):
            raise ManifestValidationError(
                f"{row.scenario_id}: textual/structural scope must declare "
                "associated_tests=not_applicable"
            )
        if (
            row.validation_scope is ValidationScope.BEHAVIORAL_EVIDENCE
            and row.associated_tests == "not_applicable"
        ):
            raise ManifestValidationError(
                f"{row.scenario_id}: behavioral evidence requires associated tests"
            )


def audit_scenario_artifacts(
    rows: Sequence[ScenarioMetadata],
    repo_root: Path = REPO_ROOT,
    tools: Sequence[str] = DEFAULT_TOOLS,
) -> tuple[str, ...]:
    """Check that every declared scenario has non-empty inputs and an oracle."""

    issues: list[str] = []
    signatures: dict[tuple[str, str, str], tuple[tuple[str, str], ...]] = {}
    for tool_name in tools:
        for row in rows:
            input_root = (
                repo_root / "scenarios_base" / tool_name / row.scenario_id
            )
            for variant in ("base", "left", "right"):
                variant_dir = input_root / variant
                if not variant_dir.is_dir():
                    issues.append(
                        f"{tool_name}/{row.scenario_id}: missing {variant} directory"
                    )
                elif not _contains_java_file(variant_dir):
                    issues.append(
                        f"{tool_name}/{row.scenario_id}: {variant} has no Java file"
                    )
                else:
                    signatures[(tool_name, row.scenario_id, variant)] = (
                        _java_tree_signature(variant_dir)
                    )
                    declared_files = getattr(row, f"{variant}_files")
                    actual_files = _java_file_paths(variant_dir)
                    if actual_files != declared_files:
                        issues.append(
                            f"{tool_name}/{row.scenario_id}: declared {variant} "
                            f"files {declared_files} != actual {actual_files}"
                        )

            oracle_dir = (
                repo_root / "output" / tool_name / "expected" / row.scenario_id
            )
            if not oracle_dir.is_dir():
                issues.append(
                    f"{tool_name}/{row.scenario_id}: missing oracle directory"
                )
            elif not _contains_java_file(oracle_dir):
                issues.append(
                    f"{tool_name}/{row.scenario_id}: oracle has no Java file"
                )
            else:
                signatures[(tool_name, row.scenario_id, "oracle")] = (
                    _java_tree_signature(oracle_dir)
                )
                actual_expected_files = _java_file_paths(oracle_dir)
                if actual_expected_files != row.expected_files:
                    issues.append(
                        f"{tool_name}/{row.scenario_id}: declared expected files "
                        f"{row.expected_files} != actual {actual_expected_files}"
                    )

    for row in rows:
        for variant in ("base", "left", "right", "oracle"):
            available = {
                tool_name: signatures[(tool_name, row.scenario_id, variant)]
                for tool_name in tools
                if (tool_name, row.scenario_id, variant) in signatures
            }
            if len(available) != len(tools):
                continue
            reference_tool = tools[0]
            differing_tools = [
                tool_name
                for tool_name in tools[1:]
                if available[tool_name] != available[reference_tool]
            ]
            if differing_tools:
                issues.append(
                    f"{row.scenario_id}: {variant} differs between "
                    f"{reference_tool} and {', '.join(differing_tools)}"
                )
    return tuple(issues)


def _contains_java_file(directory: Path) -> bool:
    return any(path.is_file() for path in directory.rglob("*.java"))


def _java_file_paths(directory: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            path.relative_to(directory).as_posix()
            for path in directory.rglob("*.java")
            if path.is_file()
        )
    )


def _java_tree_signature(directory: Path) -> tuple[tuple[str, str], ...]:
    """Represent a Java tree independent of path case and line endings."""

    entries: list[tuple[str, str]] = []
    for path in sorted(
        directory.rglob("*.java"),
        key=lambda candidate: candidate.relative_to(directory).as_posix().lower(),
    ):
        relative_path = path.relative_to(directory).as_posix().lower()
        content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        entries.append((relative_path, content))
    return tuple(entries)


def _required_text(row: dict[str, str | None], column: str, line: int) -> str:
    value = row.get(column)
    if value is None or not value.strip():
        raise ValueError(f"column '{column}' is blank at line {line}")
    if value != value.strip():
        raise ValueError(
            f"column '{column}' has leading or trailing whitespace at line {line}"
        )
    return value


def _positive_integer(
    row: dict[str, str | None], column: str, line: int
) -> int:
    value = int(_required_text(row, column, line))
    if value < 1:
        raise ValueError(f"column '{column}' must be positive at line {line}")
    return value


def _file_list(
    row: dict[str, str | None], column: str, line: int
) -> tuple[str, ...]:
    serialized = _required_text(row, column, line)
    files = tuple(serialized.split(";"))
    if len(files) != len(set(files)):
        raise ValueError(f"column '{column}' contains duplicate paths at line {line}")
    for path in files:
        if not path.endswith(".java"):
            raise ValueError(
                f"column '{column}' contains a non-Java path at line {line}: {path}"
            )
        if path.startswith("/") or "\\" in path or ".." in path.split("/"):
            raise ValueError(
                f"column '{column}' contains an unsafe path at line {line}: {path}"
            )
    return files


def _scenario_number(scenario_id: str) -> int:
    try:
        return int(scenario_id.removeprefix("scenario_"))
    except ValueError:
        return 10**9


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the canonical scenario manifest and artifacts"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path to scenario_manifest.csv",
    )
    parser.add_argument(
        "--skip-artifact-audit",
        action="store_true",
        help="Validate metadata only",
    )
    args = parser.parse_args()

    rows = load_manifest(args.manifest)
    print(f"Manifest valid: {len(rows)} unique scenarios")

    if not args.skip_artifact_audit:
        issues = audit_scenario_artifacts(rows)
        if issues:
            print(f"Artifact audit failed with {len(issues)} issue(s):")
            for issue in issues:
                print(f"- {issue}")
            return 1
        print(
            f"Artifact audit valid: {len(DEFAULT_TOOLS) * len(rows)} "
            "tool-scenario input/oracle sets"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
