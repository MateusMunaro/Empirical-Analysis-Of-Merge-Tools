# Data dictionary

This dictionary covers the normative resubmission datasets. Empty CSV values
mean “not applicable” or “not observed”; they must not be imputed as zero.

## `data/scenario_manifest.csv`

| Field | Meaning |
|---|---|
| `scenario_id` | Stable ID from `scenario_1` through `scenario_39`. |
| `title` | Human-readable controlled change label. |
| `mapping` | Confirmed operational mapping class: `1:1`, `1:N`, or `N:N`. |
| `change_type` | Confirmed `structural` or `behavioral` category. |
| `origin` | Scenario provenance; currently `synthetic_controlled`. |
| `*_description` | Description of the base, left, and right input trees. |
| `merge_intent` | Intended integration decision evaluated during oracle review. |
| `acceptance_criteria` | Scenario-specific textual acceptance rule. |
| `*_files` | Semicolon-delimited logical file lists for inputs/oracle. |
| `artifact_file_count` | Count of distinct artifacts across the input variants. |
| `logical_element_count` | Count used to operationalize mapping complexity. |
| `logical_elements` | Semicolon-delimited named logical changes/elements. |
| `dependency_scope` | Declared correspondence/dependency scope. |
| `validation_scope` | `textual_structural_only` or declared behavioral scope. |
| `associated_tests` | Scenario test reference; `not_applicable` when absent. |
| `*_basis` | Written justification for the assigned classification. |
| `oracle_review_status` | Workflow status of the proposed oracle. |
| `classification_status` | Workflow status of taxonomy labels. |

## `data/oracle_reviews.csv`

Each row is one reviewer/round/scenario decision. `reviewer_id` is provenance,
not proof that identities represent independent human experts.

| Field | Meaning |
|---|---|
| `review_round` | Sequential review pass for the reviewer ID. |
| `oracle_decision` | `accept`, `revise`, or `reject`. |
| `intent_preserved` | Whether the proposed oracle preserves declared intent. |
| `complete_artifact_tree` | Whether all required artifacts are present. |
| `no_unjustified_content` | Whether no unsupported content was introduced. |
| `syntactically_valid` | Reviewer syntax determination. |
| `compilation_result` | Compilation evidence or `not_run`. |
| `tests_result` | Behavioral test evidence or `not_applicable`/`not_run`. |
| `assigned_*` | Reviewer's independent taxonomy assignments. |
| `comments` | Decision rationale or requested correction. |
| `reviewed_at_utc` | ISO-8601 review timestamp in UTC. |

## `executions.csv`

One row per attempted `tool_name × scenario_id` cell.

| Field group | Meaning |
|---|---|
| identifiers | `tool_name`, `scenario_id`. |
| terminal outcome | `execution_status`, `status_detail`, `exit_code`. |
| timing | UTC start/finish, duration, and frozen timeout. |
| invocation | JSON command, working directory, stdout/stderr paths. |
| artifacts | raw/normalized paths, tool version, tool SHA-256. |
| environment | actual per-tool Java version, Python, OS, architecture. |
| integrity | JSON input hashes and oracle/raw/normalized tree hashes. |

`raw_output_checksum` and `normalized_output_checksum` may be empty when the
tool produced no readable tree. Input, oracle, and tool hashes are required for
all canonical cells.

## `scenario_tool_results.csv`

| Field | Meaning |
|---|---|
| `mapping`, `change_type` | Confirmed scenario labels copied from the manifest. |
| `expected_file_count`, `actual_file_count` | Whole-tree artifact counts. |
| `missing_files`, `extra_files` | Semicolon-delimited relative paths. |
| `expected_line_count`, `actual_line_count` | Normalized whole-tree line totals. |
| `true_positives` | Path-and-line tokens present in both multisets. |
| `false_positives` | Produced path-and-line multiplicity absent from the oracle. |
| `false_negatives` | Oracle path-and-line multiplicity absent from output. |
| `precision`, `recall`, `f1_score` | Content metrics derived from TP/FP/FN. |
| `sequence_agreement` | Sum of per-file LCS lengths divided by the larger tree line count. |
| `exact_oracle_match` | Exact equality of normalized path-to-lines mappings. |
| `syntactic_valid` | No configured `javac` parser diagnostic; not compilation. |
| `syntax_*` | Validator identity and evidence summary. |
| `compiles` | Compilation result; empty when not executed. |
| `scenario_tests_pass` | Behavioral result; empty when not available. |
| `complete_textual_resolution` | Frozen conjunction defined in `PROTOCOL.md`. |

Metrics are populated only for readable completed outputs. No true-negative or
classification-accuracy field belongs to the revised protocol.
