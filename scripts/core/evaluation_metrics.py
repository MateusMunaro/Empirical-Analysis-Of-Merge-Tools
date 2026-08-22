"""Normative metrics for the revised merge-tool experiment.

This module is the executable counterpart of ``PROTOCOL.md``.  It compares a
complete output tree with its oracle, preserving line multiplicity, file paths,
and line order.  The legacy evaluator is intentionally not imported here: it
uses sets of lines and a metric named ``accuracy`` that are incompatible with
the revised protocol.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from scripts.core.analysis_units import ObservationStatus


TreeLines = Mapping[str, Sequence[str]]
LineToken = tuple[str, str]


@dataclass(frozen=True)
class TreeMetrics:
    """Scenario-level comparison of an actual tree with an oracle tree."""

    expected_file_count: int
    actual_file_count: int
    missing_files: tuple[str, ...]
    extra_files: tuple[str, ...]
    expected_line_count: int
    actual_line_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float | None
    recall: float | None
    f1_score: float | None
    sequence_agreement: float
    exact_oracle_match: bool


def normalized_lines(text: str) -> tuple[str, ...]:
    """Apply the protocol's deliberately conservative text normalization.

    CRLF and lone CR become LF.  One terminal line separator is ignored so
    that platform newline conventions do not affect a score.  Blank lines,
    indentation, trailing whitespace, comments, and internal whitespace remain
    significant because changing them automatically can alter source text.
    """

    canonical = text.replace("\r\n", "\n").replace("\r", "\n")
    if canonical.endswith("\n"):
        canonical = canonical[:-1]
    if canonical == "":
        return ()
    return tuple(canonical.split("\n"))


def load_text_tree(root: Path) -> dict[str, tuple[str, ...]]:
    """Load every regular file below *root* using strict UTF-8 decoding.

    Relative POSIX paths are part of the comparison key.  A decoding failure is
    allowed to propagate so the caller can classify the execution as
    ``invalid_output`` rather than silently changing the content.
    """

    if not root.is_dir():
        raise NotADirectoryError(f"Tree root does not exist or is not a directory: {root}")

    tree: dict[str, tuple[str, ...]] = {}
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    for path in files:
        relative_path = path.relative_to(root).as_posix()
        tree[relative_path] = normalized_lines(path.read_text(encoding="utf-8"))
    return tree


def evaluate_trees(expected: TreeLines, actual: TreeLines) -> TreeMetrics:
    """Compare complete trees using path-aware line multisets and per-file LCS."""

    expected_tree = _canonical_tree(expected)
    actual_tree = _canonical_tree(actual)
    expected_paths = set(expected_tree)
    actual_paths = set(actual_tree)

    expected_counter = _line_counter(expected_tree)
    actual_counter = _line_counter(actual_tree)
    true_positives = sum((expected_counter & actual_counter).values())
    false_positives = sum((actual_counter - expected_counter).values())
    false_negatives = sum((expected_counter - actual_counter).values())

    precision = _safe_ratio(true_positives, true_positives + false_positives)
    recall = _safe_ratio(true_positives, true_positives + false_negatives)
    if precision is None or recall is None:
        f1_score = None
    elif precision + recall == 0:
        f1_score = 0.0
    else:
        f1_score = 2 * precision * recall / (precision + recall)

    expected_line_count = sum(len(lines) for lines in expected_tree.values())
    actual_line_count = sum(len(lines) for lines in actual_tree.values())
    sequence_denominator = max(expected_line_count, actual_line_count)
    if sequence_denominator == 0:
        sequence_agreement = 1.0
    else:
        lcs_total = sum(
            longest_common_subsequence_length(
                expected_tree.get(path, ()), actual_tree.get(path, ())
            )
            for path in expected_paths | actual_paths
        )
        sequence_agreement = lcs_total / sequence_denominator

    return TreeMetrics(
        expected_file_count=len(expected_paths),
        actual_file_count=len(actual_paths),
        missing_files=tuple(sorted(expected_paths - actual_paths)),
        extra_files=tuple(sorted(actual_paths - expected_paths)),
        expected_line_count=expected_line_count,
        actual_line_count=actual_line_count,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        sequence_agreement=sequence_agreement,
        exact_oracle_match=expected_tree == actual_tree,
    )


def is_complete_resolution(
    *,
    execution_status: ObservationStatus,
    metrics: TreeMetrics,
    syntactic_valid: bool,
    require_behavioral_evidence: bool = False,
    compiles: bool | None = None,
    scenario_tests_pass: bool | None = None,
) -> bool:
    """Apply the preregistered definition of a complete resolution.

    The base textual/structural claim requires a clean execution, exact oracle
    equality, and independent syntactic validation.  A behavioral claim also
    requires positive compilation and scenario-test evidence; ``None`` never
    counts as a pass.
    """

    base_complete = (
        execution_status is ObservationStatus.COMPLETED_CLEAN
        and metrics.exact_oracle_match
        and syntactic_valid
    )
    if not base_complete:
        return False
    if not require_behavioral_evidence:
        return True
    return compiles is True and scenario_tests_pass is True


def longest_common_subsequence_length(
    expected: Sequence[str], actual: Sequence[str]
) -> int:
    """Return LCS length with O(min(n, m)) memory."""

    if len(actual) > len(expected):
        expected, actual = actual, expected
    previous = [0] * (len(actual) + 1)
    for expected_line in expected:
        current = [0]
        for column, actual_line in enumerate(actual, start=1):
            if expected_line == actual_line:
                current.append(previous[column - 1] + 1)
            else:
                current.append(max(previous[column], current[column - 1]))
        previous = current
    return previous[-1]


def _canonical_tree(tree: TreeLines) -> dict[str, tuple[str, ...]]:
    canonical: dict[str, tuple[str, ...]] = {}
    for raw_path, raw_lines in tree.items():
        path = PurePosixPath(raw_path)
        if path.is_absolute() or ".." in path.parts or str(path) in ("", "."):
            raise ValueError(f"Tree path must be a safe relative POSIX path: {raw_path!r}")
        canonical_path = path.as_posix()
        if canonical_path in canonical:
            raise ValueError(f"Duplicate canonical tree path: {canonical_path}")
        canonical[canonical_path] = tuple(raw_lines)
    return canonical


def _line_counter(tree: Mapping[str, Sequence[str]]) -> Counter[LineToken]:
    return Counter(
        (path, line)
        for path, lines in tree.items()
        for line in lines
    )


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None
