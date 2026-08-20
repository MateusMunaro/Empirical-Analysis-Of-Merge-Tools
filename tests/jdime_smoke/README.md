# JDime structured-merge smoke tests

These fixtures are deliberately small and are **not** part of the 39-scenario
benchmark. They check whether the JDime installation can perform the basic
forms of merge that its structured strategy supports before it is used on the
benchmark.

| Fixture | Input form | Expected diagnostic result |
|---|---|---|
| `01_file_non_overlapping` | Three individual `Person.java` files | One non-empty merged Java file; the independent `email` field and `getName` method should both appear. |
| `02_file_conflict` | Three individual `Greeting.java` files | One Java file containing a JDime conflict. A non-zero exit code up to 127 is expected when `--stats` reports conflicts. |
| `03_directory_same_paths` | Three directories with identical relative paths | A non-empty output tree containing `src/Person.java` and `src/Audit.java`; independent changes to `Person` should both appear. |
| `04_directory_renamed_file` | Three directories whose Java filenames differ | Diagnostic boundary case. It is expected to reveal how this JDime version handles a rename; it is not a required successful merge. |

Run the suite from the repository root on Linux/WSL:

```bash
export JDIME_JAVA_HOME=/path/to/temurin-8
bash tests/jdime_smoke/run_jdime_smoke_tests.sh
```

The script searches for the JDime launcher in
`merge_tools/JDime/jdime/build/install/JDime/bin/JDime`. Override it with
`JDIME_BIN=/absolute/path/to/JDime` if necessary. Each execution uses:

```text
-f --mode structured --exit-on-error --stats --log-level FINE
```

Directory fixtures additionally use `--recursive`. Outputs and separate
stdout/stderr logs are written to `tests/jdime_smoke/results/`, which is
recreated on every run. The launcher is executed with its own `bin` directory
as the working directory, as required by JDime's README.

The script reports process exit code, generated Java files, and a compact
content check. Inspect the retained logs before drawing conclusions from an
empty output.
