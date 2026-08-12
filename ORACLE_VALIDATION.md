# Oracle and scenario-classification validation protocol

## Purpose

The submitted manuscript described the expected merge results as “manually
validated” without identifying the validators, criteria, or independent
checks. This protocol makes that process explicit and auditable.

The committed scenario labels and oracles begin as proposals. After the
two-pass review workflow succeeds, the current state is recorded as
`independently_confirmed` in
[`data/scenario_manifest.csv`](data/scenario_manifest.csv).

## Reviewer independence

At least two reviewers must inspect every scenario independently. Reviewers
must not inspect the evaluated tools' outputs or scores before submitting their
first-round decisions. They may inspect only:

- the scenario's `base`, `left`, and `right` variants;
- the proposed oracle;
- this rubric and the taxonomy definitions;
- scenario-specific acceptance criteria, once those are added.

Use stable pseudonymous identifiers such as `reviewer_A` and `reviewer_B` in
the public CSV. Keep the identity mapping in the private study records.

### Provenance of the current review ledger

The current records named `codex_reviewer_1` and `codex_reviewer_2` are two
separate Codex-assisted review passes performed under author direction. They
are not two independent human experts. The internal status name
`independently_confirmed` means that the fail-closed repository workflow has
two accepted records per scenario; it must not be expanded into a claim of
independent human validation. Publications using this dataset must describe
the evidence as an author-supervised, rubric-based, two-pass oracle audit, or
append genuine human reviews in a later immutable round before making a human
independence claim.

## Oracle review rubric

For each scenario, a reviewer records:

1. `intent_preserved`: the oracle integrates the intended compatible changes
   from both branches.
2. `complete_artifact_tree`: all required files are present and no required
   file is missing.
3. `no_unjustified_content`: the oracle introduces no content that cannot be
   justified from the intended integration.
4. `syntactically_valid`: the reviewer finds no conflict marker or apparent
   Java syntax defect.
5. `compilation_result`: `pass`, `fail`, `not_run`, or `not_applicable`.
6. `tests_result`: `pass`, `fail`, `not_run`, or `not_applicable`.
7. `oracle_decision`: `accept`, `reject`, or `needs_revision`.

An accepted oracle must pass the four review criteria and cannot have failed
compilation or tests. `not_run` is retained to distinguish missing executable
evidence from a successful check. Before the revised experiment, compilation
and testing policy must be finalized in Phase 1.

## Operational taxonomy

The authoritative coding rules, exclusions, decision procedure, and manuscript
scope are in [`TAXONOMY.md`](TAXONOMY.md). The summary below is retained for
reviewer convenience.

Mapping complexity is classified at the logical program-element level, not by
raw file count:

- `1:1`: one changed logical element corresponds to one conflicting or
  integrating counterpart across the branches.
- `1:N`: one changed logical element is split, propagated, or related to
  multiple counterparts across the branches.
- `N:N`: multiple interdependent elements on one side must be reconciled with
  multiple interdependent elements on the other side.

Change type identifies the primary intended effect:

- `structural`: primarily changes declarations, names, types, ownership,
  decomposition, file organization, or relationships among program elements.
- `behavioral`: primarily changes executable rules, validation, control flow,
  calculations, side effects, or runtime outcomes.

When a scenario contains both, the reviewer selects the primary effect and
explains the secondary effect in `comments`. If a primary effect cannot be
chosen defensibly, the scenario metadata must be revised before execution; the
reviewer must not force agreement with the proposed label.

Each reviewer independently assigns `assigned_mapping` and
`assigned_change_type`. These assignments validate the proposed labels rather
than merely confirming them.

## Recording reviews

Copy the header and add one row per reviewer and scenario to
[`data/oracle_reviews.csv`](data/oracle_reviews.csv). With two reviewers and 39
scenarios, the first review round contains 78 rows.

Rules:

- `review_round` begins at `1`;
- timestamps use UTC ISO 8601, for example `2026-07-24T18:30:00Z`;
- use `yes` or `no` for the four rubric checks;
- comments are mandatory in the research record for `reject`,
  `needs_revision`, or a classification disagreement;
- never overwrite a previous round; append a higher round.

## Disagreement and adjudication

After both first-round reviews are locked:

1. calculate agreement for oracle decision, mapping, and change type;
2. list disagreements without changing the original records;
3. reviewers discuss each disagreement;
4. revise the oracle or metadata where appropriate;
5. append a new review round;
6. use a third reviewer when consensus cannot be reached.

The manuscript should report the number of reviewers, initial agreement,
Cohen's kappa for categorical labels, number of disagreements, and
adjudication procedure. Agreement statistics do not replace a description of
the substantive corrections.

## Validation commands

Generate or refresh the technical oracle inventory:

```powershell
python -m scripts.oracle_audit
```

Prepare a new blinded reviewer packet. The output directory must be empty:

```powershell
python -m scripts.prepare_oracle_review --reviewer reviewer_A --output review_packets/reviewer_A
```

For a later immutable round, set the round number and repeat `--scenario` for
only the artifacts changed since the preceding decision:

```powershell
python -m scripts.prepare_oracle_review --reviewer reviewer_A --round 2 --output review_packets/reviewer_A_round_2 --scenario scenario_10 --scenario scenario_17
```

The returned rows must use the same reviewer identifier and the next
consecutive round number for each included scenario. Earlier records remain
unchanged in `data/oracle_reviews.csv`.

Use `--form-only` when the artifact trees will be transferred separately. The
packet deliberately excludes merge-tool outputs, scores, other reviewers'
decisions, and the proposed mapping/change-type labels.

Validate a completed returned form without modifying the canonical record:

```powershell
python -m scripts.ingest_oracle_reviews --form returned/reviewer_A/review_form.csv
```

After reviewing the validation output, append it atomically:

```powershell
python -m scripts.ingest_oracle_reviews --form returned/reviewer_A/review_form.csv --commit
```

Existing `(reviewer, scenario, round)` records cannot be overwritten, and
round numbers cannot be skipped. Repeat for the second reviewer and any later
adjudication rounds.

Validate the canonical manifest and the existence of all input/oracle trees:

```powershell
python -m scripts.scenario_metadata
```

This audit also verifies that the canonicalized `base`, `left`, `right`, and
oracle Java trees are identical across the three tool-specific copies of each
scenario. A divergence fails the audit instead of allowing the tools to receive
different experimental inputs.

Validate the review CSV while reviews are still in progress:

```powershell
python -m scripts.oracle_validation
```

Require two independent reviews for all 39 scenarios:

```powershell
python -m scripts.oracle_validation --require-complete
```

The last command fails until every scenario has at least two accepted oracle
records and at least two confirmations of both the mapping and change-type
labels. Mere review coverage is insufficient. The command must pass before the
revised experiment is released. Reviewer provenance must be reported
separately and accurately; passing this structural check alone does not prove
human independence.

The aggregate fail-closed check is:

```powershell
python -m scripts.phase2_gate
```

See [`PHASE2_STATUS.md`](PHASE2_STATUS.md) for documented open findings. A
documented issue remains a blocker; documenting it does not make the gate pass.

When all technical findings and review disagreements are resolved, run the
finalizer first as a dry run and then commit the status transition:

```powershell
python -m scripts.finalize_phase2
python -m scripts.finalize_phase2 --commit
python -m scripts.phase2_gate
```

The finalizer is all-or-nothing: it promotes both oracle and classification
statuses only after the complete evidence set passes.
