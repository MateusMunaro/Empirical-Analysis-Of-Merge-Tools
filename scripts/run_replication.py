"""Single public entry point for the published replication package."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run([sys.executable, "-m", *args], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete replication workflow.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--skip-setup", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    if args.run_dir.exists():
        parser.error(f"run directory already exists: {args.run_dir}")
    if not args.skip_setup:
        subprocess.run([sys.executable, "setup.py"], cwd=ROOT, check=True)
    if not args.skip_tests:
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    run("scripts.workflows.phase2_gate")
    run("scripts.workflows.phase3_gate", "--release")
    run("scripts.workflows.revised_experiment", "--release", "--run-dir", str(args.run_dir))
    run("scripts.workflows.phase4_gate", str(args.run_dir))
    run("scripts.workflows.phase5_analysis", str(args.run_dir / "scenario_tool_results.csv"), str(args.run_dir / "analysis"), "--run-root", str(args.run_dir), "--oracle-root", "output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
