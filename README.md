# Empirical Evaluation of Java Merge Tools

Reproducibility package for a controlled benchmark of **FSTMerge**, **IntelliMerge**, and **JDime** across 39 synthetic three-way Java merge scenarios. The frozen experiment contains 117 observations: one for every `tool_name x scenario_id` pair.

This document is the single maintained guide for installing the toolchain, running the evaluation, validating a run, interpreting the generated evidence, and reviewing the benchmark oracles.

## What this benchmark evaluates

Each scenario provides a common ancestor (`base`) and two independently changed variants (`left` and `right`). Every merge-tool output is normalized and compared with a reviewed expected output tree.

The evaluation records:

- path-aware, multiplicity-preserving precision, recall, and F1;
- per-file longest-common-subsequence order agreement;
- exact oracle equality;
- conflict-marker presence and parser diagnostics;
- execution time and one mutually exclusive terminal status.

The terminal statuses are `completed_clean`, `completed_conflicted`, `invalid_output`, `crash`, `timeout`, and `setup_error`. Missing or unavailable metrics remain missing; failures are never silently converted to an F1 score of zero.

"Complete textual resolution" means that execution completed cleanly, the normalized output exactly matched the oracle, and the Java syntax check emitted no parser diagnostic. It is not a claim of behavioral equivalence or semantic correctness.

## Frozen environment

Canonical release runs target **Linux x86_64**, either natively or through WSL2. The setup is intentionally rejected on other platforms.

| Component | Frozen version |
| --- | --- |
| Python | 3.8 or newer |
| IntelliMerge | 1.0.9 |
| FSTMerge / FeatureHouse | commit `81724157bc638524e72af5bb689cf939e6df8599` |
| JDime | commit `dc3d2eeacf0bb0980994b980bcb11c630300c4f3` |
| IntelliMerge and FSTMerge runtime | Eclipse Temurin 21.0.11+10 |
| JDime runtime | Eclipse Temurin 8u392-b08 |

Exact artifact locations, download URLs, checksums, runtime arguments, the 120-second timeout, and the execution policy are frozen in `tool_versions.lock`. JDime runs in recursive structured mode with `--accept-non-java` and `--exit-on-error`; automatic unstructured fallback is disabled.

## Prerequisites

On Debian or Ubuntu, install the host tools from a terminal:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git tar ca-certificates default-jre
```

The initial setup downloads approximately two JDKs, IntelliMerge, FeatureHouse, and the JDime source tree. Internet access and several gigabytes of free disk space are recommended. Run every command below from the repository root.

## Run the complete evaluation

Choose a new output directory. It must not already exist, which prevents stale artifacts from being mixed into a run.

```bash
python3 setup.py
source .venv/bin/activate
python -m scripts.run_replication \
  --skip-setup \
  --run-dir evaluation_results/revised_experiment/my_release_run
```

The orchestrator performs the following sequence:

1. runs the complete regression suite;
2. validates scenario metadata and oracle-review evidence;
3. validates the operating system, Java runtimes, frozen commits, and artifact hashes;
4. executes all 117 tool-scenario cells;
5. checks the integrity of the released result matrix;
6. generates the descriptive tables, figures, summary, and report.

Use a distinct run-directory name for every attempt. A timestamped name is convenient:

```bash
python -m scripts.run_replication \
  --skip-setup \
  --run-dir evaluation_results/revised_experiment/run_YYYYMMDD
```

Do not add `--skip-tests` unless the tests have already passed for the exact checkout and environment being evaluated.

## Verify each stage manually

The explicit workflow is useful for auditing failures or collecting individual gate output:

```bash
python3 setup.py
source .venv/bin/activate

python -m unittest discover -s tests -v
python -m scripts.phase2_gate
python -m scripts.phase3_gate --release

python -m scripts.revised_experiment --release \
  --run-dir evaluation_results/revised_experiment/my_release_run

python -m scripts.phase4_gate \
  evaluation_results/revised_experiment/my_release_run

python -m scripts.phase5_analysis \
  evaluation_results/revised_experiment/my_release_run/scenario_tool_results.csv \
  evaluation_results/revised_experiment/my_release_run/analysis \
  --run-root evaluation_results/revised_experiment/my_release_run \
  --oracle-root output
```

The Phase 4 command above validates a canonical computational run. The stricter `--final` gate additionally requires completed manual-audit and determinism evidence in the run directory:

```bash
python -m scripts.phase4_gate --final \
  evaluation_results/revised_experiment/my_release_run
```

A newly generated run will not pass `--final` until those review artifacts have been produced and completed.

## Run a fast diagnostic

To test instrumentation without executing the full matrix, select one or more tools and scenarios. Diagnostic runs are clearly marked and cannot be treated as canonical evidence.

```bash
source .venv/bin/activate
python -m scripts.revised_experiment \
  --tool FSTMerge \
  --scenario scenario_1 \
  --run-dir evaluation_results/revised_experiment/smoke_fstmerge_s1

python -m scripts.phase4_gate --allow-diagnostic \
  evaluation_results/revised_experiment/smoke_fstmerge_s1
