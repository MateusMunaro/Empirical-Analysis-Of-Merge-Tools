# Experimental protocol for the revised study

Protocol version: `1.0-phase-1`  
Frozen on: `2026-08-10`  
Executable specification: [`scripts/evaluation_metrics.py`](scripts/evaluation_metrics.py)

## Purpose and authority

This document preregisters the unit of analysis, execution outcomes, output
normalization, scenario-level metrics, aggregation rules, and the definition
of a complete resolution before the revised experiment is run. If prose and
code disagree, the experiment must stop and both must be reconciled under a
new protocol version before results are inspected.

The legacy evaluator in `scripts/merge_evaluation_tool.py` is not normative for
the revised study. It uses sets of lines, reports a positional score as
`accuracy`, removes conflict markers before scoring, and classifies F1 = 1 as
`PERFECT`. Phase 3 must replace or isolate that path before any revised result
is released.

## Preregistered decisions

The revised study adopts these decisions:

1. The unit of analysis is one `(tool_name, scenario_id)` pair.
2. Classification accuracy and true negatives are removed. There is no
   defensible universe of negative source-code lines from which to derive TN.
3. Content precision, recall, and F1 use multiplicities of path-aware lines,
   not sets.
4. Order is reported separately as `sequence_agreement`, based on the longest
   common subsequence (LCS).
5. The complete expected and produced artifact trees are compared. Missing and
   extra files affect the score.
6. Textual equality, syntactic validity, compilation, and behavioral tests are
   independent observations.
7. A minimum complete textual/structural resolution requires
   `completed_clean AND exact_oracle_match AND syntactic_valid`.
8. A behavioral complete-resolution claim additionally requires
   `compiles AND scenario_tests_pass`.
9. Tool failures remain explicit outcomes. They are not silently converted to
   F1 = 0 in the primary conformance analysis.
10. A separately labelled end-to-end sensitivity analysis may assign zero to
    unavailable outputs. It must never replace the primary outcome reporting.
11. JDime receives directory inputs in explicit recursive mode and with
    `--accept-non-java`, which prevents host-dependent MIME classification from
    discarding Java files before the merge. It retains `structured` as the only
    merge strategy. `--exit-on-error` disables the tool's default automatic
    line-based fallback and exposes failures as terminal execution outcomes.

## Unit of analysis and expected matrix

The unit of analysis is:

`analysis_unit = (tool_name, scenario_id)`

The design contains:

- tools: FSTMerge, IntelliMerge, and JDime;
- scenarios: `scenario_1` through `scenario_39`;
- expected observations: `3 × 39 = 117`.

Every expected unit must appear exactly once. A crash, timeout, setup failure,
or missing output remains an observation. The canonical matrix implementation
is [`scripts/analysis_units.py`](scripts/analysis_units.py).

## Mutually exclusive execution outcomes

Each analysis unit receives exactly one terminal status:

| Status | Operational meaning |
|---|---|
| `completed_clean` | The process terminates successfully, satisfies the output contract, and no conflict marker is detected. |
| `completed_conflicted` | The process terminates and produces a readable output tree, but at least one conflict marker remains. |
| `invalid_output` | The process terminates, but the output tree is absent, empty, unreadable, undecodable as UTF-8, or violates the declared output contract. |
| `crash` | The process starts but terminates with a non-zero exit code or an execution error other than timeout. |
| `timeout` | The process exceeds the preregistered wall-clock limit and is terminated. |
| `setup_error` | The tool, runtime, or required configuration cannot be initialized before the merge process starts. |

Status precedence is `timeout`, `setup_error`, `crash`, `invalid_output`,
`completed_conflicted`, then `completed_clean`. For example, a timed-out
process is `timeout` even if it left a partial file. Partial artifacts are
retained for diagnosis but are not treated as a completed output.

Content metrics are applicable only to readable output trees classified as
`completed_clean` or `completed_conflicted`. All other statuses retain null
content metrics in the primary dataset.

## Output-tree contract and normalization

The comparison unit is the entire regular-file tree rooted at the declared
scenario output directory. Logs and execution metadata must be written outside
that directory. Relative POSIX paths are part of every line identity; files
must not be flattened or matched only by basename.

Normalization is deliberately conservative:

1. read every regular file as strict UTF-8;
2. convert CRLF and lone CR line endings to LF;
3. ignore one terminal line separator;
4. preserve blank lines, indentation, trailing whitespace, comments, internal
   whitespace, case, and relative paths;
5. retain conflict markers exactly as produced.

The protocol performs no source-code formatting, comment removal, whitespace
collapse, reordering, or conflict-marker deletion. Any additional
normalization would require a new protocol version and complete regeneration
of results.

## Path-aware multiset content metrics

For each normalized line, construct a token:

`token = (relative_file_path, normalized_line_text)`

Let `E(t)` be the multiplicity of token `t` in the oracle tree and `A(t)` its
multiplicity in the actual tree. Counts are:

`TP = Σ_t min(E(t), A(t))`

`FP = Σ_t max(A(t) - E(t), 0)`

`FN = Σ_t max(E(t) - A(t), 0)`

Metrics are:

`precision = TP / (TP + FP)`

`recall = TP / (TP + FN)`

`F1 = 2 × precision × recall / (precision + recall)`

Undefined-denominator rules are explicit:

- precision is null when the actual tree has zero line tokens;
- recall is null when the oracle tree has zero line tokens;
- F1 is null when precision or recall is null;
- when precision and recall are both defined and both zero, F1 is zero.

This prevents an absent or empty output from appearing to have a meaningful
content score. Such output is normally classified as `invalid_output` by the
execution layer.

## Sequence agreement

