# Empirical Analysis of Merge Tools

> An empirical study comparing the effectiveness of structured and semi-structured merge tools on a curated benchmark of three-way merge scenarios written in Java.

This repository contains the **dataset**, **execution scripts**, **evaluation framework**, and **results** of an empirical analysis that quantitatively compares the merge correctness of multiple academic merge tools across a controlled set of conflict scenarios.

---

## Table of Contents

1. [Research Overview](#research-overview)
2. [Repository Layout](#repository-layout)
3. [Dataset](#dataset)
4. [Evaluated Tools](#evaluated-tools)
5. [Reproducing the Study](#reproducing-the-study)
   - [1. Prerequisites](#1-prerequisites)
   - [2. Clone & Setup](#2-clone--setup)
   - [3. Provision the Merge Tools](#3-provision-the-merge-tools)
   - [4. Run the Merges](#4-run-the-merges)
   - [5. Evaluate the Results](#5-evaluate-the-results)
   - [6. Generate the Report](#6-generate-the-report)
6. [Manual Tool Invocation (reference)](#manual-tool-invocation-reference)
7. [Evaluation Methodology](#evaluation-methodology)
8. [Results Summary](#results-summary)
9. [Extending the Study](#extending-the-study)
10. [Troubleshooting](#troubleshooting)
11. [Citation](#citation)
12. [Author & Contact](#author--contact)

---

## Research Overview

The goal of the study is to answer the research question:

> *How do structured, semi-structured, and unstructured merge tools compare in correctness across a controlled set of three-way merge scenarios?*

To answer this we:

1. Built a benchmark of **39 three-way merge scenarios** per tool (base / left / right) with a known *expected* resolution (ground truth).
2. Executed each tool over the benchmark using a uniform Python harness.
3. Compared each tool's output against the ground truth using line-level metrics (precision, recall, F1, accuracy) and quality classifications.
4. Aggregated the per-scenario results into a comparative report with statistical commentary.

The benchmark and all intermediate artefacts are kept in the repository so the study is fully reproducible.

---

## Repository Layout

```
Empirical-Analysis-Of-Merge-Tools/
├── scripts/                              # Python harness (execution + evaluation)
│   ├── executor.py                       # Interactive runner for the merge tools
│   ├── run_evaluation.py                 # Orchestrates the evaluation pipeline
│   ├── merge_evaluation_tool.py          # Core evaluation engine (metrics, reports)
│   ├── scientific_report_generator.py    # Builds the academic-style report
│   ├── evaluation_config.py              # Data classes & evaluation configuration
│   └── demo_complete_evaluation.py       # Guided end-to-end demonstration
│
├── scenarios_base/                       # Input dataset (39 scenarios per tool)
│   ├── FSTMerge/scenario_1 .. scenario_39/   (base/, left/, right/, merge.expression)
│   ├── IntelliMerge/scenario_1 .. scenario_39/   (base/, left/, right/)
│   ├── JDime/scenario_1 .. scenario_39/          (base/, left/, right/)
│   └── KDiff3/                                  (single illustrative sample)
│
├── merge_tools/                          # Tool binaries (some are gitignored — see below)
│   ├── JDime/                            # JDime distribution (committed)
│   └── KDiff/                            # KDiff3 reference notes
│   # FSTMerge / IntelliMerge / AutoMerge JARs are gitignored — see "Provision the Merge Tools"
│
├── output/                               # Tool outputs + ground-truth expected outputs
│   ├── FSTMerge/{scenarios,expected}/
│   ├── IntelliMerge/{scenarios,expected}/
│   └── JDime/{scenarios,expected}/
│
├── evaluation_results/                   # Generated metrics, comparisons and report
│   └── scientific_evaluation/
│       ├── tools_comparison.json
│       ├── scientific_merge_tools_evaluation.md
│       ├── FSTMerge/{evaluation_report.json, scenario_metrics.csv}
│       ├── IntelliMerge/{evaluation_report.json, scenario_metrics.csv}
│       └── JDime/{evaluation_report.json, scenario_metrics.csv}
│
├── .gitignore
└── README.md
```

> **Note on the project name.** The harness and some legacy paths still refer to a previous project name (`Pesquisa-cientifica`). The current canonical name of the repository is **`Empirical-Analysis-Of-Merge-Tools`**. Replace any absolute path you might find in older scripts/notes with the path of your local clone.

---

## Dataset

The dataset lives in [`scenarios_base/`](./scenarios_base). Each scenario is a self-contained three-way merge:

```
scenarios_base/<Tool>/scenario_N/
├── base/    # common ancestor
├── left/    # branch A (e.g. ours)
└── right/   # branch B (e.g. theirs)
```

For **FSTMerge**, each scenario additionally contains a `merge.expression` file consumed by FeatureHouse.

The reference (expected) merge result for each scenario lives under [`output/<Tool>/expected/scenario_N/`](./output) and is the ground truth used to score each tool.

| Tool         | # Scenarios | Input layout                          | Expected output             |
|--------------|-------------|---------------------------------------|-----------------------------|
| FSTMerge     | 39          | `base/`, `left/`, `right/`, `merge.expression` | `output/FSTMerge/expected/` |
| IntelliMerge | 39          | `base/`, `left/`, `right/`            | `output/IntelliMerge/expected/` |
| JDime        | 39          | `base/`, `left/`, `right/`            | `output/JDime/expected/`    |
| KDiff3       | 1 (sample)  | `base/`, `left/`, `right/`            | not part of the formal evaluation |

---

## Evaluated Tools

| Tool         | Strategy                       | Language target | Notes |
|--------------|--------------------------------|-----------------|-------|
| **FSTMerge**     | Structured (FST / FeatureHouse) | Java            | Requires a `merge.expression` per scenario. |
| **IntelliMerge** | Semantic / refactoring-aware   | Java            | Operates on directories (`-d left base right`). |
| **JDime**        | Structured AST merge (with linebased fallback) | Java | Needs JDK 8 (`JAVA_HOME`). Provisioned by `setup.py`. |
| **KDiff3**       | Line-based three-way merge     | Any text        | Used only as an illustrative reference. |

The full quantitative comparison covers **FSTMerge**, **IntelliMerge** and **JDime**, which are the three tools with a complete dataset and ground truth in this repository.

---

## Reproducing the Study

### 1. Prerequisites

The setup script needs the following on a fresh Linux machine (WSL2 also works for Windows users):

| Component       | Used for                                                       |
|-----------------|----------------------------------------------------------------|
| Python 3.8+     | Running the harness and the setup script                       |
| `git`           | Cloning JDime and FeatureHouse during provisioning             |
| A system JRE    | Running JDime's Gradle wrapper while building it from source   |
| `tar`           | Extracting the Temurin JDK 8 archive                           |

On Debian/Ubuntu the prerequisites can be installed with:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git default-jre tar ca-certificates
```

- `python3-venv` is required by `python3 -m venv` on Debian/Ubuntu.
- `ca-certificates` is required for `urllib` to download artifacts from GitHub over HTTPS.
- If you are behind a corporate proxy, export `HTTPS_PROXY` / `HTTP_PROXY` **before** running `setup.py` — `urllib`, `git`, and `pip` all honour these variables.

Everything else — IntelliMerge, FeatureHouse, JDK 8, and a freshly built JDime — is provisioned automatically by [`setup.py`](./setup.py) (see step 3).

> **Moving the repo from Windows to Linux?** Do **not** copy the `merge_tools/JDime/jdime/` folder across — `setup.py` will clone it fresh on the Linux side, avoiding CRLF line endings in `gradlew` (which would otherwise fail with `bad interpreter: /bin/sh^M`).

### 2. Clone the Repository

```bash
git clone https://github.com/MateusMunaro/Empirical-Analysis-Of-Merge-Tools.git
cd Empirical-Analysis-Of-Merge-Tools
```

All commands in the rest of this guide assume your **current working directory is the repository root**. The harness now resolves every path relative to the repository, so it can be invoked from any directory once setup is complete.

### 3. Provision the Merge Tools (automated)

Run the setup script once. It is idempotent — re-running it skips steps that are already done:

```bash
python3 setup.py
```

What it installs, under the repository:

```
.venv/                                                          # Python deps (numpy, pandas, ...)
merge_tools/IntelliMerge/IntelliMerge-1.0.9-all.jar             # downloaded from GitHub Releases
merge_tools/FSTMerge/featurehouse_20220107.jar                  # extracted from joliebig/featurehouse
java_dependencies/java-versions/jdk8u392-b08/                   # Adoptium Temurin JDK 8 (used by JDime)
merge_tools/JDime/jdime/build/install/JDime/bin/JDime           # built from se-sic/jdime via Gradle
```

Useful flags:

```bash
python3 setup.py --check          # only verify, install nothing
python3 setup.py --force          # reinstall everything from scratch
python3 setup.py --skip jdime     # skip a specific step
```

Activate the virtualenv before running any other script:

```bash
source .venv/bin/activate
```

> **AutoMerge note.** The harness no longer ships an `AutoMerge` option. The headline benchmark (FSTMerge / IntelliMerge / JDime) is fully covered by `setup.py`.

### 4. Run the Merges

The harness (`scripts/executor.py`) provides an interactive menu that runs **all 39 scenarios** for the selected tool, normalises the output layout, and reports per-scenario success/failure.

```bash
python scripts/executor.py
```

Menu:

```
1 - IntelliMerge
2 - FSTMerge
3 - JDime
```

Outputs are written to:

```
output/<Tool>/scenarios/scenario_N/...
```

Run the harness once per tool (or invoke the underlying functions directly from a Python REPL).

### 5. Evaluate the Results

Once `output/<Tool>/scenarios/` is populated for each tool, score them against the ground truth in `output/<Tool>/expected/`:

```bash
# Sanity-check that the expected/ and scenarios/ folders are well-formed
python scripts/run_evaluation.py --check-only

# Run the full evaluation (all tools that have data)
python scripts/run_evaluation.py

# Restrict to a subset
python scripts/run_evaluation.py --tools IntelliMerge JDime

# Re-aggregate from cached results without recomputing
python scripts/run_evaluation.py --summary-only

# Verbose logging
python scripts/run_evaluation.py --verbose
```

Outputs land in `evaluation_results/scientific_evaluation/`:

```
evaluation_results/scientific_evaluation/
├── tools_comparison.json                 # Cross-tool comparative summary
├── scientific_merge_tools_evaluation.md  # Human-readable academic report
└── <Tool>/
    ├── evaluation_report.json            # Aggregated metrics + per-scenario detail
    └── scenario_metrics.csv              # One row per scenario, ready for stats tools
```

### 6. Generate the Report

```bash
# Build the markdown academic report
python scripts/scientific_report_generator.py
```

### Guided demo (optional)

For a narrated end-to-end walk-through (data check → evaluation → report → summary):

```bash
python scripts/demo_complete_evaluation.py
```

---

## Manual Tool Invocation (reference)

These are the underlying commands the harness wraps. Useful for debugging a single scenario. All paths are relative to the repository root.

### FSTMerge

```bash
java -jar ./merge_tools/FSTMerge/featurehouse_20220107.jar \
  --expression    ./scenarios_base/FSTMerge/scenario_1/merge.expression \
  --base-directory ./scenarios_base/FSTMerge/scenario_1
```

### IntelliMerge

```bash
java -jar ./merge_tools/IntelliMerge/IntelliMerge-1.0.9-all.jar \
  -d ./scenarios_base/IntelliMerge/scenario_12/left \
     ./scenarios_base/IntelliMerge/scenario_12/base \
     ./scenarios_base/IntelliMerge/scenario_12/right \
  -o ./output/IntelliMerge/scenarios/scenario_12
```

### JDime (structured, with unstructured fallback)

```bash
JAVA_HOME=./java_dependencies/java-versions/jdk8u392-b08 \
./merge_tools/JDime/jdime/build/install/JDime/bin/JDime \
  -f --mode structured \
  --output ./output/JDime/scenarios/scenario_12 \
  ./scenarios_base/JDime/scenario_12/left \
  ./scenarios_base/JDime/scenario_12/base \
  ./scenarios_base/JDime/scenario_12/right
```

### KDiff3 (illustrative, line-based)

```bash
kdiff3 \
  ./scenarios_base/KDiff3/base/SimpleClass.java \
  ./scenarios_base/KDiff3/left/SimpleClass.java \
  ./scenarios_base/KDiff3/right/SimpleClass.java \
  -m --batch -o ./output/KDiff3/output.java
```

---

## Evaluation Methodology

### Metrics

For each scenario the framework compares the tool's output against the expected resolution and computes:

| Metric              | Definition                                                    |
|---------------------|---------------------------------------------------------------|
| **Precision**       | Correct lines in output / Total lines in output               |
| **Recall**          | Correct lines in output / Total lines expected                |
| **F1-Score**        | Harmonic mean of precision and recall                         |
| **Accuracy**        | Overall correctness percentage                                |
| **Success rate**    | Fraction of scenarios where the tool produced an output       |
| **Reliability**     | Fraction of scenarios producing usable (non-failed) results   |

Scenarios are normalised before comparison (whitespace collapsing) and then classified by quality:

| Class       | Threshold (F1) |
|-------------|----------------|
| Perfect     | 100%           |
| Excellent   | ≥ 95%          |
| Good        | ≥ 85%          |
| Acceptable  | ≥ 70%          |
| Poor        | ≥ 50%          |
| Failed      | < 50%          |

### Pipeline

```
load expected outputs ──┐
                        ├──► per-scenario diff ──► metrics ──► classification
load tool outputs ──────┘                                              │
                                                                       ▼
                                aggregate per tool ──► compare tools ──► report
```

### Statistical commentary

The comparative report (`tools_comparison.json`) reports pairwise F1 differences and flags potentially significant gaps. The shipped numbers are descriptive; for publication-grade significance testing, run a Mann-Whitney U / Wilcoxon rank-sum test over the per-scenario F1 column in `scenario_metrics.csv`.

---

## Results Summary

The currently committed evaluation (3 tools, 68 evaluated scenarios in total — see `evaluation_results/scientific_evaluation/tools_comparison.json`) ranks the tools as follows:

| Rank | Tool         | Overall F1 | Success rate | Reliability |
|------|--------------|------------|--------------|-------------|
| 1    | IntelliMerge | 0.704      | 0.667        | 0.833       |
| 2    | JDime        | 0.695      | 0.710        | 0.774       |
| 3    | FSTMerge     | 0.574      | 0.574        | 0.632       |

Quality distribution (fraction of scenarios in each class):

| Tool         | Perfect | Acceptable | Poor  | Failed |
|--------------|---------|------------|-------|--------|
| IntelliMerge | 0.667   | 0.000      | 0.056 | 0.278  |
| JDime        | 0.581   | 0.129      | 0.016 | 0.274  |
| FSTMerge     | 0.574   | 0.000      | 0.000 | 0.426  |

Pairwise F1 gaps (descriptive, not yet formally tested):

- FSTMerge vs IntelliMerge: **Δ = 0.130** (potentially significant)
- FSTMerge vs JDime:        **Δ = 0.121** (potentially significant)
- IntelliMerge vs JDime:    **Δ = 0.009** (likely not significant)

The full report is at [`evaluation_results/scientific_evaluation/scientific_merge_tools_evaluation.md`](./evaluation_results/scientific_evaluation/scientific_merge_tools_evaluation.md).

---

## Extending the Study

### Add a new scenario

1. Create `scenarios_base/<Tool>/scenario_N/{base,left,right}/`.
2. (FSTMerge only) Add the matching `merge.expression`.
3. Drop the ground-truth resolution under `output/<Tool>/expected/scenario_N/`.
4. If `N > 39`, update the loop bounds in `scripts/executor.py` accordingly.

### Add a new merge tool

1. Place the binary/JAR under `merge_tools/<NewTool>/`.
2. Add a `run_<newtool>()` function in `scripts/executor.py` following the existing patterns (path setup → `subprocess.run` → output relocation).
3. Add the new option to the menu in `main()`.
4. Mirror the dataset under `scenarios_base/<NewTool>/` and the ground truth under `output/<NewTool>/expected/`.
5. Re-run `scripts/run_evaluation.py` — the framework auto-detects tools that have both `scenarios/` and `expected/`.

### Add a new metric

1. Extend the `ScenarioMetrics` dataclass in `scripts/evaluation_config.py`.
2. Implement the calculation in `scripts/merge_evaluation_tool.py`.
3. Surface the new metric in `scripts/scientific_report_generator.py`.

---

## Troubleshooting

**Wrong Java version**
```bash
echo $JAVA_HOME       # JDK 8 expected for JDime
java -version
```
`setup.py` provisions Temurin JDK 8 under `java_dependencies/java-versions/jdk8u392-b08/` and `executor.py` points `JAVA_HOME` at it automatically when invoking JDime.

**Setup script reports a step failed**
Re-run `python3 setup.py` — the script is idempotent and resumes from the failed step. Use `--force` to redo a step from scratch, or `--check` to inspect what is missing without installing anything.

**JDime structured mode fails on a scenario**
The harness automatically falls back to `--mode unstructured`. The summary at the end of `run_jdime()` lists the affected scenarios.

**Permission denied on JDime launcher**
```bash
chmod +x ./merge_tools/JDime/jdime/build/install/JDime/bin/JDime
```

**`gradlew: bad interpreter: /bin/sh^M` while building JDime**
The `gradlew` script has CRLF line endings (typically from a Windows checkout). Fix with:
```bash
sed -i 's/\r$//' merge_tools/JDime/jdime/gradlew
```
Or delete `merge_tools/JDime/jdime/` and rerun `python3 setup.py` so it re-clones with native line endings.

**`setup.py` cannot reach GitHub / Foojay (Gradle toolchain)**
Building JDime requires network access for both `git clone` and the Foojay resolver, which downloads the JDK 8 toolchain the first time it runs. Behind a proxy, export `HTTPS_PROXY` and `HTTP_PROXY` before running `setup.py`.

**`output/` folder structure missing**
```bash
mkdir -p output/{FSTMerge,IntelliMerge,JDime}/{scenarios,expected}
```

**Legacy `/workspaces/Pesquisa-cientifica` paths**
Older snippets reference the previous project location. Replace with `.` (the repo root) — every script in this release uses relative paths.

---

## Citation

If you use this dataset or framework in academic work, please cite:

```bibtex
@misc{munaro_merge_tools_2025,
  title  = {Empirical Analysis of Merge Tools: A Reproducible Benchmark for Structured and Semi-structured Java Merging},
  author = {Mateus Munaro},
  year   = {2025},
  howpublished = {\url{https://github.com/MateusMunaro/Empirical-Analysis-Of-Merge-Tools}}
}
```

---

## Author & Contact

- **Mateus Munaro** — research design, dataset curation, harness and evaluation framework.
- GitHub: [@MateusMunaro](https://github.com/MateusMunaro)
- Email: `MateusSouza2@edu.unisinos.br`

Issues and pull requests are welcome — particularly for: additional merge tools (e.g. `git-merge`, Spork, JDime variants), additional scenarios, or non-Java language support.
