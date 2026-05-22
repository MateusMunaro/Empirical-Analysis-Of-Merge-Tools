#!/usr/bin/env python3
"""
Empirical Analysis of Merge Tools - Automated Environment Setup (Linux)
=======================================================================

This script provisions every external dependency required to reproduce the
study end-to-end on a fresh Linux machine:

  * Python virtual environment (.venv) with the evaluation packages
  * IntelliMerge fat-jar (downloaded from GitHub Releases)
  * FeatureHouse jar used by FSTMerge (extracted from joliebig/featurehouse)
  * Adoptium Temurin JDK 8 (used by JDime)
  * JDime built from source via its Gradle wrapper

The script is idempotent: each step checks whether its artefact already
exists and is skipped if so. Re-running it after a partial failure resumes
where it stopped.

Usage:
    python3 setup.py                # provision everything
    python3 setup.py --check        # verify the environment, install nothing
    python3 setup.py --force        # re-download/rebuild even if present

Tested on Ubuntu 22.04 / Debian 12 / Fedora 39 (x86_64).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# --- External resources ------------------------------------------------------

INTELLIMERGE_URL = (
    "https://github.com/Symbolk/IntelliMerge/releases/download/"
    "1.0.9/IntelliMerge-1.0.9-all.jar"
)
INTELLIMERGE_JAR = REPO_ROOT / "merge_tools" / "IntelliMerge" / "IntelliMerge-1.0.9-all.jar"

FEATUREHOUSE_REPO = "https://github.com/joliebig/featurehouse.git"
FEATUREHOUSE_SRC_JAR = "fstcomp/lib/FeatureHouse.jar"
FSTMERGE_JAR = REPO_ROOT / "merge_tools" / "FSTMerge" / "featurehouse_20220107.jar"

# Adoptium Temurin JDK 8u392-b08 (Linux x64).
JDK8_URL = (
    "https://github.com/adoptium/temurin8-binaries/releases/download/"
    "jdk8u392-b08/OpenJDK8U-jdk_x64_linux_hotspot_8u392b08.tar.gz"
)
JDK8_DIR = REPO_ROOT / "java_dependencies" / "java-versions" / "jdk8u392-b08"

JDIME_REPO = "https://github.com/se-sic/jdime.git"
JDIME_SRC_DIR = REPO_ROOT / "merge_tools" / "JDime" / "jdime"
JDIME_INSTALL_DIR = JDIME_SRC_DIR / "build" / "install" / "JDime"
JDIME_LAUNCHER = JDIME_INSTALL_DIR / "bin" / "JDime"

VENV_DIR = REPO_ROOT / ".venv"
PY_PACKAGES = ["numpy", "pandas", "matplotlib", "scipy", "tabulate"]

# --- Utilities ---------------------------------------------------------------


class SetupError(RuntimeError):
    """Raised when a setup step cannot complete and the user must intervene."""


def info(msg: str) -> None:
    print(f"[setup] {msg}")


def warn(msg: str) -> None:
    print(f"[setup][warn] {msg}", file=sys.stderr)


def fail(msg: str) -> None:
    print(f"[setup][error] {msg}", file=sys.stderr)


def run(cmd, cwd: Path | None = None, env: dict | None = None) -> None:
    """Run a subprocess, streaming output, raising SetupError on failure."""
    pretty = " ".join(str(c) for c in cmd)
    info(f"$ {pretty}" + (f"   (cwd={cwd})" if cwd else ""))
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env)
    if result.returncode != 0:
        raise SetupError(f"command failed ({result.returncode}): {pretty}")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    info(f"downloading {url}")
    info(f"        -> {destination}")
    tmp = destination.with_suffix(destination.suffix + ".part")
    with urllib.request.urlopen(url) as response, open(tmp, "wb") as out:
        shutil.copyfileobj(response, out)
    tmp.replace(destination)


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def require_linux() -> None:
    if platform.system() != "Linux":
        raise SetupError(
            f"This setup script targets Linux. Detected: {platform.system()}. "
            "On Windows please run it from WSL2."
        )


def require_python() -> None:
    if sys.version_info < (3, 8):
        raise SetupError(f"Python 3.8+ required, found {sys.version.split()[0]}")


def require_cli_tools() -> None:
    missing = [t for t in ("git", "java", "tar") if which(t) is None]
    if missing:
        raise SetupError(
            "Missing required system commands: " + ", ".join(missing) +
            ". Install them via your package manager (e.g. "
            "`sudo apt install git default-jre tar`)."
        )


# --- Steps -------------------------------------------------------------------


def step_python_venv(force: bool) -> None:
    info("== Python virtual environment ==")
    if VENV_DIR.exists() and not force:
        info(f"virtualenv already present at {VENV_DIR} (skipping creation)")
    else:
        if force and VENV_DIR.exists():
            info("removing existing virtualenv (--force)")
            shutil.rmtree(VENV_DIR)
        run([sys.executable, "-m", "venv", str(VENV_DIR)])

    pip = VENV_DIR / "bin" / "pip"
    if not pip.exists():
        raise SetupError(f"pip not found inside virtualenv: {pip}")

    run([str(pip), "install", "--upgrade", "pip"])
    run([str(pip), "install", *PY_PACKAGES])
    info("Python dependencies installed.")
    info(f"Activate with: source {VENV_DIR.relative_to(REPO_ROOT)}/bin/activate")


def step_intellimerge(force: bool) -> None:
    info("== IntelliMerge ==")
    if INTELLIMERGE_JAR.exists() and not force:
        info(f"already present: {INTELLIMERGE_JAR.relative_to(REPO_ROOT)} (skipping)")
        return
    download(INTELLIMERGE_URL, INTELLIMERGE_JAR)
    info("IntelliMerge jar installed.")


def step_fstmerge(force: bool) -> None:
    info("== FSTMerge / FeatureHouse ==")
    if FSTMERGE_JAR.exists() and not force:
        info(f"already present: {FSTMERGE_JAR.relative_to(REPO_ROOT)} (skipping)")
        return

    import tempfile
    with tempfile.TemporaryDirectory(prefix="featurehouse_") as tmpdir:
        clone_dir = Path(tmpdir) / "featurehouse"
        run(["git", "clone", "--depth", "1", FEATUREHOUSE_REPO, str(clone_dir)])
        src_jar = clone_dir / FEATUREHOUSE_SRC_JAR
        if not src_jar.exists():
            raise SetupError(
                f"Could not find {FEATUREHOUSE_SRC_JAR} inside the featurehouse "
                "clone. The upstream layout may have changed."
            )
        FSTMERGE_JAR.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_jar, FSTMERGE_JAR)
    info("FeatureHouse jar installed.")


def step_jdk8(force: bool) -> None:
    info("== Adoptium Temurin JDK 8 ==")
    marker = JDK8_DIR / "bin" / "java"
    if marker.exists() and not force:
        info(f"already present: {JDK8_DIR.relative_to(REPO_ROOT)} (skipping)")
        return
    if force and JDK8_DIR.exists():
        shutil.rmtree(JDK8_DIR)

    JDK8_DIR.parent.mkdir(parents=True, exist_ok=True)
    archive = JDK8_DIR.parent / "jdk8.tar.gz"
    download(JDK8_URL, archive)

    info(f"extracting {archive.name}")
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        if not members:
            raise SetupError("JDK archive is empty")
        top = members[0].name.split("/", 1)[0]
        tf.extractall(JDK8_DIR.parent)
    archive.unlink()

    extracted = JDK8_DIR.parent / top
    if extracted != JDK8_DIR:
        if JDK8_DIR.exists():
            shutil.rmtree(JDK8_DIR)
        extracted.rename(JDK8_DIR)

    if not marker.exists():
        raise SetupError(f"JDK extraction did not produce {marker}")
    info("JDK 8 installed.")


def step_jdime(force: bool) -> None:
    info("== JDime (built from source) ==")
    if JDIME_LAUNCHER.exists() and not force:
        info(f"already built: {JDIME_LAUNCHER.relative_to(REPO_ROOT)} (skipping)")
        return

    if not JDIME_SRC_DIR.exists():
        JDIME_SRC_DIR.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", JDIME_REPO, str(JDIME_SRC_DIR)])
    else:
        info(f"reusing existing clone at {JDIME_SRC_DIR.relative_to(REPO_ROOT)}")

    gradlew = JDIME_SRC_DIR / "gradlew"
    if not gradlew.exists():
        raise SetupError(f"gradlew not found at {gradlew}")
    gradlew.chmod(0o755)

    # Build with JDime's Gradle wrapper. The foojay-resolver convention plugin
    # auto-provisions the JDK 8 toolchain required by JDime, so we don't need
    # to point JAVA_HOME at our local copy here.
    env = os.environ.copy()
    run([str(gradlew), "installDist", "--no-daemon"], cwd=JDIME_SRC_DIR, env=env)

    if not JDIME_LAUNCHER.exists():
        raise SetupError(f"build finished but launcher missing: {JDIME_LAUNCHER}")
    JDIME_LAUNCHER.chmod(0o755)
    info("JDime built and installed.")


# --- Verification ------------------------------------------------------------


def verify(strict: bool) -> bool:
    info("== Verification ==")
    checks = [
        ("Python venv", VENV_DIR / "bin" / "python"),
        ("IntelliMerge jar", INTELLIMERGE_JAR),
        ("FeatureHouse jar", FSTMERGE_JAR),
        ("JDK 8 (java binary)", JDK8_DIR / "bin" / "java"),
        ("JDime launcher", JDIME_LAUNCHER),
    ]
    ok = True
    for label, path in checks:
        present = path.exists()
        marker = "OK " if present else "MISS"
        print(f"  [{marker}] {label:<22} {path.relative_to(REPO_ROOT)}")
        ok = ok and present

    if strict and not ok:
        raise SetupError("verification failed - one or more components missing")
    return ok


# --- Entry point -------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="Only verify the environment; do not install anything.")
    parser.add_argument("--force", action="store_true",
                        help="Reinstall components even when they look present.")
    parser.add_argument("--skip", nargs="*", default=[],
                        choices=["venv", "intellimerge", "fstmerge", "jdk8", "jdime"],
                        help="Skip specific steps.")
    args = parser.parse_args()

    try:
        require_linux()
        require_python()

        if args.check:
            ok = verify(strict=False)
            return 0 if ok else 1

        require_cli_tools()

        steps = [
            ("venv", step_python_venv),
            ("intellimerge", step_intellimerge),
            ("fstmerge", step_fstmerge),
            ("jdk8", step_jdk8),
            ("jdime", step_jdime),
        ]
        for name, fn in steps:
            if name in args.skip:
                info(f"-- skipping step '{name}' (per --skip)")
                continue
            fn(args.force)

        verify(strict=True)
        info("All components installed.")
        info("Next step: source .venv/bin/activate && python scripts/executor.py")
        return 0

    except SetupError as e:
        fail(str(e))
        return 2
    except KeyboardInterrupt:
        warn("interrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())