Order is measured independently. For every path in the union of oracle and
actual paths, calculate the LCS length of its normalized line sequences:

`sequence_agreement = Σ_path LCS(E_path, A_path) / max(|E|, |A|)`

Here `|E|` and `|A|` are the total line counts across their complete trees.
An absent file contributes an empty sequence. Two empty trees have sequence
agreement 1; if only one tree is empty, the agreement is 0.

This metric is not called accuracy and does not use TN.

## Exact oracle match and independent validity evidence

`exact_oracle_match` is true only when:

- the sets of relative paths are identical; and
- the normalized line sequence of every corresponding file is identical.

The following fields are recorded independently and are never inferred from
F1 or exact match:

- `syntactic_valid`: pass/fail result of the preregistered syntax validator;
- `compiles`: pass/fail/not-run/not-applicable compilation result;
- `scenario_tests_pass`: pass/fail/not-run/not-applicable scenario-test result.

A heuristic such as balanced braces is not sufficient evidence of syntactic
validity. The exact validator/compiler commands will be frozen with the tool
environment in Phase 3.

The minimum textual/structural complete resolution is:

`completed_clean AND exact_oracle_match AND syntactic_valid`

If the manuscript makes a behavioral or semantic claim, the stricter rule is:

`completed_clean AND exact_oracle_match AND syntactic_valid AND compiles AND scenario_tests_pass`

Unknown, not-run, or not-applicable evidence does not count as a pass for a
behavioral claim.

The current manifest fixes `validation_scope=textual_structural_only` for all
39 scenarios. Consequently, the revised benchmark may report textual oracle
conformance and separately observed syntax evidence, but it must not claim
semantic or behavioral correctness. The `behavioral` scenario label describes
the intended kind of change, not the evidence strength. Introducing executable
behavioral claims requires a new protocol version and named scenario tests.

## Aggregation rules

All aggregates begin from the 117-row master dataset; file-level rows are never
treated as independent scenarios.

For each tool and each declared stratum (`mapping` and `change_type`), report:

1. **Execution robustness:** count and proportion of all six statuses, using
   all expected scenarios as denominator.
2. **Primary oracle conformance:** individual values plus macro mean, median,
   and dispersion of precision, recall, F1, and sequence agreement among
   applicable produced outputs. The applicable denominator must be printed.
3. **Exact and complete rates:** counts and proportions using all expected
   scenarios as denominator; unavailable results remain non-complete.
4. **Secondary micro content scores:** sum TP, FP, and FN across applicable
   scenarios and calculate precision/recall/F1 from those sums. These are
   labelled `micro_*` and do not replace scenario-level results.
5. **End-to-end sensitivity:** for each expected scenario, use its produced F1
   when applicable and zero for `invalid_output`, `crash`, `timeout`, or
   `setup_error`. Label this `end_to_end_f1_zero_unavailable` and report it
   separately from primary conformance.

No aggregate may silently discard a scenario. Missing values remain null and
the numerator and denominator accompany every rate. Comparisons among tools
remain paired by `scenario_id`; inferential test selection belongs to Phase 5.

## Worked, auditable example

Consider these normalized trees:

| Tree | Path | Ordered lines |
|---|---|---|
| Oracle | `src/A.java` | `alpha`, `beta`, `beta`, `gamma` |
| Oracle | `src/B.java` | `omega` |
| Actual | `src/A.java` | `beta`, `alpha`, `beta`, `delta` |
| Actual | `src/C.java` | `omega` |

Path-aware multiset accounting gives:

- `src/A.java`: `alpha` contributes 1 TP, duplicate `beta` contributes 2 TP,
  `gamma` contributes 1 FN, and `delta` contributes 1 FP;
- missing `src/B.java` contributes 1 FN for `omega`;
- extra `src/C.java` contributes 1 FP for `omega`; the identical text does not
  cancel the missing line because its file path differs;
- totals: TP = 3, FP = 2, FN = 2;
- precision = `3 / (3 + 2) = 0.60`;
- recall = `3 / (3 + 2) = 0.60`;
- F1 = `0.60`.

For order, the LCS in `src/A.java` has length 2; the missing and extra paths
have LCS length 0. There are five lines in each tree, so:

`sequence_agreement = 2 / 5 = 0.40`

The path sets differ, so `exact_oracle_match = false`. This example is encoded
as a fixture in [`tests/test_evaluation_metrics.py`](tests/test_evaluation_metrics.py).

## Integrity and release checks

Before the revised experiment can be released, automated validation must
confirm:

1. exactly 117 unique `(tool_name, scenario_id)` observations;
2. exactly 39 observations per tool;
3. one valid terminal status per observation;
4. null content metrics for statuses without an applicable output;
5. non-null metrics for every applicable readable output;
6. no manually typed aggregate that disagrees with regenerated data;
7. metric code and the worked-example fixture still produce the documented
   values.

Run the current Phase 1 checks with:

```powershell
python -m unittest discover -s tests -v
```

## Matters intentionally assigned to later phases

Phase 1 freezes measurement semantics but does not pretend later work is done.
The following remain prerequisites before execution:

- preserve the completed Phase 2 oracle-review ledger and report its
  Codex-assisted provenance accurately;
- freeze tool commits, JDKs, arguments, checksums, timeout duration, syntax and
  compilation commands, and the JDime fallback policy (Phase 3);
- integrate this normative module into the execution/evaluation harness and
  produce the 117-row datasets (Phases 3 and 4);
- preregister exact inferential tests, if any, before inspecting regenerated
  comparative results (Phase 5).

Any change to normalization, metric formulas, applicability, aggregation, or
complete-resolution criteria after results are inspected requires a new
version, justification, and full regeneration of all results.