```

Repeat `--tool` or `--scenario` to request multiple cells. Omitting `--release` always produces a diagnostic run, even when all defaults are selected.

## Inspect the results

Each run directory contains:

| Artifact | Purpose |
| --- | --- |
| `run_metadata.json` | Run kind, host environment, frozen lock snapshot, tools, and scenarios |
| `executions.csv` | Command, timing, exit information, logs, and terminal status for every cell |
| `scenario_tool_results.csv` | Master evaluation matrix and applicable metrics |
| `status_counts.json` | Aggregate terminal-state counts |
| `attempts/<tool>/<scenario>/` | Raw output, normalized output, command logs, isolated inputs, and syntax evidence |
| `analysis/analysis_summary.json` | Machine-readable analysis provenance and artifact index |
| `analysis/table_*.csv` | Overall, stratified, robustness, decomposition, and diff-example tables |
| `analysis/figure_*.png` and `analysis/figure_*.pdf` | Publication-oriented figures |
| `analysis/phase5_descriptive_analysis.md` | Generated human-readable analysis report |

The analysis report is generated output, not maintained repository documentation. Running Phase 5 can therefore create a Markdown file inside a new run directory.

Before using a run in research reporting, confirm all of the following:

```bash
python -m scripts.phase4_gate evaluation_results/revised_experiment/my_release_run
python -m unittest discover -s tests -v
python setup.py --check
```

Also verify that `run_metadata.json` declares `canonical_release`, lists all three tools and all 39 scenarios, and contains the expected lock snapshot.

## Repository structure

```text
data/
  scenario_manifest.csv        Scenario definitions, labels, and acceptance criteria
  oracle_reviews.csv           Reviewer decisions and provenance
  oracle_inventory.csv         Expected-file hashes and technical checks
scenarios_base/<tool>/         Base, left, and right input trees
output/<tool>/expected/        Accepted oracle trees
scripts/
  run_replication.py           Public end-to-end orchestrator
  workflows/                   Execution, validation gates, audit, and analysis
  core/                        Metrics, artifact hashes, and data models
  oracles/                     Oracle packet, ingestion, and validation utilities
  legacy/                      Superseded exploratory pipeline
tests/                         Regression and JDime smoke tests
evaluation_results/            Retained execution evidence and generated analyses
tool_versions.lock             Frozen environment and execution policy
```

Files under `scripts/legacy/` and `evaluation_results/scientific_evaluation/` are historical. They do not implement or constitute current release evidence.

## Oracle review and scenario taxonomy

The canonical metadata is `data/scenario_manifest.csv`. A scenario mapping describes logical correspondence across branches:

- `1:1`: one logical element maps to one counterpart;
- `1:n`: one logical element maps to multiple counterparts;
- `n:1`: multiple logical elements map to one counterpart;
- `n:m`: multiple elements correspond on both sides.

The `change_type` label describes the dominant intended change according to the manifest. Reviewers must judge the proposed oracle against the scenario's `merge_intent`, `acceptance_criteria`, declared file set, and available base/left/right artifacts. They must not inspect merge-tool outputs, scores, earlier decisions, or proposed labels before making an independent decision.

For each review row:

- complete every required field and use an ISO 8601 UTC timestamp;
- provide a substantive comment for a rejection or classification concern;
- use `tests_result=not_applicable` when `validation_scope=textual_structural_only`;
- use `compilation_result=not_run` unless a documented compilation fixture was actually executed;
- never infer compilation success from visual inspection;
- preserve earlier rounds and append validated decisions to `data/oracle_reviews.csv`.

Generate a blinded review packet with the oracle utilities only when conducting a new review round. The generated packet includes its own task-specific README and must be kept separate from tool outputs.

## Troubleshooting

### `setup.py` rejects the operating system

Use Linux x86_64 or WSL2. Windows-native and macOS runs are not canonical release environments.

### A tool or JDK is missing

Resume the idempotent setup and then verify it:

```bash
python3 setup.py
python3 setup.py --check
```

Use `python3 setup.py --force` only when a cached artifact is corrupt or its commit/hash does not match the lockfile; this deliberately rebuilds or downloads components.

### Phase 3 is blocked

Read every reported issue. Typical causes are the wrong platform, a missing JAR, an unexpected checksum, an incorrect Java major version, or a JDime build from the wrong commit. Do not bypass this gate for a release run.

### The run directory already exists

Choose a new directory. The evaluator refuses to reuse it by design.

### A diagnostic run fails Phase 4

Pass `--allow-diagnostic` when validating its structure. Only a full `--release` run may pass the canonical gate.

### Python cannot import analysis packages

Activate the environment created by setup:

```bash
source .venv/bin/activate
```

## Scientific scope and reuse

The benchmark population consists of controlled synthetic scenarios, not merges mined from production histories. Conclusions must remain scoped to this benchmark; external validity to real-world repositories has not been established. Oracle-review provenance must accurately distinguish independent human review from author-supervised or AI-assisted review.

No dataset or software license is currently declared in this repository. Do not infer reuse rights until the maintainers add a license file.

Repository: <https://github.com/MateusMunaro/Empirical-Analysis-Of-Merge-Tools>
