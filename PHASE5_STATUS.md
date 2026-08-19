# Phase 5 status — descriptive analysis and presentation

Last automated generation: `2026-08-14`

## Released analysis components

The released 117-observation dataset now regenerates the following conceptual
artifacts from one source of truth:

- **T1 — Master outcome matrix:** one row per scenario and one non-overlapping
  outcome cell per tool.
- **T2 — Overall tool summary:** primary macro distributions, secondary pooled
  TP/FP/FN metrics, exact/complete rates, and end-to-end sensitivity.
- **T3 — Stratified summary:** every `tool × mapping × change type` stratum,
  with explicit applicable and unavailable denominators.
- **T4 — Execution robustness:** mutually exclusive terminal-state counts and
  proportions by tool and mapping.
- **T5 — Score decomposition:** TP/FP/FN, paths, exact value, and rounded value
  for every readable output.
- **T6 — Recurring rounded scores:** cells and TP/FP/FN decompositions for each
  rounded F1 value occurring more than once.
- **T7 — Line-difference examples:** representative missing and extra
  path-aware line tokens for exact, empty, conflicted, and low-precision cases.
- **F1 — Outcome heatmap:** scenario-level content F1 with unavailable, empty,
  conflicted, and complete outcomes explicitly marked.
- **F2 — Execution-state bars:** stacked terminal states by tool and mapping.
- **F3 — F1 distributions:** individual applicable observations, medians, and
  visible sample sizes by tool and mapping.

The identifiers above are stable conceptual references. Manuscript and reviewer
response prose must use these identifiers until final section, table, figure,
and replication-package locations are assigned.

## Statistical decision

The primary analysis is descriptive. No primary three-tool paired inferential
test is reported because JDime has no defined scenario-level F1 values and
therefore there are no complete cases across all three tools. Treating every
unavailable result as F1 = 0 would change the estimand from oracle conformance
among produced outputs to end-to-end availability sensitivity.

The study therefore reports:

1. scenario-level observations and explicit missingness;
2. macro distributions among defined applicable outputs;
3. pooled micro TP/FP/FN as a secondary content view;
4. exact and complete rates over all 39 expected scenarios;
5. a clearly labelled zero-unavailable end-to-end sensitivity analysis.

No p-value or claim of statistical significance is supported by the released
analysis. The manuscript must remove the earlier promise of generic
“statistical analysis” and present the study as a rigorous controlled,
descriptive comparison.

## Integrity guarantees

- All aggregates start from exactly 117 unique `tool × scenario` observations.
- Every declared stratum is present exactly once in the stratified table.
- Undefined precision/F1 and unavailable executions retain explicit
  denominators and are never silently discarded.
- Macro, micro, exact/complete, and end-to-end measures remain separately named.
- Regression tests freeze the canonical overall metrics and reject values that
  disagree with TP/FP/FN.

## Completion status

T2–T7 and F1–F3 are now integrated into the revised Results and Discussion
narrative. The master T1 matrix remains available as complete supplementary
evidence and is represented visually by F1 in the manuscript. Final page and
line numbers will be assigned only after IEEE typesetting is stable.

Phase 5 is complete for descriptive analysis. Later repository cleanup may move
the implementation and generated files, but the stable conceptual identifiers
and scientific values must remain unchanged.
