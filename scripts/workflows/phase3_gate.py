"""Fail-closed checks for the frozen Phase 3 execution environment."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

from scripts.core.artifact_hashes import sha256_file, sha256_zip_content


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK = REPO_ROOT / "tool_versions.lock"
REQUIRED_TOOLS = ("FSTMerge", "IntelliMerge", "JDime")


def phase3_issues(lock_path: Path = DEFAULT_LOCK, release: bool = False) -> tuple[str, ...]:
    issues: list[str] = []
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return (f"lockfile cannot be read: {error}",)
    policy = lock.get("execution_policy", {})
    if policy.get("expected_observations") != 117:
        issues.append("execution policy must declare exactly 117 observations")
    if policy.get("timeout_seconds", 0) < 1:
        issues.append("execution timeout must be positive")
    if policy.get("jdime_mode") != "structured":
        issues.append("JDime mode must be frozen as structured")
    if policy.get("jdime_recursive_directories") is not True:
        issues.append("JDime directory inputs must be merged recursively")
    if policy.get("jdime_accept_non_java") is not True:
        issues.append("JDime directory inputs must bypass host MIME filtering")
    if policy.get("jdime_fallback") != "disabled":
        issues.append("JDime fallback must remain disabled")
    if policy.get("jdime_exit_on_error") is not True:
        issues.append("JDime must exit on structured merge errors")
    tools = lock.get("tools", {})
    for name in REQUIRED_TOOLS:
        if name not in tools:
            issues.append(f"lockfile is missing tool: {name}")
    for name in ("FSTMerge", "IntelliMerge"):
        entry = tools.get(name, {})
        path = REPO_ROOT / str(entry.get("artifact_path", ""))
        expected = entry.get("artifact_sha256")
        if not path.is_file():
            issues.append(f"{name} artifact is missing: {path}")
        elif not expected:
            issues.append(f"{name} has no frozen artifact checksum")
        elif sha256_file(path) != expected:
            issues.append(f"{name} artifact checksum does not match the lockfile")
    jdime = tools.get("JDime", {})
    jdime_arguments = jdime.get("arguments", [])
    if "--exit-on-error" not in jdime_arguments:
        issues.append("JDime locked arguments must disable automatic fallback")
    if "--accept-non-java" not in jdime_arguments:
        issues.append("JDime locked arguments must bypass host MIME filtering")
    jdime_key = "artifact_path_windows" if platform.system() == "Windows" else "artifact_path_linux"
    jdime_path = REPO_ROOT / str(jdime.get(jdime_key, ""))
    jdime_build = REPO_ROOT / str(jdime.get("build_artifact_path", ""))
    if release:
        if not jdime_path.is_file():
            issues.append(f"JDime launcher is missing: {jdime_path}")
        if not jdime_build.is_file():
            issues.append(f"JDime build artifact is missing: {jdime_build}")
        elif not jdime.get("build_content_sha256"):
            issues.append("JDime canonical build-content checksum has not been frozen")
        elif sha256_zip_content(jdime_build) != jdime["build_content_sha256"]:
            issues.append(
                "JDime canonical build-content checksum does not match the lockfile"
            )
        target = lock.get("target_environment", {}).get("operating_system", "")
        if not platform.system().lower().startswith("linux"):
            issues.append(
                f"release execution requires {target}; current host is {platform.platform()}"
            )
        for name in REQUIRED_TOOLS:
            entry = tools.get(name, {})
            java_path = REPO_ROOT / str(entry.get("runtime_java_path", ""))
            expected_major = entry.get("runtime_java_major")
            if not java_path.is_file():
                issues.append(f"{name} frozen Java runtime is missing: {java_path}")
                continue
            try:
                result = subprocess.run(
                    [str(java_path), "-version"], capture_output=True, text=True,
                    timeout=10, check=False,
                )
                version_text = (result.stderr or result.stdout).splitlines()[0]
            except (OSError, subprocess.TimeoutExpired, IndexError) as error:
                issues.append(f"{name} Java runtime cannot be identified: {error}")
                continue
            expected_token = f'"1.{expected_major}.' if expected_major == 8 else f'"{expected_major}.'
            if expected_token not in version_text:
                issues.append(
                    f"{name} Java runtime version does not match major {expected_major}: "
                    f"{version_text}"
                )
    required_modules = (
        REPO_ROOT / "scripts" / "core" / "analysis_units.py",
        REPO_ROOT / "scripts" / "core" / "evaluation_metrics.py",
        REPO_ROOT / "scripts" / "workflows" / "revised_experiment.py",
    )
    for path in required_modules:
        if not path.is_file():
            issues.append(f"required harness module is missing: {path.name}")
    return tuple(issues)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 environment")
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument(
        "--release", action="store_true",
        help="Require the complete target environment and all built artifacts",
    )
    args = parser.parse_args()
    issues = phase3_issues(args.lock, args.release)
    mode = "RELEASE" if args.release else "DEVELOPMENT"
    if issues:
        print(f"PHASE 3 {mode} GATE: BLOCKED ({len(issues)} issue(s))")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PHASE 3 {mode} GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
