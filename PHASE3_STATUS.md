# Phase 3 status — frozen environment and auditable harness

Last automated audit: `2026-08-12`

## Frozen decisions

- Unit of analysis: one `tool_name × scenario_id` observation (117 total).
- Timeout: 120 wall-clock seconds per attempt.
- JDime: structured mode only; unstructured fallback disabled.
- Failures remain `setup_error`, `crash`, `timeout`, or `invalid_output`; they
  are never silently changed to F1 = 0 in the primary analysis.
- Raw and normalized outputs are retained separately.
- Output directories are new and empty for every attempt.
- Java artifact paths are preserved as declared logical paths; ambiguous
  duplicate basenames invalidate the output instead of being overwritten.
- Syntax evidence uses `javac -proc:none -XDrawDiagnostics` and considers only
  parser diagnostics. It is not reported as compilation evidence.

The authoritative versions, commits, commands, runtime archives, and checksums
are in `tool_versions.lock`.

## Implemented harness

`scripts/revised_experiment.py`:

- continues after individual failures;
- writes `executions.csv` and `scenario_tool_results.csv`;
- records command, timestamps, duration, exit code, stdout/stderr, versions,
  environment, and input/oracle/output checksums;
- applies the Phase 1 path-aware multiset and sequence metrics only to readable
  produced outputs;
- validates matrix completeness before releasing CSVs.

`scripts/phase3_gate.py` has two levels:

```powershell
python -m scripts.phase3_gate
python -m scripts.phase3_gate --release
```

The development gate validates the lockfile, harness, and locally available
IntelliMerge/FSTMerge artifacts. The release gate additionally requires a
built, hashed JDime artifact and the frozen Linux x86_64 environment.

## Current host

- Windows 11 x64;
- Python 3.12.3;
- Oracle Java 24;
- frozen Temurin 8 and 21 Linux runtimes not installed on this Windows host;
- IntelliMerge 1.0.9 artifact present and checksum verified;
- FeatureHouse/FSTMerge commit `81724157bc638524e72af5bb689cf939e6df8599`
  artifact present and checksum verified;
- JDime source fixed at commit
  `dc3d2eeacf0bb0980994b980bcb11c630300c4f3`; the Gradle distribution build
  completed. The canonical Linux x86_64 build was reproduced with
  `clean installDist`; its raw SHA-256 is
  `2c87fb916cb2d99d843085bb30d27da92004e503b4dbeb00bcdb251bfdd867af`
  and its metadata-independent ZIP-content SHA-256 is
  `db7dacfbae08c2ab68b18826e4bc0249e1982cbfd5fc7bd3a02b69a8292887aa`.
  The Windows build is intentionally not accepted as a release artifact.

The development gate passes here. The release gate remains closed because the
frozen target is Linux x86_64 and its provisioned Temurin runtimes are absent.
Both registered user distributions (`Ubuntu` and `kali-linux`) fail to start:
their registered `ext4.vhdx` files are missing
(`Wsl/Service/CreateInstance/MountDisk/HCS/ERROR_FILE_NOT_FOUND`). Therefore a
Windows run can be diagnostic only and must not be presented as publication
data. The canonical 117-attempt run must be completed in a working Linux/WSL2
environment after `python setup.py`.

## Smoke evidence

- IntelliMerge/scenario_1 exited successfully but produced only refactoring
  metadata and no Java artifact; the harness recorded `invalid_output`.
- FSTMerge/scenario_1 produced a readable tree; all three files were retained,
  including two extras relative to the oracle, and metrics were computed over
  the complete tree.

These smoke results validate instrumentation only. They are not publication
results and must not be mixed with the canonical Phase 4 dataset.
