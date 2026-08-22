"""Check that a revised manuscript remains aligned with canonical study claims."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Sequence


BANNED_PATTERNS = {
    r"Group 1: Completely Correct": "legacy overlapping result groups remain",
    r"Group 2: Partially Correct": "legacy overlapping result groups remain",
    r"Group 3: Execution Failures": "legacy overlapping result groups remain",
    r"Accuracy\s*=": "classification accuracy equation remains",
    r"executor\.py": "manuscript names a mutable implementation file",
    r"evaluation_results/": "manuscript names a mutable repository path",
    r"scripts/": "manuscript names a mutable repository path",
    r"JDime resolves many": "legacy JDime result claim remains",
    r"scalability limitation": "unsupported internal causal claim remains",
    r"graph-based abstraction still loses": "unsupported internal causal claim remains",
    r"F1-score\s*=\s*0\.80": "legacy recurring score claim remains",
    r"F1-score\s*=\s*0\.66": "legacy recurring score claim remains",
}

REQUIRED_TEXT = (
    "117 tool--scenario observations",
    "End-to-end F1",
    "$TP=2076$",
    "$TP=883$",
    "Only two of 117 cells",
    "We report no primary significance test",
    "controlled synthetic",
)


def manuscript_issues(
    tex_path: Path,
    *,
    summary_path: Path | None = None,
    require_assets: bool = False,
) -> tuple[str, ...]:
    try:
        text = tex_path.read_text(encoding="utf-8")
    except OSError as error:
        return (f"cannot read manuscript: {error}",)
    issues: list[str] = []
    for pattern, message in BANNED_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            issues.append(message)
    for required in REQUIRED_TEXT:
        if required not in text:
            issues.append(f"required revised claim is missing: {required}")
    begin_count = len(re.findall(r"\\begin\{", text))
    end_count = len(re.findall(r"\\end\{", text))
    if begin_count != end_count:
        issues.append(
            f"LaTeX environment count mismatch: {begin_count} begin, {end_count} end"
        )
    issues.extend(_bibliography_issues(text))
    if require_assets:
        for stable_id in ("F0", "F1", "F2", "F3"):
            if not (tex_path.parent / f"{stable_id}.pdf").is_file():
                issues.append(f"stable figure asset is missing: {stable_id}.pdf")
            if f"{{{stable_id}.pdf}}" not in text:
                issues.append(f"stable figure asset is not included: {stable_id}.pdf")
    if summary_path is not None:
        issues.extend(_summary_issues(text, summary_path))
    return tuple(issues)


def _bibliography_issues(text: str) -> list[str]:
    if "\\begin{thebibliography}" not in text:
        return []
    citation_order: list[str] = []
    seen: set[str] = set()
    bibliography_start = text.index("\\begin{thebibliography}")
    for match in re.finditer(r"\\cite\{([^}]+)\}", text[:bibliography_start]):
        for raw_key in match.group(1).split(","):
            key = raw_key.strip()
            if key and key not in seen:
                seen.add(key)
                citation_order.append(key)
    bibliography_order = re.findall(r"\\bibitem\{([^}]+)\}", text)
    issues = []
    duplicates = sorted(
        key for key in set(bibliography_order) if bibliography_order.count(key) > 1
    )
    missing = [key for key in citation_order if key not in bibliography_order]
    unused = [key for key in bibliography_order if key not in citation_order]
    if duplicates:
        issues.append(f"duplicate bibliography keys: {duplicates}")
    if missing:
        issues.append(f"citations missing bibliography entries: {missing}")
    if unused:
        issues.append(f"unused bibliography entries remain: {unused}")
    if not missing and not unused and citation_order != bibliography_order:
        issues.append("bibliography is not ordered by first citation")
    return issues


def _summary_issues(text: str, summary_path: Path) -> list[str]:
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read canonical analysis summary: {error}"]
    tools = {row["tool_name"]: row for row in summary.get("tool_summary", [])}
    expected = {
        "FSTMerge": (0.46361121830998053, 0.45172375117382718),
        "IntelliMerge": (0.711073323120824, 0.30995503828343612),
        "JDime": (None, 0.0),
    }
    issues = []
    for tool, (macro_f1, end_to_end) in expected.items():
        row = tools.get(tool)
        if row is None:
            issues.append(f"canonical summary is missing {tool}")
            continue
        observed_macro = row.get("macro_f1_score_mean")
        observed_e2e = row.get("end_to_end_f1_zero_unavailable")
        if macro_f1 is None:
            if observed_macro is not None:
                issues.append(f"canonical {tool} macro F1 should be undefined")
        elif not math.isclose(observed_macro, macro_f1, rel_tol=1e-12):
            issues.append(f"canonical {tool} macro F1 changed")
        if not math.isclose(observed_e2e, end_to_end, rel_tol=1e-12):
            issues.append(f"canonical {tool} end-to-end F1 changed")
    for displayed in (".464", ".452", ".711", ".310"):
        if displayed not in text:
            issues.append(f"manuscript is missing canonical displayed value {displayed}")
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("--summary-json", type=Path)
    parser.add_argument("--require-assets", action="store_true")
    args = parser.parse_args(argv)
    issues = manuscript_issues(
        args.manuscript,
        summary_path=args.summary_json,
        require_assets=args.require_assets,
    )
    if issues:
        print("MANUSCRIPT GATE: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("MANUSCRIPT GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
