"""Auditable execution and evaluation harness for the revised experiment.

Every invocation produces one immutable run directory.  Each requested
tool/scenario pair is recorded even when setup fails, a process crashes, times
out, or produces no output.  Raw tool output, normalized Java artifacts, logs,
commands, checksums, and scenario-level oracle metrics are kept separately.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

from scripts.analysis_units import (
    AnalysisMatrix,
    AnalysisUnit,
    DEFAULT_SCENARIO_IDS,
    DEFAULT_TOOLS,
    ObservationStatus,
    ScenarioObservation,
)
from scripts.artifact_hashes import sha256_file, sha256_zip_content
from scripts.evaluation_metrics import (
    TreeMetrics,
    evaluate_trees,
    is_complete_resolution,
    load_text_tree,
)
from scripts.scenario_metadata import load_manifest
from scripts.phase3_gate import phase3_issues


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOCK = REPO_ROOT / "tool_versions.lock"
DEFAULT_RESULTS_ROOT = REPO_ROOT / "evaluation_results" / "revised_experiment"
CONFLICT_PATTERN = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.MULTILINE)
PARSER_DIAGNOSTICS = (
    "compiler.err.expected",
    "compiler.err.illegal.start",
    "compiler.err.premature.eof",
    "compiler.err.reached.end.of.file",
    "compiler.err.not.stmt",
    "compiler.err.else.without.if",
    "compiler.err.catch.without.try",
    "compiler.err.try.without.catch.finally.or.resource.decls",
    "compiler.err.class.public.should.be.in.file",
)


EXECUTION_FIELDS = (
    "tool_name", "scenario_id", "execution_status", "status_detail",
    "started_at_utc", "finished_at_utc", "duration_seconds", "exit_code",
    "timeout_seconds", "command_json", "working_directory", "stdout_path",
    "stderr_path", "raw_output_path", "normalized_output_path",
    "tool_version", "tool_artifact_sha256", "java_version", "python_version",
    "operating_system", "architecture", "input_checksums_json",
    "oracle_checksum", "raw_output_checksum", "normalized_output_checksum",
)

RESULT_FIELDS = (
    "tool_name", "scenario_id", "mapping", "change_type", "execution_status",
    "status_detail", "expected_file_count", "actual_file_count",
    "missing_files", "extra_files", "expected_line_count", "actual_line_count",
    "true_positives", "false_positives", "false_negatives", "precision",
    "recall", "f1_score", "sequence_agreement", "exact_oracle_match",
    "syntactic_valid", "syntax_validator", "syntax_detail", "compiles",
    "scenario_tests_pass", "complete_textual_resolution",
)


@dataclass(frozen=True)
class ToolRuntime:
    name: str
    version: str
    artifact: Path
    checksum_artifact: Path
    expected_sha256: str | None
    checksum_kind: str
    java_executable: Path
    java_home: Path
    command_builder: Callable[[str, Path, Path, dict[str, str]], tuple[list[str], Path, Path]]


@dataclass(frozen=True)
class ProcessOutcome:
    exit_code: int | None
    timed_out: bool
    setup_error: str | None
    duration_seconds: float


@dataclass(frozen=True)
class SyntaxEvidence:
    valid: bool | None
    detail: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def sha256_tree(root: Path) -> str | None:
    if not root.is_dir():
        return None
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    if not files:
        return None
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content_hash = bytes.fromhex(sha256_file(path))
        digest.update(content_hash)
    return digest.hexdigest()


def contains_conflict_markers(root: Path) -> bool:
    for path in sorted(root.rglob("*.java")):
        try:
            if CONFLICT_PATTERN.search(path.read_text(encoding="utf-8")):
                return True
        except UnicodeDecodeError:
            return False
    return False


def normalize_java_output(raw_root: Path, normalized_root: Path) -> tuple[bool, str]:
    """Copy logical Java artifacts while stripping tool-generated prefixes.

    All current benchmark artifacts are declared at the scenario root.  A
    basename is therefore the logical relative path.  Duplicate basenames are
    rejected instead of renamed or overwritten.  Raw trees remain untouched.
    """

    java_files = sorted(path for path in raw_root.rglob("*.java") if path.is_file())
    if not java_files:
        return False, "no Java artifact was produced"
    by_name: dict[str, list[Path]] = {}
    for path in java_files:
        by_name.setdefault(path.name, []).append(path)
    collisions = sorted(name for name, paths in by_name.items() if len(paths) > 1)
    if collisions:
        return False, "ambiguous duplicate Java basenames: " + ", ".join(collisions)
    normalized_root.mkdir(parents=True, exist_ok=False)
    try:
        for name, paths in sorted(by_name.items()):
            source = paths[0]
            source.read_text(encoding="utf-8")
            shutil.copy2(source, normalized_root / name)
    except (OSError, UnicodeDecodeError) as error:
        shutil.rmtree(normalized_root, ignore_errors=True)
        return False, f"unreadable Java artifact: {error}"
    return True, f"normalized {len(java_files)} Java artifact(s)"


def classify_terminal_status(
    *, process: ProcessOutcome, output_valid: bool, has_conflicts: bool
) -> tuple[ObservationStatus, str]:
    if process.timed_out:
        return ObservationStatus.TIMEOUT, "process exceeded the configured timeout"
    if process.setup_error:
        return ObservationStatus.SETUP_ERROR, process.setup_error
    if process.exit_code not in (0, None):
        return ObservationStatus.CRASH, f"process exited with code {process.exit_code}"
    if not output_valid:
        return ObservationStatus.INVALID_OUTPUT, "output contract was not satisfied"
    if has_conflicts:
        return ObservationStatus.COMPLETED_CONFLICTED, "conflict markers remain"
    return ObservationStatus.COMPLETED_CLEAN, "process completed with a readable output tree"


def run_process(
    command: Sequence[str], cwd: Path, timeout_seconds: int,
    stdout_path: Path, stderr_path: Path, env: dict[str, str] | None = None,
) -> ProcessOutcome:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(command), cwd=cwd, env=env, capture_output=True,
            timeout=timeout_seconds, check=False,
        )
        stdout_path.write_bytes(completed.stdout)
        stderr_path.write_bytes(completed.stderr)
        return ProcessOutcome(
            completed.returncode, False, None, time.monotonic() - started
        )
    except subprocess.TimeoutExpired as error:
        stdout_path.write_bytes(error.stdout or b"")
        stderr_path.write_bytes(error.stderr or b"")
        return ProcessOutcome(None, True, None, time.monotonic() - started)
    except OSError as error:
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(str(error), encoding="utf-8")
        return ProcessOutcome(None, False, str(error), time.monotonic() - started)


def javac_syntax_evidence(root: Path, evidence_dir: Path, timeout_seconds: int = 30) -> SyntaxEvidence:
    files = sorted(str(path) for path in root.rglob("*.java") if path.is_file())
    if not files:
        return SyntaxEvidence(None, "not run: normalized tree has no Java files")
    javac = shutil.which("javac")
    if javac is None:
        return SyntaxEvidence(None, "not run: javac is unavailable")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    classes = evidence_dir / "classes"
    classes.mkdir()
    command = [javac, "-proc:none", "-XDrawDiagnostics", "-d", str(classes), *files]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout_seconds, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return SyntaxEvidence(None, f"validator could not complete: {error}")
    diagnostics = (result.stdout or "") + (result.stderr or "")
    (evidence_dir / "javac.stdout.txt").write_text(result.stdout or "", encoding="utf-8")
    (evidence_dir / "javac.stderr.txt").write_text(result.stderr or "", encoding="utf-8")
    parser_errors = sorted(
        diagnostic for diagnostic in PARSER_DIAGNOSTICS if diagnostic in diagnostics
    )
    if parser_errors:
        return SyntaxEvidence(False, "parser diagnostics: " + ", ".join(parser_errors))
    return SyntaxEvidence(
        True,
        "no javac parser diagnostic; type-resolution diagnostics, if any, are not compilation evidence",
    )


def _java_version(java_executable: Path) -> str:
    try:
        result = subprocess.run(
            [str(java_executable), "-version"], capture_output=True, text=True,
            timeout=10, check=False,
        )
        return " ".join(((result.stderr or result.stdout).splitlines()[:2]))
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"unavailable: {error}"


def _artifact_preflight(runtime: ToolRuntime) -> str | None:
    if not runtime.artifact.is_file():
        return f"locked tool artifact is missing: {runtime.artifact}"
    if runtime.expected_sha256:
        if not runtime.checksum_artifact.is_file():
            return f"locked checksum artifact is missing: {runtime.checksum_artifact}"
        observed = (
            sha256_zip_content(runtime.checksum_artifact)
            if runtime.checksum_kind == "canonical_zip_content_sha256"
            else sha256_file(runtime.checksum_artifact)
        )
        if observed != runtime.expected_sha256:
            return (
                f"tool artifact checksum mismatch: expected {runtime.expected_sha256}, "
                f"observed {observed}"
            )
    return None


def _intellimerge_command(
    scenario_id: str, attempt: Path, raw: Path, lock: dict[str, str]
) -> tuple[list[str], Path, Path]:
    source = REPO_ROOT / "scenarios_base" / "IntelliMerge" / scenario_id
    artifact = REPO_ROOT / lock["artifact_path"]
    command = [
        lock["java_executable"], "-jar", str(artifact), "-d", str(source / "left"),
        str(source / "base"), str(source / "right"), "-o", str(raw),
    ]
    return command, REPO_ROOT, raw


def _fstmerge_command(
    scenario_id: str, attempt: Path, raw: Path, lock: dict[str, str]
) -> tuple[list[str], Path, Path]:
    isolated = attempt / "isolated_input"
    shutil.copytree(REPO_ROOT / "scenarios_base" / "FSTMerge" / scenario_id, isolated)
    artifact = REPO_ROOT / lock["artifact_path"]
    command = [
        lock["java_executable"], "-jar", str(artifact), "--expression",
        str(isolated / "merge.expression"), "--base-directory", str(isolated),
    ]
    return command, REPO_ROOT, isolated / "merge"


def _jdime_command(
    scenario_id: str, attempt: Path, raw: Path, lock: dict[str, str]
) -> tuple[list[str], Path, Path]:
    artifact_key = "artifact_path_windows" if os.name == "nt" else "artifact_path_linux"
    artifact = REPO_ROOT / lock[artifact_key]
    source = REPO_ROOT / "scenarios_base" / "JDime" / scenario_id
    command = [
        str(artifact), "-f", "--mode", "structured", "--recursive",
        "--exit-on-error", "--output", str(raw),
        str(source / "left"), str(source / "base"), str(source / "right"),
    ]
    return command, artifact.parent, raw


def load_runtimes(lock_path: Path) -> tuple[dict, dict[str, ToolRuntime]]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    tools = lock["tools"]
    fallback_java = Path(shutil.which("java") or "java")

    def java_for(entry: dict) -> Path:
        frozen = REPO_ROOT / entry["runtime_java_path"]
        return frozen if frozen.is_file() else fallback_java

    intelli_java = java_for(tools["IntelliMerge"])
    fst_java = java_for(tools["FSTMerge"])
    jdime_java = java_for(tools["JDime"])
    runtimes = {
        "IntelliMerge": ToolRuntime(
            "IntelliMerge", tools["IntelliMerge"]["tag"],
            REPO_ROOT / tools["IntelliMerge"]["artifact_path"],
            REPO_ROOT / tools["IntelliMerge"]["artifact_path"],
            tools["IntelliMerge"]["artifact_sha256"],
            "raw_sha256",
            intelli_java, intelli_java.parent.parent,
            lambda scenario, attempt, raw, _ignored: _intellimerge_command(
                scenario, attempt, raw,
                {**tools["IntelliMerge"], "java_executable": str(intelli_java)}
            ),
        ),
        "FSTMerge": ToolRuntime(
            "FSTMerge", tools["FSTMerge"]["commit"],
            REPO_ROOT / tools["FSTMerge"]["artifact_path"],
            REPO_ROOT / tools["FSTMerge"]["artifact_path"],
            tools["FSTMerge"]["artifact_sha256"],
            "raw_sha256",
            fst_java, fst_java.parent.parent,
            lambda scenario, attempt, raw, _ignored: _fstmerge_command(
                scenario, attempt, raw,
                {**tools["FSTMerge"], "java_executable": str(fst_java)}
            ),
        ),
        "JDime": ToolRuntime(
            "JDime", tools["JDime"]["commit"],
            REPO_ROOT / (
                tools["JDime"]["artifact_path_windows"] if os.name == "nt"
                else tools["JDime"]["artifact_path_linux"]
            ),
            REPO_ROOT / tools["JDime"]["build_artifact_path"],
            tools["JDime"]["build_content_sha256"],
            tools["JDime"]["build_artifact_verification"],
            jdime_java, jdime_java.parent.parent,
            lambda scenario, attempt, raw, _ignored: _jdime_command(
                scenario, attempt, raw, tools["JDime"]
            ),
        ),
    }
    return lock, runtimes


def _copy_raw_output(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        return
    if source.is_dir():
        shutil.copytree(source, destination)


def _input_checksums(tool: str, scenario_id: str) -> dict[str, str | None]:
    source = REPO_ROOT / "scenarios_base" / tool / scenario_id
    return {variant: sha256_tree(source / variant) for variant in ("base", "left", "right")}


def _empty_metric_record() -> dict[str, object]:
    return {field: None for field in RESULT_FIELDS[6:20]}


def run_attempt(
    runtime: ToolRuntime, scenario_id: str, run_dir: Path, timeout_seconds: int,
    manifest_by_id: dict, environment: dict[str, str],
) -> tuple[dict[str, object], dict[str, object], ScenarioObservation]:
    attempt = run_dir / "attempts" / runtime.name / scenario_id
    attempt.mkdir(parents=True, exist_ok=False)
    raw = attempt / "raw_output"
    normalized = attempt / "normalized_output"
    stdout_path = attempt / "stdout.log"
    stderr_path = attempt / "stderr.log"
    started = utc_now()
    command: list[str] = []
    cwd = REPO_ROOT
    produced_source = raw
    setup_issue = _artifact_preflight(runtime)
    if setup_issue is None:
        try:
            command, cwd, produced_source = runtime.command_builder(
                scenario_id, attempt, raw, {}
            )
            if produced_source == raw:
                raw.mkdir()
            process_env = os.environ.copy()
            process_env["JAVA_HOME"] = str(runtime.java_home)
            process_env["PATH"] = (
                f"{runtime.java_executable.parent}{os.pathsep}"
                f"{process_env.get('PATH', '')}"
            )
            process = run_process(
                command, cwd, timeout_seconds, stdout_path, stderr_path,
                env=process_env,
            )
            if produced_source != raw and produced_source.is_dir():
                _copy_raw_output(produced_source, raw)
        except OSError as error:
            process = ProcessOutcome(None, False, str(error), 0.0)
            stdout_path.write_text("", encoding="utf-8")
            stderr_path.write_text(str(error), encoding="utf-8")
    else:
        process = ProcessOutcome(None, False, setup_issue, 0.0)
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(setup_issue, encoding="utf-8")

    output_valid, normalization_detail = (
        normalize_java_output(raw, normalized)
        if raw.is_dir() else (False, "raw output directory is absent")
    )
    conflicts = output_valid and contains_conflict_markers(normalized)
    status, status_detail = classify_terminal_status(
        process=process, output_valid=output_valid, has_conflicts=bool(conflicts)
    )
    if status is ObservationStatus.INVALID_OUTPUT:
        status_detail = normalization_detail
    finished = utc_now()
    manifest = manifest_by_id[scenario_id]
    oracle = REPO_ROOT / "output" / runtime.name / "expected" / scenario_id
    observation = ScenarioObservation(
        AnalysisUnit(runtime.name, scenario_id), status, status_detail
    )
    execution = {
        "tool_name": runtime.name,
        "scenario_id": scenario_id,
        "execution_status": status.value,
        "status_detail": status_detail,
        "started_at_utc": started,
        "finished_at_utc": finished,
        "duration_seconds": round(process.duration_seconds, 6),
        "exit_code": process.exit_code,
        "timeout_seconds": timeout_seconds,
        "command_json": json.dumps(command, ensure_ascii=False),
        "working_directory": str(cwd),
        "stdout_path": str(stdout_path.relative_to(run_dir).as_posix()),
        "stderr_path": str(stderr_path.relative_to(run_dir).as_posix()),
        "raw_output_path": str(raw.relative_to(run_dir).as_posix()),
        "normalized_output_path": str(normalized.relative_to(run_dir).as_posix()),
        "tool_version": runtime.version,
        "tool_artifact_sha256": (
            sha256_file(runtime.checksum_artifact)
            if runtime.checksum_artifact.is_file() else None
        ),
        "java_version": _java_version(runtime.java_executable),
        **environment,
        "input_checksums_json": json.dumps(
            _input_checksums(runtime.name, scenario_id), sort_keys=True
        ),
        "oracle_checksum": sha256_tree(oracle),
        "raw_output_checksum": sha256_tree(raw),
        "normalized_output_checksum": sha256_tree(normalized),
    }

    result: dict[str, object] = {
        "tool_name": runtime.name,
        "scenario_id": scenario_id,
        "mapping": manifest.mapping.value,
        "change_type": manifest.change_type.value,
        "execution_status": status.value,
        "status_detail": status_detail,
        **_empty_metric_record(),
        "syntactic_valid": None,
        "syntax_validator": "javac -proc:none -XDrawDiagnostics; parser diagnostics only",
        "syntax_detail": "not applicable for this execution status",
        "compiles": None,
        "scenario_tests_pass": None,
        "complete_textual_resolution": False,
    }
    if status in (
        ObservationStatus.COMPLETED_CLEAN, ObservationStatus.COMPLETED_CONFLICTED
    ):
        metrics = evaluate_trees(load_text_tree(oracle), load_text_tree(normalized))
        result.update(_metrics_record(metrics))
        syntax = javac_syntax_evidence(normalized, attempt / "syntax_evidence")
        result["syntactic_valid"] = syntax.valid
        result["syntax_detail"] = syntax.detail
        result["complete_textual_resolution"] = is_complete_resolution(
            execution_status=status,
            metrics=metrics,
            syntactic_valid=syntax.valid is True,
        )
    return execution, result, observation


def _metrics_record(metrics: TreeMetrics) -> dict[str, object]:
    record = asdict(metrics)
    return {
        "expected_file_count": record["expected_file_count"],
        "actual_file_count": record["actual_file_count"],
        "missing_files": ";".join(record["missing_files"]),
        "extra_files": ";".join(record["extra_files"]),
        "expected_line_count": record["expected_line_count"],
        "actual_line_count": record["actual_line_count"],
        "true_positives": record["true_positives"],
        "false_positives": record["false_positives"],
        "false_negatives": record["false_negatives"],
        "precision": record["precision"],
        "recall": record["recall"],
        "f1_score": record["f1_score"],
        "sequence_agreement": record["sequence_agreement"],
        "exact_oracle_match": record["exact_oracle_match"],
    }


def _write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def execute_matrix(
    *, run_dir: Path, tools: Sequence[str], scenarios: Sequence[str],
    timeout_seconds: int, lock_path: Path = DEFAULT_LOCK,
    run_kind: str = "diagnostic",
) -> None:
    run_dir = run_dir.resolve()
    lock_path = lock_path.resolve()
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    lock, runtimes = load_runtimes(lock_path)
    unknown_tools = sorted(set(tools) - set(runtimes))
    if unknown_tools:
        raise ValueError("Unknown tool(s): " + ", ".join(unknown_tools))
    expected_scenarios = set(DEFAULT_SCENARIO_IDS)
    unknown_scenarios = sorted(set(scenarios) - expected_scenarios)
    if unknown_scenarios:
        raise ValueError("Unknown scenario(s): " + ", ".join(unknown_scenarios))
    manifest_by_id = {item.scenario_id: item for item in load_manifest()}
    environment = {
        "python_version": platform.python_version(),
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "created_at_utc": utc_now(), "tools": list(tools),
                "scenarios": list(scenarios), "timeout_seconds": timeout_seconds,
                "run_kind": run_kind, "lockfile": str(lock_path), "lock": lock,
                "environment": environment,
            }, indent=2, ensure_ascii=False,
        ), encoding="utf-8",
    )
    executions: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    matrix = AnalysisMatrix(tools=tools, scenario_ids=scenarios)
    for tool in tools:
        for scenario in scenarios:
            execution, result, observation = run_attempt(
                runtimes[tool], scenario, run_dir, timeout_seconds,
                manifest_by_id, environment,
            )
            executions.append(execution)
            results.append(result)
            matrix.add(observation)
            print(f"{tool}/{scenario}: {observation.status.value}")
    matrix.validate_complete()
    _write_csv(run_dir / "executions.csv", EXECUTION_FIELDS, executions)
    _write_csv(run_dir / "scenario_tool_results.csv", RESULT_FIELDS, results)
    (run_dir / "status_counts.json").write_text(
        json.dumps(
            {status.value: count for status, count in matrix.status_counts().items()},
            indent=2,
        ), encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the revised merge experiment")
    parser.add_argument("--tool", action="append", dest="tools")
    parser.add_argument("--scenario", action="append", dest="scenarios")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument(
        "--release", action="store_true",
        help="Run the canonical 117-cell matrix; fail closed unless Phase 3 release passes",
    )
    args = parser.parse_args()
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    timeout = args.timeout or int(lock["execution_policy"]["timeout_seconds"])
    if timeout < 1:
        parser.error("--timeout must be at least 1 second")
    tools = tuple(args.tools or DEFAULT_TOOLS)
    scenarios = tuple(args.scenarios or DEFAULT_SCENARIO_IDS)
    if args.release:
        if tools != tuple(DEFAULT_TOOLS) or scenarios != tuple(DEFAULT_SCENARIO_IDS):
            parser.error("--release requires the complete frozen 3 x 39 matrix")
        issues = phase3_issues(args.lock.resolve(), release=True)
        if issues:
            print("ERROR: Phase 3 release gate is closed:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            return 1
    run_dir = args.run_dir or DEFAULT_RESULTS_ROOT / datetime.now().strftime(
        "%Y%m%dT%H%M%SZ"
    )
    try:
        execute_matrix(
            run_dir=run_dir, tools=tools, scenarios=scenarios,
            timeout_seconds=timeout, lock_path=args.lock,
            run_kind="canonical_release" if args.release else "diagnostic",
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Run completed: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
