"""Generate the preregistered descriptive analysis from a Phase 4 master CSV.

The module deliberately accepts its input and output locations as arguments.
Public-facing prose can therefore refer to stable conceptual artifact IDs
without depending on the repository's current directory layout or script name.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

from scripts.analysis_units import (
    DEFAULT_SCENARIO_IDS,
    DEFAULT_TOOLS,
    ObservationStatus,
)
from scripts.evaluation_metrics import load_text_tree


COMPLETED_STATUSES = {
    ObservationStatus.COMPLETED_CLEAN.value,
    ObservationStatus.COMPLETED_CONFLICTED.value,
}
STATUS_ORDER = tuple(status.value for status in ObservationStatus)
MAPPING_ORDER = ("1:1", "1:N", "N:N")
CHANGE_TYPE_ORDER = ("structural", "behavioral")
METRICS = ("precision", "recall", "f1_score", "sequence_agreement")
EXPECTED_KEYS = {
    (tool, scenario)
    for tool in DEFAULT_TOOLS
    for scenario in DEFAULT_SCENARIO_IDS
}
REQUIRED_FIELDS = {
    "tool_name",
    "scenario_id",
    "mapping",
    "change_type",
    "execution_status",
    "true_positives",
    "false_positives",
    "false_negatives",
    "precision",
    "recall",
    "f1_score",
    "sequence_agreement",
    "exact_oracle_match",
    "syntactic_valid",
    "complete_textual_resolution",
}
DIFF_EXAMPLE_KEYS = {
    ("FSTMerge", "scenario_1"): "clean output with two extra file paths and high FP",
    ("FSTMerge", "scenario_5"): "readable empty output with undefined precision and F1",
    ("FSTMerge", "scenario_26"): "lowest-precision structural output with missing and extra paths",
    ("IntelliMerge", "scenario_6"): "complete exact textual resolution",
    ("IntelliMerge", "scenario_23"): "conflicted output with four missing paths",
    ("IntelliMerge", "scenario_38"): "conflicted behavioral output in the high-risk sample",
    ("JDime", "scenario_5"): "readable empty structured output",
}


class AnalysisError(ValueError):
    """Raised when a master dataset cannot support the frozen analysis."""


def read_master(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = set(reader.fieldnames or ())
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            raise AnalysisError(f"master dataset is missing fields: {missing}")
        rows = list(reader)
    validate_master(rows)
    return rows


def validate_master(rows: Sequence[Mapping[str, str]]) -> None:
    if len(rows) != 117:
        raise AnalysisError(f"master dataset must contain 117 rows; found {len(rows)}")
    keys = [(row.get("tool_name", ""), row.get("scenario_id", "")) for row in rows]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    if duplicates:
        raise AnalysisError(f"master dataset has duplicate keys: {duplicates[:5]}")
    missing = sorted(EXPECTED_KEYS - set(keys))
    unexpected = sorted(set(keys) - EXPECTED_KEYS)
    if missing or unexpected:
        raise AnalysisError(
            f"master matrix mismatch: {len(missing)} missing, "
            f"{len(unexpected)} unexpected"
        )
    for row in rows:
        key = f"{row['tool_name']}/{row['scenario_id']}"
        if row.get("execution_status") not in STATUS_ORDER:
            raise AnalysisError(f"{key}: unknown execution status")
        if row.get("mapping") not in MAPPING_ORDER:
            raise AnalysisError(f"{key}: unknown mapping")
        if row.get("change_type") not in CHANGE_TYPE_ORDER:
            raise AnalysisError(f"{key}: unknown change type")
        completed = row["execution_status"] in COMPLETED_STATUSES
        counts = tuple(row.get(field, "") for field in (
            "true_positives", "false_positives", "false_negatives"
        ))
        if completed and any(value == "" for value in counts):
            raise AnalysisError(f"{key}: completed output has no TP/FP/FN")
        if not completed and any(value != "" for value in counts):
            raise AnalysisError(f"{key}: unavailable output has TP/FP/FN")
        if completed:
            try:
                tp, fp, fn = (int(value) for value in counts)
            except ValueError as error:
                raise AnalysisError(f"{key}: TP/FP/FN must be integers") from error
            if min(tp, fp, fn) < 0:
                raise AnalysisError(f"{key}: TP/FP/FN must be non-negative")
            expected_precision = _ratio(tp, tp + fp)
            expected_recall = _ratio(tp, tp + fn)
            expected_f1 = (
                None
                if expected_precision is None or expected_recall is None
                else 0.0
                if expected_precision + expected_recall == 0
                else 2 * expected_precision * expected_recall
                / (expected_precision + expected_recall)
            )
            for field, expected in (
                ("precision", expected_precision),
                ("recall", expected_recall),
                ("f1_score", expected_f1),
            ):
                observed = _float(row, field)
                if observed is None or expected is None:
                    consistent = observed is expected
                else:
                    consistent = math.isclose(
                        observed, expected, rel_tol=1e-9, abs_tol=1e-12
                    )
                if not consistent:
                    raise AnalysisError(f"{key}: {field} is inconsistent with TP/FP/FN")
            sequence = _float(row, "sequence_agreement")
            if sequence is None or not 0.0 <= sequence <= 1.0:
                raise AnalysisError(f"{key}: sequence agreement must be in [0, 1]")
        else:
            populated_metrics = [
                field for field in METRICS if row.get(field, "") != ""
            ]
            if populated_metrics:
                raise AnalysisError(
                    f"{key}: unavailable output has populated metrics: "
                    f"{populated_metrics}"
                )


def _float(row: Mapping[str, str], field: str) -> float | None:
    value = row.get(field, "")
    return None if value == "" else float(value)


def _bool(row: Mapping[str, str], field: str) -> bool:
    return row.get(field) == "True"


def _ratio(numerator: int | float, denominator: int | float) -> float | None:
    return numerator / denominator if denominator else None


def _quantile(values: Sequence[float], probability: float) -> float | None:
    """Linear quantile using the (n - 1) index convention."""

    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _distribution(values: Sequence[float], prefix: str) -> dict[str, int | float | None]:
    return {
        f"{prefix}_n": len(values),
        f"{prefix}_mean": statistics.fmean(values) if values else None,
        f"{prefix}_median": statistics.median(values) if values else None,
        f"{prefix}_sample_sd": statistics.stdev(values) if len(values) > 1 else None,
        f"{prefix}_min": min(values) if values else None,
        f"{prefix}_q1": _quantile(values, 0.25),
        f"{prefix}_q3": _quantile(values, 0.75),
        f"{prefix}_max": max(values) if values else None,
    }


def summarize_subset(rows: Sequence[Mapping[str, str]]) -> dict[str, int | float | None]:
    if not rows:
        raise AnalysisError("cannot summarize an empty declared subset")
    total = len(rows)
    applicable = [row for row in rows if row["execution_status"] in COMPLETED_STATUSES]
    result: dict[str, int | float | None] = {
        "expected_n": total,
        "applicable_n": len(applicable),
        "unavailable_n": total - len(applicable),
    }
    for status in STATUS_ORDER:
        count = sum(row["execution_status"] == status for row in rows)
        result[f"status_{status}_n"] = count
        result[f"status_{status}_rate"] = count / total

    for metric in METRICS:
        values = [
            value for row in applicable
            if (value := _float(row, metric)) is not None
        ]
        result.update(_distribution(values, f"macro_{metric}"))

    tp = sum(int(row["true_positives"]) for row in applicable)
    fp = sum(int(row["false_positives"]) for row in applicable)
    fn = sum(int(row["false_negatives"]) for row in applicable)
    micro_precision = _ratio(tp, tp + fp)
    micro_recall = _ratio(tp, tp + fn)
    micro_f1 = (
        None
        if micro_precision is None or micro_recall is None
        else 0.0
        if micro_precision + micro_recall == 0
        else 2 * micro_precision * micro_recall / (micro_precision + micro_recall)
    )
    result.update(
        micro_true_positives=tp,
        micro_false_positives=fp,
        micro_false_negatives=fn,
        micro_precision=micro_precision,
        micro_recall=micro_recall,
        micro_f1_score=micro_f1,
        exact_oracle_match_n=sum(_bool(row, "exact_oracle_match") for row in rows),
        exact_oracle_match_rate=sum(_bool(row, "exact_oracle_match") for row in rows) / total,
        complete_textual_resolution_n=sum(
            _bool(row, "complete_textual_resolution") for row in rows
        ),
        complete_textual_resolution_rate=sum(
            _bool(row, "complete_textual_resolution") for row in rows
        ) / total,
        end_to_end_f1_zero_unavailable=sum(
            _float(row, "f1_score") or 0.0 for row in rows
        ) / total,
    )
    return result


def _scenario_number(scenario_id: str) -> int:
    return int(scenario_id.rsplit("_", 1)[1])


def build_tables(rows: Sequence[Mapping[str, str]]) -> dict[str, list[dict]]:
    validate_master(rows)
    by_key = {(row["tool_name"], row["scenario_id"]): row for row in rows}

    tool_summary: list[dict] = []
    for tool in DEFAULT_TOOLS:
        subset = [row for row in rows if row["tool_name"] == tool]
        tool_summary.append({"tool_name": tool, **summarize_subset(subset)})

    stratum_summary: list[dict] = []
    for tool in DEFAULT_TOOLS:
        for mapping in MAPPING_ORDER:
            for change_type in CHANGE_TYPE_ORDER:
                subset = [
                    row for row in rows
                    if row["tool_name"] == tool
                    and row["mapping"] == mapping
                    and row["change_type"] == change_type
                ]
                stratum_summary.append(
                    {
                        "tool_name": tool,
                        "mapping": mapping,
                        "change_type": change_type,
                        **summarize_subset(subset),
                    }
                )

    status_by_mapping: list[dict] = []
    for tool in DEFAULT_TOOLS:
        for mapping in MAPPING_ORDER:
            subset = [
                row for row in rows
                if row["tool_name"] == tool and row["mapping"] == mapping
            ]
            summary = summarize_subset(subset)
            record = {"tool_name": tool, "mapping": mapping, "expected_n": len(subset)}
            for status in STATUS_ORDER:
                record[f"status_{status}_n"] = summary[f"status_{status}_n"]
                record[f"status_{status}_rate"] = summary[f"status_{status}_rate"]
            status_by_mapping.append(record)

    matrix: list[dict] = []
    for scenario in sorted(DEFAULT_SCENARIO_IDS, key=_scenario_number):
        exemplar = by_key[(DEFAULT_TOOLS[0], scenario)]
        record: dict[str, str | int | float | None] = {
            "scenario_id": scenario,
            "scenario_number": _scenario_number(scenario),
            "mapping": exemplar["mapping"],
            "change_type": exemplar["change_type"],
        }
        for tool in DEFAULT_TOOLS:
            row = by_key[(tool, scenario)]
            prefix = tool.lower()
            record[f"{prefix}_status"] = row["execution_status"]
            record[f"{prefix}_precision"] = _float(row, "precision")
            record[f"{prefix}_recall"] = _float(row, "recall")
            record[f"{prefix}_f1_score"] = _float(row, "f1_score")
            record[f"{prefix}_sequence_agreement"] = _float(row, "sequence_agreement")
            record[f"{prefix}_exact_oracle_match"] = _bool(row, "exact_oracle_match")
            record[f"{prefix}_syntactic_valid"] = (
                None if row.get("syntactic_valid", "") == ""
                else _bool(row, "syntactic_valid")
            )
            record[f"{prefix}_complete_textual_resolution"] = _bool(
                row, "complete_textual_resolution"
            )
        matrix.append(record)

    completed_rows = [
        row for row in rows if row["execution_status"] in COMPLETED_STATUSES
    ]
    rounded_counts = Counter(
        f"{value:.2f}"
        for row in completed_rows
        if (value := _float(row, "f1_score")) is not None
    )
    score_decomposition: list[dict] = []
    for row in sorted(
        completed_rows,
        key=lambda item: (
            DEFAULT_TOOLS.index(item["tool_name"]),
            _scenario_number(item["scenario_id"]),
        ),
    ):
        f1 = _float(row, "f1_score")
        rounded = None if f1 is None else f"{f1:.2f}"
        score_decomposition.append(
            {
                "tool_name": row["tool_name"],
                "scenario_id": row["scenario_id"],
                "mapping": row["mapping"],
                "change_type": row["change_type"],
                "execution_status": row["execution_status"],
                "true_positives": int(row["true_positives"]),
                "false_positives": int(row["false_positives"]),
                "false_negatives": int(row["false_negatives"]),
                "precision": _float(row, "precision"),
                "recall": _float(row, "recall"),
                "f1_score": f1,
                "f1_rounded_2": rounded,
                "rounded_score_cell_count": 0 if rounded is None else rounded_counts[rounded],
                "missing_files": row.get("missing_files", ""),
                "extra_files": row.get("extra_files", ""),
                "exact_oracle_match": _bool(row, "exact_oracle_match"),
                "complete_textual_resolution": _bool(
                    row, "complete_textual_resolution"
                ),
            }
        )

    recurring_scores: list[dict] = []
    for rounded, count in sorted(
        rounded_counts.items(), key=lambda item: (-item[1], float(item[0]))
    ):
        if count < 2:
            continue
        members = [
            row for row in score_decomposition if row["f1_rounded_2"] == rounded
        ]
        recurring_scores.append(
            {
                "f1_rounded_2": rounded,
                "cell_count": count,
                "distinct_exact_f1_count": len(
                    {member["f1_score"] for member in members}
                ),
                "cells": ";".join(
                    f"{member['tool_name']}/{member['scenario_id']}"
                    for member in members
                ),
                "tp_fp_fn_decompositions": ";".join(
                    f"{member['true_positives']}/{member['false_positives']}/{member['false_negatives']}"
                    for member in members
                ),
            }
        )

    return {
        "tool_summary": tool_summary,
        "stratum_summary": stratum_summary,
        "status_by_mapping": status_by_mapping,
        "master_outcome_matrix": matrix,
        "score_decomposition": score_decomposition,
        "recurring_scores": recurring_scores,
    }


def _write_csv(path: Path, rows: Sequence[Mapping]) -> None:
    if not rows:
        raise AnalysisError(f"refusing to write empty table: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _counter(tree: Mapping[str, Sequence[str]]) -> Counter[tuple[str, str]]:
    return Counter(
        (path, line)
        for path, lines in tree.items()
        for line in lines
    )


def _line_examples(counter: Counter[tuple[str, str]], limit: int = 5) -> str:
    examples = []
    for (path, line), count in sorted(counter.items())[:limit]:
        examples.append(
            {
                "path": path,
                "line": line if len(line) <= 160 else line[:157] + "...",
                "multiplicity": count,
            }
        )
    return json.dumps(examples, ensure_ascii=False, separators=(",", ":"))


def build_diff_examples(
    rows: Sequence[Mapping[str, str]], run_root: Path, oracle_root: Path
) -> list[dict]:
    """Build logical line excerpts without exposing physical repository paths."""

    by_key = {(row["tool_name"], row["scenario_id"]): row for row in rows}
    examples = []
    for tool, scenario in sorted(
        DIFF_EXAMPLE_KEYS,
        key=lambda key: (DEFAULT_TOOLS.index(key[0]), _scenario_number(key[1])),
    ):
        row = by_key[(tool, scenario)]
        if row["execution_status"] not in COMPLETED_STATUSES:
            raise AnalysisError(f"diff example is not readable: {tool}/{scenario}")
        expected_dir = oracle_root / tool / "expected" / scenario
        actual_dir = run_root / "attempts" / tool / scenario / "normalized_output"
        try:
            expected = load_text_tree(expected_dir)
            actual = load_text_tree(actual_dir)
        except (OSError, UnicodeError) as error:
            raise AnalysisError(
                f"cannot load retained diff evidence for {tool}/{scenario}: {error}"
            ) from error
        expected_counter = _counter(expected)
        actual_counter = _counter(actual)
        missing = expected_counter - actual_counter
        extra = actual_counter - expected_counter
        examples.append(
            {
                "tool_name": tool,
                "scenario_id": scenario,
                "selection_reason": DIFF_EXAMPLE_KEYS[(tool, scenario)],
                "execution_status": row["execution_status"],
                "true_positives": int(row["true_positives"]),
                "false_positives": int(row["false_positives"]),
                "false_negatives": int(row["false_negatives"]),
                "precision": _float(row, "precision"),
                "recall": _float(row, "recall"),
                "f1_score": _float(row, "f1_score"),
                "missing_file_paths": row.get("missing_files", ""),
                "extra_file_paths": row.get("extra_files", ""),
                "missing_line_examples_json": _line_examples(missing),
                "extra_line_examples_json": _line_examples(extra),
                "exact_oracle_match": _bool(row, "exact_oracle_match"),
                "complete_textual_resolution": _bool(
                    row, "complete_textual_resolution"
                ),
            }
        )
    return examples


def _format_percent(value: float | None) -> str:
    return "N/D" if value is None else f"{100 * value:.2f}%"


def _markdown_report(tables: Mapping[str, Sequence[Mapping]]) -> str:
    tools = {row["tool_name"]: row for row in tables["tool_summary"]}
    lines = [
        "# Phase 5 descriptive analysis",
        "",
        "This report is generated from the released 117-observation canonical dataset.",
        "Artifact names and repository paths are intentionally not part of the study's",
        "scientific claims; the manuscript should cite the replication package and stable",
        "table/figure identifiers instead.",
        "",
        "## Overall results",
        "",
        "| Tool | Applicable | Macro precision | Macro recall | Macro F1 | Micro F1 | End-to-end F1 | Complete |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for tool in DEFAULT_TOOLS:
        row = tools[tool]
        lines.append(
            f"| {tool} | {row['applicable_n']}/{row['expected_n']} | "
            f"{_format_percent(row['macro_precision_mean'])} | "
            f"{_format_percent(row['macro_recall_mean'])} | "
            f"{_format_percent(row['macro_f1_score_mean'])} | "
            f"{_format_percent(row['micro_f1_score'])} | "
            f"{_format_percent(row['end_to_end_f1_zero_unavailable'])} | "
            f"{row['complete_textual_resolution_n']}/{row['expected_n']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundaries",
            "",
            "- Macro conformance describes quality only where a readable output exists.",
            "- Micro scores pool TP/FP/FN and are secondary to scenario-level results.",
            "- End-to-end F1 assigns zero to unavailable outputs and is a sensitivity measure.",
            "- A clean execution is not equivalent to exact oracle conformance.",
            "- Syntax evidence is not compilation, testing, semantic, or behavioral evidence.",
            "- The benchmark is controlled and synthetic; claims do not generalize directly to mined projects.",
            "",
        ]
    )
    return "\n".join(lines)


def _save_figures(rows: Sequence[Mapping[str, str]], tables: Mapping[str, Sequence[Mapping]], output_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

    # One stable methodological figure replaces the two overlapping process
    # diagrams formerly maintained by hand in the manuscript.
    fig, ax = plt.subplots(figsize=(13.8, 4.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = (
        (0.015, 0.39, 0.14, 0.27, "Controlled inputs\n39 scenarios\nbase / left / right / oracle", "#e8f1fa"),
        (0.185, 0.39, 0.14, 0.27, "Isolated execution\n3 tools x 39 scenarios\nfrozen configuration", "#e8f1fa"),
        (0.355, 0.39, 0.14, 0.27, "Terminal state\nclean / conflicted / invalid\ncrash / timeout / setup error", "#fff2cc"),
        (0.535, 0.57, 0.16, 0.27, "Readable tree\nnormalization and\noracle comparison", "#e2f0d9"),
        (0.535, 0.12, 0.16, 0.21, "Unavailable output\nstate retained; no primary\nconformance score", "#f4cccc"),
        (0.735, 0.39, 0.12, 0.27, "Canonical dataset\n117 observations\nwith provenance", "#d9eaf7"),
        (0.885, 0.39, 0.10, 0.27, "Regenerated\ntables, figures,\nand checks", "#eadcf8"),
    )
    for x, y, width, height, label, color in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), width, height,
                boxstyle="round,pad=0.012,rounding_size=0.015",
                linewidth=1.1, edgecolor="#4d4d4d", facecolor=color,
            )
        )
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=8.5)

    def arrow(start, end, *, dashed=False):
        ax.add_patch(
            FancyArrowPatch(
                start, end, arrowstyle="-|>", mutation_scale=12,
                linewidth=1.25, color="#4d4d4d",
                linestyle="--" if dashed else "-",
                connectionstyle="arc3,rad=0.0",
            )
        )

    arrow((0.155, 0.525), (0.185, 0.525))
    arrow((0.325, 0.525), (0.355, 0.525))
    arrow((0.495, 0.56), (0.535, 0.68))
    arrow((0.495, 0.47), (0.535, 0.225), dashed=True)
    arrow((0.695, 0.68), (0.735, 0.55))
    arrow((0.695, 0.225), (0.735, 0.45), dashed=True)
    arrow((0.855, 0.525), (0.885, 0.525))
    ax.text(0.505, 0.69, "readable", ha="center", va="bottom", fontsize=8, color="#3d6b35")
    ax.text(0.505, 0.25, "unavailable", ha="center", va="top", fontsize=8, color="#9c2f2f")
    ax.set_title("Controlled execution, assessment, and evidence flow", fontsize=13, pad=12)
    _save_figure(fig, output_dir / "figure_method_flow")

    by_key = {(row["tool_name"], row["scenario_id"]): row for row in rows}
    scenarios = sorted(DEFAULT_SCENARIO_IDS, key=_scenario_number)
    heat = np.full((len(scenarios), len(DEFAULT_TOOLS)), np.nan)
    annotations: dict[tuple[int, int], str] = {}
    for i, scenario in enumerate(scenarios):
        for j, tool in enumerate(DEFAULT_TOOLS):
            row = by_key[(tool, scenario)]
            value = _float(row, "f1_score")
            if value is not None:
                heat[i, j] = value
            if row["execution_status"] == ObservationStatus.INVALID_OUTPUT.value:
                annotations[(i, j)] = "I"
            elif value is None:
                annotations[(i, j)] = "E"
            elif row["execution_status"] == ObservationStatus.COMPLETED_CONFLICTED.value:
                annotations[(i, j)] = "C"
            elif _bool(row, "complete_textual_resolution"):
                annotations[(i, j)] = "R"

    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#bdbdbd")
    fig, ax = plt.subplots(figsize=(6.8, 12.0))
    image = ax.imshow(heat, vmin=0, vmax=1, aspect="auto", cmap=cmap)
    ax.set_xticks(range(len(DEFAULT_TOOLS)), DEFAULT_TOOLS)
    ax.set_yticks(range(len(scenarios)), [str(_scenario_number(s)) for s in scenarios])
    ax.set_xlabel("Merge tool")
    ax.set_ylabel("Scenario")
    ax.set_title("Scenario-level content F1 and terminal outcome")
    for (i, j), label in annotations.items():
        ax.text(j, i, label, ha="center", va="center", fontsize=7,
                color="white" if label == "I" else "black", fontweight="bold")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.04)
    colorbar.set_label("Content F1")
    ax.legend(
        handles=[
            Patch(facecolor="#bdbdbd", label="I: invalid output / E: readable empty"),
            Patch(facecolor="#66c2a5", label="C: conflicted output / R: complete resolution"),
        ],
        loc="upper center", bbox_to_anchor=(0.5, -0.045), frameon=False, fontsize=8,
    )
    fig.tight_layout()
    _save_figure(fig, output_dir / "figure_outcome_heatmap")

    status_rows = tables["status_by_mapping"]
    labels = [f"{tool}\n{mapping}" for tool in DEFAULT_TOOLS for mapping in MAPPING_ORDER]
    positions = np.arange(len(labels))
    colors = {
        ObservationStatus.COMPLETED_CLEAN.value: "#2ca25f",
        ObservationStatus.COMPLETED_CONFLICTED.value: "#fec44f",
        ObservationStatus.INVALID_OUTPUT.value: "#de2d26",
        ObservationStatus.CRASH.value: "#756bb1",
        ObservationStatus.TIMEOUT.value: "#636363",
        ObservationStatus.SETUP_ERROR.value: "#9ecae1",
    }
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    bottom = np.zeros(len(labels))
    for status in STATUS_ORDER:
        values = np.array([row[f"status_{status}_n"] for row in status_rows])
        ax.bar(positions, values, bottom=bottom, label=status.replace("_", " "), color=colors[status])
        bottom += values
    ax.set_xticks(positions, labels)
    ax.set_ylabel("Scenarios")
    ax.set_title("Execution outcomes by tool and mapping")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.14), frameon=False)
    ax.set_ylim(0, max(bottom) + 1)
    fig.tight_layout()
    _save_figure(fig, output_dir / "figure_execution_status")

    fig, axes = plt.subplots(1, len(MAPPING_ORDER), figsize=(12.5, 4.8), sharey=True)
    rng = np.random.default_rng(20260814)
    for axis, mapping in zip(axes, MAPPING_ORDER):
        for tool_index, tool in enumerate(DEFAULT_TOOLS):
            values = [
                value for row in rows
                if row["tool_name"] == tool and row["mapping"] == mapping
                if (value := _float(row, "f1_score")) is not None
            ]
            jitter = rng.uniform(-0.10, 0.10, size=len(values))
            axis.scatter(
                np.full(len(values), tool_index) + jitter,
                values,
                alpha=0.75,
                s=28,
                color="#3182bd",
                edgecolor="white",
                linewidth=0.4,
            )
            if values:
                axis.scatter(tool_index, statistics.median(values), marker="_", s=360,
                             linewidth=3, color="#cb181d", zorder=4)
            axis.text(tool_index, 1.035, f"n={len(values)}", ha="center", va="bottom", fontsize=8)
        axis.set_xticks(range(len(DEFAULT_TOOLS)), DEFAULT_TOOLS, rotation=20, ha="right")
        axis.set_title(f"Mapping {mapping}")
        axis.set_ylim(-0.04, 1.10)
        axis.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Scenario-level content F1")
    fig.suptitle("Applicable F1 distributions; red marker denotes median")
    fig.tight_layout()
    _save_figure(fig, output_dir / "figure_f1_distribution")


def _save_figure(figure, base_path: Path) -> None:
    figure.savefig(base_path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    figure.savefig(base_path.with_suffix(".pdf"), bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(figure)


def generate(
    master_path: Path,
    output_dir: Path,
    *,
    run_root: Path | None = None,
    oracle_root: Path | None = None,
    manuscript_assets: Path | None = None,
) -> dict:
    rows = read_master(master_path)
    tables = build_tables(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_names = {
        "table_tool_summary": "table_tool_summary.csv",
        "table_stratum_summary": "table_stratum_summary.csv",
        "table_status_by_mapping": "table_status_by_mapping.csv",
        "table_master_outcome_matrix": "table_master_outcome_matrix.csv",
        "table_score_decomposition": "table_score_decomposition.csv",
        "table_recurring_scores": "table_recurring_scores.csv",
    }
    if (run_root is None) != (oracle_root is None):
        raise AnalysisError("run_root and oracle_root must be supplied together")
    if run_root is not None and oracle_root is not None:
        tables["line_diff_examples"] = build_diff_examples(
            rows, run_root, oracle_root
        )
        artifact_names["table_line_diff_examples"] = "table_line_diff_examples.csv"
    for table_id, filename in artifact_names.items():
        _write_csv(output_dir / filename, tables[table_id.removeprefix("table_")])

    source_sha256 = hashlib.sha256(master_path.read_bytes()).hexdigest()
    summary = {
        "schema_version": 1,
        "analysis_id": "canonical_descriptive_analysis_v1",
        "source_sha256": source_sha256,
        "unit_of_analysis": "tool_name x scenario_id",
        "expected_observations": 117,
        "aggregation": {
            "primary": "macro distribution among defined applicable outputs",
            "secondary": "micro TP/FP/FN among applicable outputs",
            "sensitivity": "mean scenario F1 with unavailable or undefined F1 set to zero",
            "dispersion": "sample standard deviation and linear Q1/Q3",
            "missingness": "retained and reported; never silently discarded",
        },
        "artifact_ids": {
            **artifact_names,
            "figure_outcome_heatmap": ["figure_outcome_heatmap.png", "figure_outcome_heatmap.pdf"],
            "figure_execution_status": ["figure_execution_status.png", "figure_execution_status.pdf"],
            "figure_f1_distribution": ["figure_f1_distribution.png", "figure_f1_distribution.pdf"],
            "figure_method_flow": ["figure_method_flow.png", "figure_method_flow.pdf"],
            "descriptive_report": "phase5_descriptive_analysis.md",
        },
        "tool_summary": tables["tool_summary"],
    }
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "phase5_descriptive_analysis.md").write_text(
        _markdown_report(tables), encoding="utf-8"
    )
    _save_figures(rows, tables, output_dir)
    if manuscript_assets is not None:
        manuscript_assets.mkdir(parents=True, exist_ok=True)
        for stable_id, generated_name in (
            ("F0", "figure_method_flow.pdf"),
            ("F1", "figure_outcome_heatmap.pdf"),
            ("F2", "figure_execution_status.pdf"),
            ("F3", "figure_f1_distribution.pdf"),
        ):
            shutil.copyfile(
                output_dir / generated_name,
                manuscript_assets / f"{stable_id}.pdf",
            )
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master_csv", type=Path, help="Released 117-row master result CSV")
    parser.add_argument("output_dir", type=Path, help="Destination for generated analysis artifacts")
    parser.add_argument(
        "--run-root", type=Path,
        help="Optional retained canonical run root used for logical diff excerpts",
    )
    parser.add_argument(
        "--oracle-root", type=Path,
        help="Optional accepted oracle root used with --run-root",
    )
    parser.add_argument(
        "--manuscript-assets", type=Path,
        help="Optional destination for stable F0/F1/F2/F3 vector figure assets",
    )
    args = parser.parse_args(argv)
    try:
        summary = generate(
            args.master_csv,
            args.output_dir,
            run_root=args.run_root,
            oracle_root=args.oracle_root,
            manuscript_assets=args.manuscript_assets,
        )
    except (OSError, AnalysisError, ValueError) as error:
        parser.error(str(error))
    print(
        f"PHASE 5 DESCRIPTIVE ANALYSIS: generated "
        f"{len(summary['artifact_ids'])} conceptual artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
