"""Prepare manual review and compare repeat runs for Phase 4."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from scripts.phase4_gate import phase4_issues


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
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
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            count = prepare_manual_audit(args.run_dir.resolve(), args.output.resolve())
            print(f"Manual audit form created with {count} selected cells: {args.output}")
            return 0
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
