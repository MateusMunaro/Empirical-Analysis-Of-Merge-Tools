# Independent oracle review packet

Reviewer: `codex_reviewer_2`  
Round: `2`

Inspect only `artifacts/<scenario>/base`, `left`, `right`, and `proposed_oracle`.

Do not inspect merge-tool outputs, scores, previous reviewer decisions, or the
proposed mapping/change-type labels. Apply `ORACLE_VALIDATION.md` and
`TAXONOMY.md`, complete every field in `review_form.csv`, and use an ISO 8601
UTC timestamp. A non-accept decision or classification concern requires a
substantive comment. Return the completed form without modifying earlier
rounds. The study coordinator validates and appends it to
`data/oracle_reviews.csv`.

For `validation_scope=textual_structural_only`, use `tests_result=not_applicable`.
Use `compilation_result=not_run` unless a documented compilation fixture was
actually executed; do not infer compilation from visual inspection.
