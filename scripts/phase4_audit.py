"""Prepare manual review and compare repeat runs for Phase 4."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from scripts.phase4_gate import HIGH_RISK_KEYS, phase4_issues


DETERMINISM_RESULT_FIELDS = (
    "execution_status", "expected_file_count", "actual_file_count",
    "missing_files", "extra_files", "expected_line_count", "actual_line_count",
    "true_positives", "false_positives", "false_negatives", "precision",
    "recall", "f1_score", "sequence_agreement", "exact_oracle_match",
    "syntactic_valid", "complete_textual_resolution",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite audit evidence: {path}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def prepare_manual_audit(run_dir: Path, output: Path) -> int:
    issues = phase4_issues(run_dir, require_release=True)
    if issues:
        raise ValueError("Phase 4 run is not eligible: " + "; ".join(issues))
    results = read_csv(run_dir / "scenario_tool_results.csv")
    executions = {
        (row["tool_name"], row["scenario_id"]): row
        for row in read_csv(run_dir / "executions.csv")
    }
    selected: dict[tuple[str, str], str] = {}
    strata_seen: set[tuple[str, str, str]] = set()
    for row in results:
        key = (row["tool_name"], row["scenario_id"])
        stratum = (row["tool_name"], row["mapping"], row["change_type"])
        if stratum not in strata_seen:
            selected[key] = "stratified_sample"
            strata_seen.add(stratum)
        boundary_reasons = []
        if row["execution_status"] != "completed_clean":
            boundary_reasons.append("non_clean_terminal_status")
        if row.get("exact_oracle_match") == "True":
            boundary_reasons.append("exact_match")
        if row.get("syntactic_valid") == "False":
            boundary_reasons.append("syntax_boundary")
        if boundary_reasons:
            selected[key] = ";".join(
                filter(None, [selected.get(key, ""), *boundary_reasons])
            )
    by_key = {(row["tool_name"], row["scenario_id"]): row for row in results}
    rows = []
    for key, reason in sorted(selected.items()):
        result = by_key[key]
        execution = executions[key]
        rows.append(
            {
                "tool_name": key[0],
                "scenario_id": key[1],
                "selection_reason": reason,
                "execution_status": result["execution_status"],
                "f1_score": result["f1_score"],
                "exact_oracle_match": result["exact_oracle_match"],
                "syntactic_valid": result["syntactic_valid"],
                "raw_output_checksum": execution["raw_output_checksum"],
                "normalized_output_checksum": execution["normalized_output_checksum"],
                "audit_decision": "",
                "auditor_id": "",
                "audit_notes": "",
                "audited_at_utc": "",
            }
        )
    fields = list(rows[0]) if rows else []
    write_csv(output, fields, rows)
    return len(rows)


def compare_runs(primary: Path, repeat: Path, output: Path) -> int:
    for label, run_dir in (("primary", primary), ("repeat", repeat)):
        issues = phase4_issues(run_dir, require_release=True)
        if issues:
            raise ValueError(f"{label} run is not eligible: " + "; ".join(issues))
    fields_to_compare = (
        "execution_status", "exit_code", "raw_output_checksum",
        "normalized_output_checksum", "oracle_checksum",
    )
    primary_rows = {
        (row["tool_name"], row["scenario_id"]): row
        for row in read_csv(primary / "executions.csv")
    }
    repeat_rows = {
        (row["tool_name"], row["scenario_id"]): row
        for row in read_csv(repeat / "executions.csv")
    }
    rows = []
    difference_count = 0
    for key in sorted(primary_rows):
        differences = [
            field for field in fields_to_compare
            if primary_rows[key].get(field) != repeat_rows[key].get(field)
        ]
        difference_count += bool(differences)
        rows.append(
            {
                "tool_name": key[0],
                "scenario_id": key[1],
                "deterministic": str(not differences),
                "different_fields": ";".join(differences),
                "primary_normalized_checksum": primary_rows[key].get(
                    "normalized_output_checksum", ""
                ),
                "repeat_normalized_checksum": repeat_rows[key].get(
                    "normalized_output_checksum", ""
                ),
                "adjudication": "" if differences else "not_required",
            }
        )
    write_csv(output, list(rows[0]), rows)
    return difference_count


def compare_sample(primary: Path, repeat: Path, output: Path) -> int:
    """Compare a diagnostic high-risk subset with a canonical primary run."""

    issues = phase4_issues(primary, require_release=True)
    if issues:
        raise ValueError("primary run is not eligible: " + "; ".join(issues))
    try:
        metadata = json.loads((repeat / "run_metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"repeat metadata cannot be read: {error}") from error
    if metadata.get("run_kind") != "diagnostic":
        raise ValueError("sample repeat must be marked diagnostic")
    declared_tools = metadata.get("tools")
    declared_scenarios = metadata.get("scenarios")
    if not isinstance(declared_tools, list) or not declared_tools:
        raise ValueError("sample repeat has no declared tools")
    if not isinstance(declared_scenarios, list) or not declared_scenarios:
        raise ValueError("sample repeat has no declared scenarios")
    expected_keys = {
        (tool, scenario) for tool in declared_tools for scenario in declared_scenarios
    }
    if expected_keys != HIGH_RISK_KEYS:
        raise ValueError("sample repeat is not the frozen 27-cell high-risk matrix")
    primary_executions = {
        (row["tool_name"], row["scenario_id"]): row
        for row in read_csv(primary / "executions.csv")
    }
    repeat_executions_list = read_csv(repeat / "executions.csv")
    repeat_executions = {
        (row["tool_name"], row["scenario_id"]): row
        for row in repeat_executions_list
    }
    if len(repeat_executions_list) != len(repeat_executions):
        raise ValueError("sample repeat contains duplicate execution keys")
    if set(repeat_executions) != expected_keys:
        raise ValueError("sample repeat keys do not match its declared matrix")
    if not expected_keys <= set(primary_executions):
        raise ValueError("sample repeat contains keys absent from the primary run")
    primary_results = {
        (row["tool_name"], row["scenario_id"]): row
        for row in read_csv(primary / "scenario_tool_results.csv")
    }
    repeat_results_list = read_csv(repeat / "scenario_tool_results.csv")
    repeat_results = {
        (row["tool_name"], row["scenario_id"]): row
        for row in repeat_results_list
    }
    if len(repeat_results_list) != len(repeat_results):
        raise ValueError("sample repeat contains duplicate result keys")
    if set(repeat_results) != expected_keys:
        raise ValueError("sample result keys do not match its declared matrix")

    rows = []
    difference_count = 0
    for key in sorted(expected_keys):
        primary_execution = primary_executions[key]
        repeat_execution = repeat_executions[key]
        primary_result = primary_results[key]
        repeat_result = repeat_results[key]
        differences = []
        for field in (
            "execution_status", "normalized_output_checksum", "oracle_checksum",
            "tool_artifact_sha256",
        ):
            if primary_execution.get(field) != repeat_execution.get(field):
                differences.append(f"execution.{field}")
        for field in DETERMINISM_RESULT_FIELDS:
            if primary_result.get(field) != repeat_result.get(field):
                differences.append(f"result.{field}")
        difference_count += bool(differences)
        rows.append(
            {
                "tool_name": key[0],
                "scenario_id": key[1],
                "deterministic": str(not differences),
                "different_fields": ";".join(differences),
                "raw_output_checksum_changed": str(
                    primary_execution.get("raw_output_checksum")
                    != repeat_execution.get("raw_output_checksum")
                ),
                "primary_status": primary_execution.get("execution_status", ""),
                "repeat_status": repeat_execution.get("execution_status", ""),
                "primary_normalized_checksum": primary_execution.get(
                    "normalized_output_checksum", ""
                ),
                "repeat_normalized_checksum": repeat_execution.get(
                    "normalized_output_checksum", ""
                ),
                "adjudication": "" if differences else "not_required",
            }
        )
    write_csv(output, list(rows[0]), rows)
    return difference_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    prepare = subparsers.add_parser("prepare", help="create stratified review form")
    prepare.add_argument("run_dir", type=Path)
    prepare.add_argument("--output", type=Path, required=True)
    compare = subparsers.add_parser("compare", help="compare two canonical runs")
    compare.add_argument("primary", type=Path)
    compare.add_argument("repeat", type=Path)
    compare.add_argument("--output", type=Path, required=True)
    sample = subparsers.add_parser(
        "compare-sample", help="compare a diagnostic subset with a canonical run"
    )
    sample.add_argument("primary", type=Path)
    sample.add_argument("repeat", type=Path)
    sample.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            count = prepare_manual_audit(args.run_dir.resolve(), args.output.resolve())
            print(f"Manual audit form created with {count} selected cells: {args.output}")
            return 0
        if args.action == "compare-sample":
            differences = compare_sample(
                args.primary.resolve(), args.repeat.resolve(), args.output.resolve()
            )
        else:
            differences = compare_runs(
                args.primary.resolve(), args.repeat.resolve(), args.output.resolve()
            )
        print(f"Determinism comparison created: {args.output}")
        if differences:
            print(f"BLOCKED: {differences} cell(s) differ and require adjudication")
            return 1
        print("PASS: no compared execution/output field differs")
        return 0
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
