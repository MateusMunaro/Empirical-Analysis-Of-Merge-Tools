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

## Preserved invalid runs

`canonical_run_1` produced all 117 records and exposed missing explicit JDime
recursive mode. `canonical_run_2` added that option and passed the structural
gate, but source-level audit before analysis found that this JDime commit tries
automatic line-based fallback after structured exceptions unless
`--exit-on-error` is supplied. Both runs are preserved with
`run_invalidation.json` and must not be analyzed or reported. The Phase 4 gate
was also corrected to accept mathematically undefined precision/F1 for a
readable zero-line output.

`canonical_run_3` has now been received and passes the 117-cell integrity gate.
The 85-cell Codex-assisted evidence inspection is complete and recorded in
`PHASE4_AUDIT.md` and `canonical_run_3/manual_audit.csv`. Only the frozen
27-cell high-risk determinism repeat remains before `phase4_gate --final` can
release Phase 4.

## Remaining command sequence

Run only the frozen high-risk repeat in the same Linux x86_64 environment:

```bash
python -m scripts.revised_experiment \
  --tool FSTMerge --tool IntelliMerge --tool JDime \
  --scenario scenario_1 --scenario scenario_5 --scenario scenario_6 \
  --scenario scenario_10 --scenario scenario_11 --scenario scenario_17 \
  --scenario scenario_23 --scenario scenario_30 --scenario scenario_38 \
  --run-dir evaluation_results/revised_experiment/determinism_high_risk_1

python -m scripts.phase4_audit compare-sample \
  evaluation_results/revised_experiment/canonical_run_3 \
  evaluation_results/revised_experiment/determinism_high_risk_1 \
  --output evaluation_results/revised_experiment/canonical_run_3/determinism_high_risk.csv

python -m scripts.phase4_gate --final \
  evaluation_results/revised_experiment/canonical_run_3
```

Do not add `--release` to the repeat: it is intentionally a diagnostic subset
and cannot replace the canonical 117-cell source. Any substantive difference
blocks the final gate and requires explicit adjudication. A raw byte checksum
change alone is retained as provenance but is not a difference when the
normalized tree, terminal state, oracle, tool artifact, and metrics agree.

The preregistered high-risk repeat uses all three tools on scenarios 1, 5, 6,
10, 11, 17, 23, 30, and 38. These 27 cells cover every mapping/change-type
stratum, exact matches, empty artifacts, invalid outputs, syntax boundaries,
and conflicts. Run it without `--release`, then compare it with
`phase4_audit compare-sample`; diagnostic metadata prevents it from replacing
the 117-cell canonical source of truth.
