# Phase 4 status — canonical re-execution

Last automated audit: `2026-08-12`

## Ready

- `scripts/revised_experiment.py --release` requires the frozen complete
  3-tool × 39-scenario matrix and refuses to start when Phase 3 is not released.
- Every attempt records its terminal status, logs, command, runtime, checksums,
  raw output, normalized output, and applicable metrics.
- `scripts/phase4_gate.py` validates exactly 117 unique rows in each master CSV,
  all expected keys, valid statuses, checksum coverage, status/metric
  applicability, TP/FP/FN denominators, derived precision/recall/F1, sequence
  bounds, and the complete-resolution rule.
- Diagnostic smoke executions exist for each adapter. They are isolated from
  publication results and carry `run_kind = diagnostic`.

## Blocked

The canonical run has not been executed. This host is Windows and its Ubuntu
and Kali WSL2 registrations both point to missing `ext4.vhdx` files. The
release command correctly fails closed before creating a result directory.

After a working Linux x86_64 environment is available, run:

```bash
python3 setup.py
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m scripts.phase3_gate --release
python -m scripts.revised_experiment --release \
  --run-dir evaluation_results/revised_experiment/canonical_run_1
python -m scripts.phase4_gate \
  evaluation_results/revised_experiment/canonical_run_1
python -m scripts.phase4_audit prepare \
  evaluation_results/revised_experiment/canonical_run_1 \
  --output evaluation_results/revised_experiment/manual_audit.csv
```

Manual stratified inspection and a full or high-risk repeat for determinism
remain mandatory after this first canonical run. After the repeat, compare it
with `python -m scripts.phase4_audit compare <primary> <repeat> --output
<determinism.csv>`. Any differing cell requires explicit adjudication. Phases 5
and 8 results must not be regenerated from diagnostic data.
