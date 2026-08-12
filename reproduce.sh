#!/usr/bin/env bash
set -euo pipefail

run_dir="${1:-evaluation_results/revised_experiment/canonical_run_2}"

python3 setup.py
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m scripts.phase2_gate
python -m scripts.phase3_gate --release
python -m scripts.revised_experiment --release --run-dir "$run_dir"
python -m scripts.phase4_gate "$run_dir"
