# Controlled benchmark for Java merge tools

Replication package for a controlled, synthetic benchmark comparing FSTMerge,
IntelliMerge, and JDime on 39 three-way Java merge scenarios. The experimental
unit is one `tool_name × scenario_id` pair, yielding exactly 117 observations.

The repository is undergoing a preregistered resubmission correction. Results
under `evaluation_results/scientific_evaluation/` were produced by the legacy
pipeline and are retained only for traceability; they are not current evidence.
Only a run marked `canonical_release` that passes `scripts.phase4_gate` may be
used in the revised manuscript.

## Study scope

- Population: 39 controlled/synthetic scenarios, not mined real-world merges.
- Tools: FSTMerge, IntelliMerge, and JDime.
- Inputs: `base`, `left`, and `right` trees under `scenarios_base/`.
- Oracles: reviewed output trees under `output/<tool>/expected/`.
- Primary content metrics: path-aware, multiplicity-preserving precision,
  recall, and F1.
- Order metric: per-file longest-common-subsequence agreement.
- Complete textual resolution: clean execution, exact oracle equality, and no
  Java parser diagnostic. This is not a behavioral-correctness claim.
- JDime configuration: structured mode only; automatic unstructured fallback
  is disabled.

The normative definitions are in [PROTOCOL.md](PROTOCOL.md). Scenario labels
and their operational rules are in [TAXONOMY.md](TAXONOMY.md), and the oracle
review provenance is in [ORACLE_VALIDATION.md](ORACLE_VALIDATION.md).

## Repository map

```text
data/
  scenario_manifest.csv       39 scenario definitions and confirmed labels
  oracle_reviews.csv          review rounds and decisions
  oracle_inventory.csv        per-file oracle hashes and technical checks
scenarios_base/<tool>/         base/left/right inputs
output/<tool>/expected/        accepted oracle trees
scripts/
  revised_experiment.py        canonical execution/evaluation harness
  phase2_gate.py               metadata/oracle release gate
  phase3_gate.py               environment and tool-artifact gate
  phase4_gate.py               117-row result integrity gate
  phase4_audit.py              audit selection and determinism comparison
tests/                         evaluator and gate regression tests
tool_versions.lock             frozen commits, artifacts, hashes, JDKs, policy
evaluation_results/
  revised_experiment/          isolated diagnostic/canonical run directories
```

The older `executor.py`, `run_evaluation.py`, `merge_evaluation_tool.py`, and
`scientific_report_generator.py` remain only to reproduce the original state.
Do not use them for the resubmission.

## Frozen environment

Canonical execution targets Linux x86_64 (native or WSL2) and uses:

| Component | Frozen version |
|---|---|
| Python | 3.8 or newer |
| IntelliMerge | tag 1.0.9, release JAR SHA-256 in lockfile |
| FSTMerge/FeatureHouse | commit `81724157bc638524e72af5bb689cf939e6df8599` |
| JDime | commit `dc3d2eeacf0bb0980994b980bcb11c630300c4f3` |
| Merge-tool runtime | Eclipse Temurin 21.0.11+10 |
| JDime runtime | Eclipse Temurin 8u392-b08 |

`setup.py` downloads/builds these exact resources, validates published archive
hashes and tool hashes, and checks out detached commits. AutoMerge is not a
prerequisite and is not evaluated.

Because JDime is built locally, its release identity is the canonical hash of
the JAR entry names and uncompressed contents, which ignores ZIP container
metadata. The frozen value was reproduced before and after a clean build on
the Linux x86_64 target; the raw Linux JAR hash is retained as supplementary
provenance in `tool_versions.lock`.

System prerequisites on Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git tar ca-certificates default-jre
```

## Canonical reproduction

From the repository root on Linux x86_64:

```bash
python3 setup.py
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m scripts.phase2_gate
python -m scripts.phase3_gate --release
python -m scripts.revised_experiment --release \
  --run-dir evaluation_results/revised_experiment/canonical_run_3
python -m scripts.phase4_gate \
  evaluation_results/revised_experiment/canonical_run_3
```

The release command fails before creating results unless the full 3 × 39
matrix, exact artifacts, per-tool Java runtimes, and Linux target pass the
environment gate. A run directory must not already exist; this prevents stale
outputs from being reused.

For an instrumentation-only smoke run, omit `--release` and select cells:

```bash
python -m scripts.revised_experiment \
  --tool FSTMerge --scenario scenario_1 \
  --run-dir evaluation_results/revised_experiment/my_diagnostic
```

Diagnostic runs are marked in `run_metadata.json` and cannot pass the default
Phase 4 gate. They must never be mixed with publication data.

The accepted canonical source is `canonical_run_3`. Its 85-cell
Codex-assisted, author-supervised evidence inspection is recorded in
`manual_audit.csv`. Phase 4 is released only after the preregistered 27-cell
high-risk repeat has been compared and the final gate passes:

```bash
python -m scripts.phase4_audit compare-sample \
  evaluation_results/revised_experiment/canonical_run_3 \
  evaluation_results/revised_experiment/determinism_high_risk_1 \
  --output evaluation_results/revised_experiment/canonical_run_3/determinism_high_risk.csv
python -m scripts.phase4_gate --final \
  evaluation_results/revised_experiment/canonical_run_3
```

## Run outputs

Each run contains:

- `run_metadata.json`: lockfile snapshot, declared matrix, run kind, and host;
- `executions.csv`: one terminal execution record per requested cell;
- `scenario_tool_results.csv`: labels and applicable evaluation metrics;
- `status_counts.json`: terminal-state counts;
- `attempts/<tool>/<scenario>/`: command logs, raw output, normalized output,
  isolated FSTMerge input, and syntax evidence where applicable.

Terminal states are mutually exclusive: `completed_clean`,
`completed_conflicted`, `invalid_output`, `crash`, `timeout`, and
`setup_error`. Failures remain missing metrics; they are not silently converted
to F1 = 0.

See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for column-level definitions.

## Validation status

- Phase 2: complete; see [PHASE2_STATUS.md](PHASE2_STATUS.md).
- Phase 3: complete; the frozen Linux release gate passed before canonical run
  3; see [PHASE3_STATUS.md](PHASE3_STATUS.md).
- Phase 4: canonical run 3 passes the 117-cell integrity gate and its evidence
  inspection is complete; only the frozen determinism repeat remains; see
  [PHASE4_STATUS.md](PHASE4_STATUS.md) and [PHASE4_AUDIT.md](PHASE4_AUDIT.md).
- Phases 5 and 8 result-dependent content must wait for the final Phase 4 gate.

Run all repository tests with:

```bash
python -m unittest discover -s tests -v
```

## Provenance and limitations

The scenario origin is `synthetic_controlled`. Claims must therefore be limited
to this benchmark; external validity to mined project histories has not been
established. The oracle review record accurately identifies the Codex-assisted
review rounds and must not be described as two independent human experts.

No dataset/software license has yet been selected by the authors. Reuse rights
must not be inferred until a license file is added. Citation metadata should be
finalized together with the revised manuscript author list and publication
details.

Repository: <https://github.com/MateusMunaro/Empirical-Analysis-Of-Merge-Tools>
