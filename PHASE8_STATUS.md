# Phase 8 status — manuscript revision

Last revision pass: `2026-08-14`

## Completed technical rewrite

- The abstract reports the released 117-observation results and separates
  conditional conformance from end-to-end sensitivity.
- The title now scopes the study to execution robustness, textual oracle
  conformance, and controlled synthetic scenarios.
- Accuracy and true negatives were removed. The method now defines path-aware
  line multisets, multiplicity, sequence agreement, undefined values, and
  aggregation denominators.
- Methodology now includes the P1 worked example, the O1 two-pass oracle and
  taxonomy audit with agreement statistics and honest reviewer provenance, and
  the E1 frozen tool/runtime/policy table.
- Results were rewritten from the canonical evidence. The three overlapping
  legacy groups and their manually typed values were removed.
- Results now cover execution robustness, macro and micro conformance,
  end-to-end sensitivity, mapping/change strata, exact/complete outcomes, and
  auditable TP/FP/FN examples.
- Discussion no longer provides a universal ranking or unsupported internal
  causal explanations.
- Threats to validity distinguish internal, construct, external, and conclusion
  validity, including oracle-review provenance and the absence of executable
  behavioral evidence.
- The conclusion is aligned with the revised evidence.
- Stable vector assets F0–F3 are included without references to repository
  directories or implementation filenames.
- Duplicated Related Work material was consolidated, the LLM/agentic scope was
  clarified, and the two overlapping process figures were replaced by one
  execution-and-assessment flow.

## Remaining editorial work

- Complete the language and encoding pass after content stabilization.
- Insert exact reviewer quotations and final page/line references in the
  response letter.
- Produce clean and highlighted manuscripts from the same final source.
- Restore the IEEE Access class and remaining publication assets needed for a
  full local compilation. The current host has a LaTeX engine, but the class
  file is absent from the supplied article materials.
