# Phase 2 status — metadata, taxonomy, and oracle validation

Last automated audit: `2026-08-10`  
Release state: **blocked pending human and oracle work**

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
- Blank first-round forms exist for `reviewer_A` and `reviewer_B` under
  `data/review_forms/`. They are templates, not completed reviews.

## Open technical findings

The automatic audit found two proposed-oracle defects. They are recorded in
`data/oracle_technical_issues.csv` and must be resolved through the review and
adjudication process rather than silently changed:

1. `scenario_17/Person.java` declares public type `PersonIdentity`.
2. `scenario_26/Custumer.java` declares public type `Customer`.

The oracle inventory currently contains 70 Java files. The two records above
have `technical_status=fail`; all other inventory records pass the limited
encoding/path/name/conflict-marker precheck. This technical check is not a
substitute for compilation or behavioral validation.

## Human work still required

- Two independent reviewers must complete 39 first-round records each: 78
  records total.
- Reviewers must not inspect tool outputs or each other's first-round forms.
- Every scenario needs two accepted oracle decisions and two confirmations of
  mapping and change type.
- Disagreements require a new immutable round and, if necessary, a third
  reviewer.
- The two technical findings must be accepted with justification or corrected
  and re-reviewed.

`data/oracle_reviews.csv` intentionally contains zero completed records until
real reviews are returned. No synthetic approval may be inserted to make the
gate pass.

## Executable tests and compilation

All 39 scenarios currently declare `associated_tests=none_defined`. A local
probe also showed that some oracle snippets are not self-contained compilation
units because supporting domain types and imports are absent. Phase 2 therefore
cannot claim that the oracles compile or preserve behavior. The authors must
either add fixtures/dependencies and executable acceptance tests, or explicitly
limit the study to textual/structural oracle conformance as defined in
`PROTOCOL.md`.

## Commands

Generate a full artifact packet for a reviewer in a new empty directory:

```powershell
python -m scripts.prepare_oracle_review --reviewer reviewer_A --output review_packets/reviewer_A
```

After returned forms have been validated and appended to
`data/oracle_reviews.csv`:

```powershell
python -m scripts.oracle_validation --require-complete
```

Run the complete fail-closed Phase 2 gate:

```powershell
python -m scripts.phase2_gate
```

The gate must remain blocked until technical issues, independent review,
manifest statuses, and the executable-test policy are resolved.
