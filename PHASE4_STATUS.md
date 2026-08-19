# Phase 4 status — canonical re-execution

Last automated audit: `2026-08-14`

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

The canonical run passes the 117-cell integrity gate. The 85-cell
Codex-assisted evidence inspection is complete and recorded in the audit
record. The frozen 27-cell high-risk repeat is also complete: all 27 cells are
substantively deterministic and require no adjudication. The final Phase 4
gate passes and releases the canonical dataset for analysis.

## Final release evidence

The release was confirmed with the final integrity gate after comparing the
canonical run with the preregistered high-risk repeat. The repeat covers every
mapping/change-type stratum, both exact matches, empty Java artifacts, invalid
output, source-form boundaries, and conflicts.

The diagnostic repeat remains separate from the canonical 117-cell source of
truth. It supports determinism only and does not replace or enlarge the primary
dataset. Phase 5 must derive every result from the released canonical source.
