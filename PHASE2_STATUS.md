# Phase 2 status — metadata, taxonomy, and oracle validation

Last automated audit: `2026-08-12`  
Release state: **complete — Phase 2 gate passed**

## Implemented

- The canonical manifest contains 39 unique scenario records and auditable
  fields for mapping, change type, origin, variant descriptions, merge intent,
  acceptance criteria, file trees, artifact scope, logical-element scope,
  dependency scope, associated tests, and review status.
- The file lists in the manifest match all 117 replicated tool/scenario
  input-oracle sets.
- `TAXONOMY.md` provides mutually exclusive operational coding rules and
  explicitly excludes unobserved human factors.
- `ORACLE_VALIDATION.md` defines independent review, rubric, immutable rounds,
  agreement, Cohen's kappa, and adjudication.
- `scripts/oracle_audit.py` inventories every proposed oracle file with SHA-256,
  size, normalized line count, public type, and conflict-marker count.
- `scripts/prepare_oracle_review.py` creates reviewer-specific forms and can
  package base/left/right/proposed-oracle trees without tool outputs or proposed
  classification labels.
- `scripts/ingest_oracle_reviews.py` validates returned forms, preserves
  immutable rounds, and appends records atomically only with `--commit`.
- `scripts/finalize_phase2.py` performs an all-or-nothing readiness check and
  promotes manifest statuses only after real approvals and technical closure.
- Two separate Codex-assisted first-round review passes are recorded for all
  39 scenarios: 78 immutable records from `codex_reviewer_1` and
  `codex_reviewer_2`.
- Initial agreement was 97.4% for oracle decisions (Cohen's kappa 0.938) and
  100% for both mapping and change type (kappa 1.000 for each).
- The 12 oracles identified for revision were corrected consistently across
  the three replicas, and targeted round-2 packets were generated under
  `data/review_forms/codex_reviewer_1_round_2/` and
  `data/review_forms/codex_reviewer_2_round_2/`.
- Both round-2 passes accepted the 12 revised oracles, adding 24 immutable
  records. The canonical review ledger therefore contains 102 records.
- The latest decisions agree on every oracle, mapping label, and change-type
  label (agreement 100%, Cohen's kappa 1.000 for all three dimensions).
- All 39 `oracle_review_status` and `classification_status` values are
  `independently_confirmed`, and `python -m scripts.phase2_gate` passes.

## Resolved technical findings

The first-round audit and reviewers identified two filename/public-type
defects. Both were corrected in every oracle replica and recorded in
`data/oracle_technical_issues.csv`:

1. `scenario_17/Person.java` was renamed to `PersonIdentity.java`.
2. `scenario_26/Custumer.java` was renamed to `Customer.java`.

The revised oracle inventory contains 77 Java files, and every record passes
the limited encoding/path/name/conflict-marker precheck. This technical check
is not a substitute for compilation or behavioral validation.

The same correction round addressed the substantive findings for scenarios
10, 12, 14, 15, 17, 21, 24, 26, 31, 32, 34, and 39. The revised merge intents
and exact expected trees are recorded in `data/scenario_manifest.csv` and the
round-2 review packets.

## Review provenance and limitation

The two public reviewer identifiers represent separate Codex-assisted review
passes completed under author direction; they do not represent two independent
human experts. The machine value `independently_confirmed` denotes satisfaction
of the repository's two-record workflow and must not be reported as independent
human validation in the manuscript. The defensible wording is
"author-supervised, rubric-based, two-pass oracle audit." A later human review
may be appended as a new immutable round without replacing this evidence.

## Evidence scope

The current benchmark is explicitly limited to
`validation_scope=textual_structural_only`, with
`associated_tests=not_applicable`. A local probe showed that some oracle
snippets are not self-contained compilation units because supporting domain
types and imports are absent. The revised study therefore evaluates textual
oracle conformance and separately recorded syntax evidence; it must not call
this semantic or behavioral correctness.

Adding executable behavioral validation later requires a new protocol version,
scenario fixtures, named test paths in the manifest, and complete regeneration
of results. The `behavioral` change-type label continues to describe the
scenario's intended effect, not the strength of validation evidence.

## Commands

Generate a full artifact packet for a reviewer in a new empty directory:

```powershell
python -m scripts.prepare_oracle_review --reviewer reviewer_A --output review_packets/reviewer_A
```

After returned forms have been validated and appended to
`data/oracle_reviews.csv`:

```powershell
python -m scripts.ingest_oracle_reviews --form returned/reviewer_A/review_form.csv
python -m scripts.ingest_oracle_reviews --form returned/reviewer_A/review_form.csv --commit
python -m scripts.oracle_validation --require-complete
```

The completed targeted second round was ingested with:

```powershell
python -m scripts.ingest_oracle_reviews --form data/review_forms/codex_reviewer_1_round_2/review_form.csv
python -m scripts.ingest_oracle_reviews --form data/review_forms/codex_reviewer_1_round_2/review_form.csv --commit
python -m scripts.ingest_oracle_reviews --form data/review_forms/codex_reviewer_2_round_2/review_form.csv
python -m scripts.ingest_oracle_reviews --form data/review_forms/codex_reviewer_2_round_2/review_form.csv --commit
```

Finalize confirmed statuses after both reviewers and adjudications are loaded:

```powershell
python -m scripts.finalize_phase2
python -m scripts.finalize_phase2 --commit
```

Run the complete fail-closed Phase 2 gate:

```powershell
python -m scripts.phase2_gate
```

Current result: `PHASE 2 GATE: PASS`.
