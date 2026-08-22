"""Build the enriched Phase 2 scenario manifest from canonical artifacts.

The generated descriptions document the current oracle's intended decision.
They remain proposals until the independent review process confirms them.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "scenario_manifest.csv"
CANONICAL_TOOL = "FSTMerge"

FIELDNAMES = (
    "scenario_id",
    "title",
    "mapping",
    "change_type",
    "origin",
    "base_description",
    "left_description",
    "right_description",
    "merge_intent",
    "acceptance_criteria",
    "base_files",
    "left_files",
    "right_files",
    "expected_files",
    "artifact_file_count",
    "logical_element_count",
    "logical_elements",
    "dependency_scope",
    "validation_scope",
    "associated_tests",
    "mapping_basis",
    "change_type_basis",
    "oracle_review_status",
    "classification_status",
)


MERGE_INTENTS = {
    1: "Adopt Client as the resolved class name and update the constructor and textual representation consistently.",
    2: "Keep the phone field name and incorporate the default phone value selected by the oracle.",
    3: "Adopt getNumber and setNumber as the resolved phone accessor names.",
    4: "Preserve the String phone representation selected by the oracle instead of either incompatible numeric type change.",
    5: "Preserve the Person class when one branch removes it and the other retains it.",
    6: "Add the Person class represented identically by both branches.",
    7: "Remove the email state and its accessors while retaining the name state selected by the oracle.",
    8: "Combine the email and phone additions with their constructor parameters and accessors.",
    9: "Remove the textual representation method while retaining the Person data fields and accessors.",
    10: "Retain the branch-supported no-argument and two-argument constructors, complete accessors, and the left branch's textual representation without inventing a new constructor.",
    11: "Combine Builder-based user creation from the left branch with Validator-based create and update checks from the right branch.",
    12: "Combine distributed order validation with audit logging and retain every validator, exception, and logger artifact required by the resolved OrderService workflow.",
    13: "Resolve the Person decomposition into Individual and ContactInfo according to the oracle tree.",
    14: "Resolve the Person decomposition into PersonalInfo and ContactDetails while propagating the left branch's name-to-fullName change into PersonalInfo.",
    15: "Resolve the attribute reorganization across Individual and ContactInfo while propagating the left branch's getPhoneNumber and setPhoneNumber accessors into ContactInfo.",
    16: "Retain Person while extracting contact data into ContactData and applying the selected phone representation.",
    17: "Retain the right branch's PersonIdentity and ContactMethods decomposition despite the competing whole-class removal.",
    18: "Resolve the addition into PersonBasicInfo and PersonContactInfo.",
    19: "Resolve the removal across the CoreInfo and ExtendedInfo decomposition.",
    20: "Resolve the addition across PersonId and PersonContact.",
    21: "Resolve the decomposition into Identity and Contact while propagating the left branch's removal of birthDate.",
    22: "Resolve the attribute addition across BasicPerson and ExtendedPerson.",
    23: "Combine strategy-based notification dispatch with logging and error handling.",
    24: "Resolve the coupled Person-to-Client and Address-to-Location reorganization while preserving city in Location.",
    25: "Resolve the coupled Person-to-User and contact-model reorganization while retaining the oracle's Contact representation.",
    26: "Integrate the selected Customer and Order field changes using Java filenames consistent with their public types.",
    27: "Resolve the coupled Department-to-Division and Employee-to-Worker reorganization.",
    28: "Retain the Address artifact selected by the oracle while resolving the competing Person and detailed-profile decomposition.",
    29: "Retain Employee and integrate the selected Organization and Position artifacts from the multi-class decomposition.",
    30: "Retain the Contact and Person artifacts selected by the oracle while resolving the competing UserContact reorganization.",
    31: "Resolve Customer and Order into Client, Item, and Purchase while propagating email into Client and orderDate into Purchase.",
    32: "Retain Course, preserve student identity in Learner, and retain the separate StudentDetails artifact.",
    33: "Retain Profile and User while resolving the competing Account and UserProfile decomposition.",
    34: "Combine the left branch's tiered premium discounts with the right branch's MAX_DISCOUNT cap.",
    35: "Combine the competing setAge validation constraints into the accepted age-validation behavior.",
    36: "Combine singleton connection management with factory-based database connection creation.",
    37: "Resolve list-versus-set membership semantics with deterministic uniqueness and both list and set views.",
    38: "Combine exception-based and boolean validation with configurable error logging.",
    39: "Integrate the branch-defined loyalty and subscription behaviors without invented cross-system bonuses: use the larger branch-defined customer discount, configure recurring billing before total calculation, retain the right branch's 12 percent service tax, and keep loyalty and subscription upgrades independent.",
}


def build_manifest_rows(manifest_path: Path) -> list[dict[str, str | int]]:
    with manifest_path.open("r", encoding="utf-8", newline="") as source_file:
        source_rows = list(csv.DictReader(source_file))

    rows: list[dict[str, str | int]] = []
    for source in source_rows:
        scenario_id = _required(source, "scenario_id")
        number = int(scenario_id.removeprefix("scenario_"))
        title = _required(source, "title")
        mapping = _required(source, "mapping")
        variant_files = {
            variant: _java_files(
                REPO_ROOT
                / "scenarios_base"
                / CANONICAL_TOOL
                / scenario_id
                / variant
            )
            for variant in ("base", "left", "right")
        }
        expected_files = _java_files(
            REPO_ROOT / "output" / CANONICAL_TOOL / "expected" / scenario_id
        )
        all_files = set(expected_files)
        for files in variant_files.values():
            all_files.update(files)

        intent = MERGE_INTENTS[number]
        rows.append(
            {
                "scenario_id": scenario_id,
                "title": title,
                "mapping": mapping,
                "change_type": _required(source, "change_type"),
                "origin": _required(source, "origin"),
                "base_description": _variant_description(
                    "Common ancestor", title, variant_files["base"]
                ),
                "left_description": _variant_description(
                    "Left branch", title, variant_files["left"]
                ),
                "right_description": _variant_description(
                    "Right branch", title, variant_files["right"]
                ),
                "merge_intent": intent,
                "acceptance_criteria": (
                    f"The normalized output tree must contain exactly "
                    f"{_display_files(expected_files)}, match the workflow-"
                    f"confirmed oracle, contain no conflict markers, pass the "
                    f"preregistered syntax check, and satisfy this intent: {intent}"
                ),
                "base_files": _serialize_files(variant_files["base"]),
                "left_files": _serialize_files(variant_files["left"]),
                "right_files": _serialize_files(variant_files["right"]),
                "expected_files": _serialize_files(expected_files),
                "artifact_file_count": len(all_files),
                "logical_element_count": _provisional_element_count(mapping),
                "logical_elements": title,
                "dependency_scope": _dependency_scope(mapping),
                "validation_scope": "textual_structural_only",
                "associated_tests": "not_applicable",
                "mapping_basis": _required(source, "mapping_basis"),
                "change_type_basis": _required(source, "change_type_basis"),
                "oracle_review_status": source.get(
                    "oracle_review_status", "pending_independent_review"
                ),
                "classification_status": _required(
                    source, "classification_status"
                ),
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str | int]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _java_files(root: Path) -> tuple[str, ...]:
    if not root.is_dir():
        raise FileNotFoundError(f"Missing artifact directory: {root}")
    return tuple(
        sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*.java")
            if path.is_file()
        )
    )


def _serialize_files(files: tuple[str, ...]) -> str:
    return ";".join(files)


def _display_files(files: tuple[str, ...]) -> str:
    return "[" + ", ".join(files) + "]"


def _variant_description(label: str, title: str, files: tuple[str, ...]) -> str:
    return f"{label} for the controlled '{title}' scenario; Java tree: {_display_files(files)}."


def _provisional_element_count(mapping: str) -> int:
    return {"1:1": 1, "1:N": 2, "N:N": 4}[mapping]


def _dependency_scope(mapping: str) -> str:
    return {
        "1:1": "single_logical_correspondence",
        "1:N": "one_to_multiple_correspondence",
        "N:N": "multiple_interdependent_correspondences",
    }[mapping]


def _required(row: dict[str, str | None], field: str) -> str:
    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"Manifest field is blank: {field}")
    return value.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the enriched scenario manifest")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = build_manifest_rows(args.manifest)
    output = args.output or args.manifest
    write_manifest(rows, output)
    print(f"Wrote {len(rows)} enriched scenario records to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
