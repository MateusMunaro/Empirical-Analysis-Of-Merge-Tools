# Phase 4 audit record

Audit date: `2026-08-14`
Canonical source: `evaluation_results/revised_experiment/canonical_run_3`
Provenance: Codex-assisted, author-supervised evidence inspection; not an
independent human audit.

## Integrity result

`python -m scripts.phase4_gate canonical_run_3` passes. The run contains 117
unique observations, the complete 3 × 39 matrix, valid environment/artifact
provenance, applicable metrics, and internally consistent TP/FP/FN
denominators.

Observed terminal states:

| Tool | Clean | Conflicted | Invalid output | Crash | Timeout |
|---|---:|---:|---:|---:|---:|
| FSTMerge | 39 | 0 | 0 | 0 | 0 |
| IntelliMerge | 6 | 12 | 21 | 0 | 0 |
| JDime | 2 | 0 | 37 | 0 | 0 |

Only `IntelliMerge/scenario_6` and `IntelliMerge/scenario_10` satisfy the
preregistered complete textual-resolution definition.

## Evidence inspection

The selection in `canonical_run_3/manual_audit.csv` contains 85 cells: a
stratified sample across every `tool × mapping × change type`, every non-clean
terminal state, every configured Java source-form diagnostic, and both exact
oracle matches. All 85 decisions are `evidence_consistent` and retain the
auditor identifier, notes, and UTC timestamp.

The exhaustive checks found:

- all 58 `invalid_output` cells contain no hidden raw or normalized Java file;
- all 12 `completed_conflicted` cells contain actual conflict markers;
- every false source-form result has corresponding retained `javac` evidence;
- both exact matches have F1 = 1, sequence agreement = 1, and valid source
  form;
- sampled missing/extra paths and TP/FP/FN values agree with the retained
  artifact trees and the Phase 4 gate.

Raw byte-tree checksums can differ from normalized oracle equality because the
protocol normalizes line separators and one terminal separator. Normalized
tree comparison is authoritative for `exact_oracle_match`.

## Release condition

The frozen high-risk sample was repeated and compared. All 27 cells are
substantively deterministic, no cell requires adjudication, and the final
Phase 4 integrity gate passes. The canonical 117-cell dataset is released for
Phase 5 analysis.
