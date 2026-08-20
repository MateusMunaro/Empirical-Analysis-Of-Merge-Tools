#!/usr/bin/env bash
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FIXTURES_DIR="$ROOT_DIR/tests/jdime_smoke/fixtures"
RESULTS_DIR="$ROOT_DIR/tests/jdime_smoke/results"
JDIME_BIN="${JDIME_BIN:-$ROOT_DIR/merge_tools/JDime/jdime/build/install/JDime/bin/JDime}"

if [[ ! -x "$JDIME_BIN" ]]; then
  echo "JDime launcher not executable: $JDIME_BIN" >&2
  echo "Set JDIME_BIN to build/install/JDime/bin/JDime." >&2
  exit 2
fi

if [[ -n "${JDIME_JAVA_HOME:-}" ]]; then
  export JAVA_HOME="$JDIME_JAVA_HOME"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

if ! java -version 2>&1 | grep -qE 'version "1\.8\.|version "8\.'; then
  echo "JDime smoke tests require a Java 8 runtime. Set JDIME_JAVA_HOME." >&2
  java -version >&2 || true
  exit 2
fi

rm -rf "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR"
LAUNCH_DIR="$(cd "$(dirname "$JDIME_BIN")" && pwd)"

run_case() {
  local name="$1"
  local input_kind="$2"
  local out="$RESULTS_DIR/$name/output"
  local log_dir="$RESULTS_DIR/$name"
  local left="$FIXTURES_DIR/$name/left"
  local base="$FIXTURES_DIR/$name/base"
  local right="$FIXTURES_DIR/$name/right"
  local exit_code

  mkdir -p "$log_dir"
  if [[ "$input_kind" == "file" ]]; then
    left="$(find "$left" -maxdepth 1 -type f -name '*.java' -print -quit)"
    base="$(find "$base" -maxdepth 1 -type f -name '*.java' -print -quit)"
    right="$(find "$right" -maxdepth 1 -type f -name '*.java' -print -quit)"
    if [[ -z "$left" || -z "$base" || -z "$right" ]]; then
      echo "[$name] missing Java fixture file" >&2
      return 2
    fi
    out="$out.java"
    (
      cd "$LAUNCH_DIR"
      "$JDIME_BIN" -f --accept-non-java --mode structured --exit-on-error --stats --log-level FINE \
        --output "$out" "$left" "$base" "$right"
    ) >"$log_dir/stdout.log" 2>"$log_dir/stderr.log"
  else
    (
      cd "$LAUNCH_DIR"
      "$JDIME_BIN" -f --accept-non-java --mode structured --recursive --exit-on-error --stats --log-level FINE \
        --output "$out" "$left" "$base" "$right"
    ) >"$log_dir/stdout.log" 2>"$log_dir/stderr.log"
  fi
  exit_code=$?

  echo "[$name] exit=$exit_code"
  if [[ -f "$out" ]]; then
    echo "  output: ${out#$ROOT_DIR/} ($(wc -c < "$out") bytes)"
  elif [[ -d "$out" ]]; then
    local java_files
    java_files="$(find "$out" -type f -name '*.java' -print | sed "s|$ROOT_DIR/||")"
    if [[ -n "$java_files" ]]; then
      echo "  Java outputs:"
      printf '    %s\n' "$java_files"
    else
      echo "  Java outputs: none"
    fi
  else
    echo "  output: absent"
  fi
  echo "  logs: ${log_dir#$ROOT_DIR/}/stdout.log and stderr.log"
}

run_case 01_file_non_overlapping file
run_case 02_file_conflict file
run_case 03_directory_same_paths directory
run_case 04_directory_renamed_file directory

echo
echo "Finished. Results are in ${RESULTS_DIR#$ROOT_DIR/}."
