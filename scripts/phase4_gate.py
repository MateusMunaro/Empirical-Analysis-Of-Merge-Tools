"""Integrity gate for a Phase 4 experimental run directory."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

from scripts.analysis_units import (
    DEFAULT_SCENARIO_IDS,
    DEFAULT_TOOLS,
    ObservationStatus,
)


EXPECTED_KEYS = {
    (tool, scenario) for tool in DEFAULT_TOOLS for scenario in DEFAULT_SCENARIO_IDS
}
HIGH_RISK_SCENARIOS = (
    "scenario_1", "scenario_5", "scenario_6", "scenario_10", "scenario_11",
    "scenario_17", "scenario_23", "scenario_30", "scenario_38",
)
HIGH_RISK_KEYS = {
    (tool, scenario) for tool in DEFAULT_TOOLS for scenario in HIGH_RISK_SCENARIOS
}
COMPLETED = {
    ObservationStatus.COMPLETED_CLEAN.value,
    ObservationStatus.COMPLETED_CONFLICTED.value,
}
VALID_STATUSES = {status.value for status in ObservationStatus}
METRIC_FIELDS = (
    "expected_file_count", "actual_file_count", "expected_line_count",
    "actual_line_count", "true_positives", "false_positives",
    "false_negatives", "sequence_agreement", "exact_oracle_match",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    try:
        # utf-8-sig also accepts ordinary UTF-8 and strips a BOM emitted by
        # spreadsheet/PowerShell workflows before the first quoted header.
        with path.open(encoding="utf-8-sig", newline="") as source:
            return list(csv.DictReader(source)), []
    except OSError as error:
        return [], [f"cannot read {path.name}: {error}"]


def _key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("tool_name", ""), row.get("scenario_id", "")


def _keys_issues(label: str, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    keys = [_key(row) for row in rows]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    missing = sorted(EXPECTED_KEYS - set(keys))
    unexpected = sorted(set(keys) - EXPECTED_KEYS)
    if len(rows) != 117:
        issues.append(f"{label} must contain 117 records; found {len(rows)}")
    if duplicates:
        issues.append(f"{label} has duplicate keys: {duplicates[:5]}")
    if missing:
        issues.append(f"{label} is missing {len(missing)} expected keys")
    if unexpected:
        issues.append(f"{label} has unexpected keys: {unexpected[:5]}")
    return issues


def _float(value: str) -> float | None:
    try:
        return float(value) if value != "" else None
    except ValueError:
        return None


def _close(observed: float | None, expected: float | None) -> bool:
    if observed is None or expected is None:
        return observed is expected
    return math.isclose(observed, expected, rel_tol=1e-9, abs_tol=1e-12)


def _metric_issues(row: dict[str, str]) -> list[str]:
    key = f"{row.get('tool_name')}/{row.get('scenario_id')}"
    status = row.get("execution_status", "")
    issues: list[str] = []
    if status not in COMPLETED:
        populated = [field for field in METRIC_FIELDS if row.get(field, "") != ""]
        if populated:
            issues.append(f"{key}: metrics populated for non-completed status")
        return issues
    missing = [field for field in METRIC_FIELDS if row.get(field, "") == ""]
    if missing:
        issues.append(f"{key}: completed result has missing metrics: {missing}")
        return issues
    try:
        expected_lines = int(row["expected_line_count"])
        actual_lines = int(row["actual_line_count"])
        tp = int(row["true_positives"])
        fp = int(row["false_positives"])
        fn = int(row["false_negatives"])
    except ValueError:
        return [f"{key}: count metric is not an integer"]
    if expected_lines != tp + fn:
        issues.append(f"{key}: expected_line_count != TP + FN")
    if actual_lines != tp + fp:
        issues.append(f"{key}: actual_line_count != TP + FP")
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (
        None if precision is None or recall is None
        else 0.0 if precision + recall == 0
        else 2 * precision * recall / (precision + recall)
    )
    for field, expected in (("precision", precision), ("recall", recall), ("f1_score", f1)):
        if not _close(_float(row[field]), expected):
            issues.append(f"{key}: {field} is inconsistent with TP/FP/FN")
    sequence = _float(row["sequence_agreement"])
    if sequence is None or not 0.0 <= sequence <= 1.0:
        issues.append(f"{key}: sequence_agreement must be in [0, 1]")
    exact = row["exact_oracle_match"] == "True"
    complete = row.get("complete_textual_resolution") == "True"
    syntax = row.get("syntactic_valid") == "True"
    if complete and not (
        status == ObservationStatus.COMPLETED_CLEAN.value and exact and syntax
    ):
        issues.append(f"{key}: complete resolution violates the frozen definition")
    return issues


def _final_audit_issues(
    run_dir: Path, results: list[dict[str, str]]
) -> list[str]:
    issues: list[str] = []
    audit, read_issues = _read_csv(run_dir / "manual_audit.csv")
    if read_issues:
        return read_issues
    audit_keys = [_key(row) for row in audit]
    duplicate_audit_keys = sorted(
        key for key, count in Counter(audit_keys).items() if count > 1
    )
    unexpected_audit_keys = sorted(set(audit_keys) - EXPECTED_KEYS)
    if duplicate_audit_keys:
        issues.append(
            f"manual audit has duplicate keys: {duplicate_audit_keys[:5]}"
        )
    if unexpected_audit_keys:
        issues.append(
            f"manual audit has unexpected keys: {unexpected_audit_keys[:5]}"
        )
    audit_by_key = {_key(row): row for row in audit}
    required_boundary_keys = {
        _key(row) for row in results
        if row.get("execution_status") != ObservationStatus.COMPLETED_CLEAN.value
        or row.get("exact_oracle_match") == "True"
        or row.get("syntactic_valid") == "False"
    }
    missing_boundary = sorted(required_boundary_keys - set(audit_by_key))
    if missing_boundary:
        issues.append(
            f"manual audit is missing {len(missing_boundary)} boundary/unexpected cells"
        )
    results_by_key = {_key(row): row for row in results}
    audited_strata = {
        (key[0], results_by_key[key]["mapping"], results_by_key[key]["change_type"])
        for key in audit_by_key
        if key in results_by_key
    }
    required_strata = {
        (row["tool_name"], row["mapping"], row["change_type"])
        for row in results
    }
    if required_strata - audited_strata:
        issues.append("manual audit does not cover every tool/mapping/change-type stratum")
    for key, row in audit_by_key.items():
        label = f"{key[0]}/{key[1]}"
        if row.get("audit_decision") != "evidence_consistent":
            issues.append(f"{label}: manual audit decision is not evidence_consistent")
        if not row.get("auditor_id", "").strip():
            issues.append(f"{label}: manual audit has no auditor provenance")
        if not row.get("audit_notes", "").strip():
            issues.append(f"{label}: manual audit has no notes")
        if not row.get("audited_at_utc", "").strip():
            issues.append(f"{label}: manual audit has no UTC timestamp")

    determinism, determinism_read_issues = _read_csv(
        run_dir / "determinism_high_risk.csv"
    )
    if determinism_read_issues:
        issues.extend(determinism_read_issues)
        return issues
    keys = [_key(row) for row in determinism]
    if len(keys) != len(set(keys)):
        issues.append("determinism evidence contains duplicate keys")
    if set(keys) != HIGH_RISK_KEYS:
        issues.append(
            "determinism evidence must contain the frozen 27-cell high-risk sample"
        )
    for row in determinism:
        if row.get("deterministic") != "True" or row.get("different_fields"):
            issues.append(
                f"{row.get('tool_name')}/{row.get('scenario_id')}: "
                "determinism comparison differs or is not adjudicated"
            )
    return issues


def phase4_issues(
    run_dir: Path, require_release: bool = True, require_final_audit: bool = False
) -> tuple[str, ...]:
    run_dir = run_dir.resolve()
    issues: list[str] = []
    invalidation_path = run_dir / "run_invalidation.json"
    if invalidation_path.is_file():
        issues.append("run has been explicitly invalidated; see run_invalidation.json")
    executions, execution_read_issues = _read_csv(run_dir / "executions.csv")
    results, result_read_issues = _read_csv(run_dir / "scenario_tool_results.csv")
    issues.extend(execution_read_issues)
    issues.extend(result_read_issues)
    if execution_read_issues or result_read_issues:
        return tuple(issues)
    issues.extend(_keys_issues("executions.csv", executions))
    issues.extend(_keys_issues("scenario_tool_results.csv", results))
    execution_by_key = {_key(row): row for row in executions}
    result_by_key = {_key(row): row for row in results}
    for key in sorted(set(execution_by_key) & set(result_by_key)):
        execution = execution_by_key[key]
        result = result_by_key[key]
        status = execution.get("execution_status", "")
        label = f"{key[0]}/{key[1]}"
        if status not in VALID_STATUSES:
            issues.append(f"{label}: invalid or empty execution status: {status!r}")
        if result.get("execution_status") != status:
            issues.append(f"{label}: execution status differs between CSV files")
        if not execution.get("status_detail", "").strip():
            issues.append(f"{label}: status_detail is empty")
        for field in ("tool_artifact_sha256", "oracle_checksum"):
            if not SHA256_PATTERN.fullmatch(execution.get(field, "")):
                issues.append(f"{label}: {field} is not a SHA-256 digest")
        try:
            inputs = json.loads(execution.get("input_checksums_json", ""))
            if set(inputs) != {"base", "left", "right"} or not all(
                isinstance(value, str) and SHA256_PATTERN.fullmatch(value)
                for value in inputs.values()
            ):
                raise ValueError
        except (json.JSONDecodeError, TypeError, ValueError):
            issues.append(f"{label}: input checksums are incomplete or invalid")
        if status in COMPLETED and not SHA256_PATTERN.fullmatch(
            execution.get("normalized_output_checksum", "")
        ):
            issues.append(f"{label}: completed output lacks normalized checksum")
        issues.extend(_metric_issues(result))
    metadata_path = run_dir / "run_metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        issues.append(f"cannot read run_metadata.json: {error}")
    else:
        if require_release and metadata.get("run_kind") != "canonical_release":
            issues.append("run is diagnostic, not a canonical release")
        if metadata.get("tools") != list(DEFAULT_TOOLS):
            issues.append("run metadata does not declare the frozen tool order")
        if metadata.get("scenarios") != list(DEFAULT_SCENARIO_IDS):
            issues.append("run metadata does not declare all 39 scenarios")
    if require_final_audit and not issues:
        issues.extend(_final_audit_issues(run_dir, results))
    return tuple(issues)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Phase 4 run")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--allow-diagnostic", action="store_true",
        help="Validate structure without requiring canonical_release metadata",
    )
    parser.add_argument(
        "--final", action="store_true",
        help="Also require completed manual-audit and determinism evidence",
    )
    args = parser.parse_args()
    if args.final and args.allow_diagnostic:
        parser.error("--final cannot be combined with --allow-diagnostic")
    issues = phase4_issues(
        args.run_dir, require_release=not args.allow_diagnostic,
        require_final_audit=args.final,
    )
    if issues:
        print(f"PHASE 4 GATE: BLOCKED ({len(issues)} issue(s))")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("PHASE 4 GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
