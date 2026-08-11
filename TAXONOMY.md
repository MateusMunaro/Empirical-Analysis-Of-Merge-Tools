# Operational scenario taxonomy

Taxonomy version: `1.0-phase-2`  
Status: proposed labels pending independent review

## Purpose

This codebook replaces the former interpretive “Human Factors” dimension with
variables that are observable in the controlled scenario artifacts. It governs
the `mapping`, `change_type`, `artifact_file_count`, `logical_element_count`,
and `dependency_scope` fields in `data/scenario_manifest.csv`.

The benchmark has no human participants. It therefore does not measure
cognitive load, developer experience, effort, understandability, or other
human factors. Such properties must not be inferred from these labels.

## Unit being classified

Reviewers classify the intended integration represented by the complete
`base`, `left`, `right`, and proposed oracle trees. Raw file count alone does
not determine a label. A logical program element can be a declaration, field,
method, responsibility, or coupled group whose correspondence across branches
is relevant to the merge.

## Mapping complexity

Choose exactly one label:

| Label | Operational rule | Inclusion example | Exclusion rule |
|---|---|---|---|
| `1:1` | One changed logical element on a branch corresponds to one logical counterpart in the other branch or oracle. | Competing renames or type changes of the same field. | Do not use when one element is deliberately decomposed across multiple elements. |
| `1:N` | One logical source element corresponds to two or more target elements, or a change to one element must be propagated to multiple counterparts. | Splitting one class into data and contact classes. | Do not use when both sides contain multiple interdependent source groups. |
| `N:N` | Two or more interdependent logical elements on one side must be reconciled with two or more interdependent elements on the other side. | Coordinated reorganization of Person/Address into Client/Location. | File count alone is insufficient; the elements must participate in the same intended integration. |

Decision procedure:

1. Identify the smallest logical elements needed to explain the intended
   integration without looking at any tool output.
2. Record those elements and a conservative count in the manifest.
3. Trace their correspondences across the two branches and proposed oracle.
4. Assign `1:1`, `1:N`, or `N:N` from that correspondence graph.
5. If the graph cannot be reconstructed unambiguously, select a proposed label
   in the review form, mark the oracle decision `needs_revision`, and explain
   the ambiguity. Do not force agreement with the manifest.

## Change type

Choose exactly one primary label:

| Label | Operational rule | Typical evidence |
|---|---|---|
| `structural` | The primary intended effect changes declarations, naming, type representation, ownership, decomposition, file organization, or relationships among program elements. | Renaming a class, splitting one class, moving fields, changing an API shape. |
| `behavioral` | The primary intended effect changes executable rules, validation, control flow, calculations, side effects, state transitions, or runtime outcomes. | Combining validation constraints, discount rules, logging behavior, or recurring billing. |

A scenario may contain secondary effects of the other type. The reviewer still
selects one primary type and records the secondary effect in `comments`. If
neither effect is defensibly primary, the metadata requires revision before
execution. Multiple labels are not allowed in the master dataset because the
planned stratified aggregates require mutually exclusive groups.

## Artifact and dependency scope

- `artifact_file_count` is the number of distinct Java relative paths in the
  union of base, left, right, and oracle trees. It is generated from the
  artifacts and checked automatically.
- `logical_element_count` is a conservative proposed count used to make the
  classification auditable. It is not a complexity score and must be confirmed
  or corrected during review.
- `logical_elements` names the relevant elements or responsibility represented
  by the scenario title. Reviewers use `comments` to record a more precise list
  when the proposal is incomplete.
- `dependency_scope` records the correspondence form as
  `single_logical_correspondence`, `one_to_multiple_correspondence`, or
  `multiple_interdependent_correspondences`.

## Coding and adjudication

Each reviewer independently assigns `assigned_mapping` and
`assigned_change_type` in `data/oracle_reviews.csv` before seeing tool outputs.
The first-round records are immutable. The validation script reports observed
agreement and Cohen's kappa for both fields. Disagreements are discussed only
after both first-round forms are locked; corrections are appended as a higher
review round. A third reviewer adjudicates unresolved cases.

The public manifest remains `pending_independent_review` until every scenario
has at least two independent confirmations of both labels and two accepted
oracle decisions. Agreement coverage alone is not confirmation.

## Manuscript use

The revised manuscript should present this operational taxonomy instead of the
former Human Factors table. Any comparison by mapping or change type must be
generated from the confirmed manifest. The taxonomy describes the controlled
benchmark design; it is not a claim about the population frequency or
difficulty of real-world merges.
