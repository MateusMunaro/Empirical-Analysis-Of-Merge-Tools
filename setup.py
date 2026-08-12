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
import hashlib
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
INTELLIMERGE_SHA256 = "a1bc929f8c5cb2f293b4d7fdd9a9bdf67460cad79c58b5ca052ada44e4df5f0e"

FEATUREHOUSE_REPO = "https://github.com/joliebig/featurehouse.git"
FEATUREHOUSE_COMMIT = "81724157bc638524e72af5bb689cf939e6df8599"
FEATUREHOUSE_SRC_JAR = "fstcomp/lib/FeatureHouse.jar"
FSTMERGE_JAR = REPO_ROOT / "merge_tools" / "FSTMerge" / "featurehouse-8172415.jar"
FSTMERGE_SHA256 = "b70425b557ab3ac20d223febc9b6247cddbd12befa5165067972e95173aed10f"

# Adoptium Temurin JDK 8u392-b08 (Linux x64). Used by JDime at runtime.
JDK8_URL = (
    "https://github.com/adoptium/temurin8-binaries/releases/download/"
    "jdk8u392-b08/OpenJDK8U-jdk_x64_linux_hotspot_8u392b08.tar.gz"
)
JDK8_DIR = REPO_ROOT / "java_dependencies" / "java-versions" / "jdk8u392-b08"
JDK8_SHA256 = "15d091e22aa0cad12a241acff8c1634e7228b9740f8d19634250aa6fe0c19a33"

# Adoptium Temurin JDK 21 (Linux x64). Used to run the Gradle wrapper while
# building JDime. JDime's own toolchain (JDK 8) is still resolved via Foojay.
JDK21_URL = (
    "https://github.com/adoptium/temurin21-binaries/releases/download/"
    "jdk-21.0.11%2B10/OpenJDK21U-jdk_x64_linux_hotspot_21.0.11_10.tar.gz"
)
JDK21_DIR = REPO_ROOT / "java_dependencies" / "java-versions" / "jdk-21.0.11+10"
JDK21_SHA256 = "4b2220e232a97997b436ca6ab15cbf70171ecff52958a46159dfa5a8c44ca4de"

JDIME_REPO = "https://github.com/se-sic/jdime.git"
JDIME_COMMIT = "dc3d2eeacf0bb0980994b980bcb11c630300c4f3"
JDIME_SRC_DIR = REPO_ROOT / "merge_tools" / "JDime" / "jdime"
JDIME_INSTALL_DIR = JDIME_SRC_DIR / "build" / "install" / "JDime"
JDIME_LAUNCHER = JDIME_INSTALL_DIR / "bin" / "JDime"
JDIME_BUILD_JAR = JDIME_INSTALL_DIR / "lib" / "JDime.jar"
JDIME_BUILD_SHA256 = "9ad4ebfbbe43a1e3d85b2ec77cd217f87451f0e56e73f09b886a5d708ff5e248"

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_sha256(path: Path, expected: str) -> None:
    observed = sha256_file(path)
    if observed != expected:
        raise SetupError(
            f"checksum mismatch for {path}: expected {expected}, observed {observed}"
        )


def download(url: str, destination: Path, expected_sha256: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    info(f"downloading {url}")
    info(f"        -> {destination}")
    tmp = destination.with_suffix(destination.suffix + ".part")
    with urllib.request.urlopen(url) as response, open(tmp, "wb") as out:
        shutil.copyfileobj(response, out)
    require_sha256(tmp, expected_sha256)
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
        require_sha256(INTELLIMERGE_JAR, INTELLIMERGE_SHA256)
        info(f"already present: {INTELLIMERGE_JAR.relative_to(REPO_ROOT)} (skipping)")
        return
    download(INTELLIMERGE_URL, INTELLIMERGE_JAR, INTELLIMERGE_SHA256)
    info("IntelliMerge jar installed.")


def step_fstmerge(force: bool) -> None:
    info("== FSTMerge / FeatureHouse ==")
    if FSTMERGE_JAR.exists() and not force:
        require_sha256(FSTMERGE_JAR, FSTMERGE_SHA256)
        info(f"already present: {FSTMERGE_JAR.relative_to(REPO_ROOT)} (skipping)")
        return

    import tempfile
    with tempfile.TemporaryDirectory(prefix="featurehouse_") as tmpdir:
        clone_dir = Path(tmpdir) / "featurehouse"
        run(["git", "clone", FEATUREHOUSE_REPO, str(clone_dir)])
        run(["git", "checkout", "--detach", FEATUREHOUSE_COMMIT], cwd=clone_dir)
        src_jar = clone_dir / FEATUREHOUSE_SRC_JAR
        if not src_jar.exists():
            raise SetupError(
                f"Could not find {FEATUREHOUSE_SRC_JAR} inside the featurehouse "
                "clone. The upstream layout may have changed."
            )
        FSTMERGE_JAR.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_jar, FSTMERGE_JAR)
        require_sha256(FSTMERGE_JAR, FSTMERGE_SHA256)
    info("FeatureHouse jar installed.")


def _install_jdk(
    label: str, url: str, expected_sha256: str, target_dir: Path,
    archive_name: str, force: bool,
) -> None:
    info(f"== Adoptium Temurin {label} ==")
    marker = target_dir / "bin" / "java"
    if marker.exists() and not force:
        info(f"already present: {target_dir.relative_to(REPO_ROOT)} (skipping)")
        return
    if force and target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    archive = target_dir.parent / archive_name
    download(url, archive, expected_sha256)

    info(f"extracting {archive.name}")
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        if not members:
            raise SetupError("JDK archive is empty")
        top = members[0].name.split("/", 1)[0]
        tf.extractall(target_dir.parent)
    archive.unlink()

    extracted = target_dir.parent / top
    if extracted != target_dir:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        extracted.rename(target_dir)

    if not marker.exists():
        raise SetupError(f"JDK extraction did not produce {marker}")
    info(f"{label} installed.")


def step_jdk8(force: bool) -> None:
    _install_jdk("JDK 8", JDK8_URL, JDK8_SHA256, JDK8_DIR, "jdk8.tar.gz", force)


def step_jdk21(force: bool) -> None:
    _install_jdk("JDK 21", JDK21_URL, JDK21_SHA256, JDK21_DIR, "jdk21.tar.gz", force)


def step_jdime(force: bool) -> None:
    info("== JDime (built from source) ==")
    if JDIME_LAUNCHER.exists() and not force:
        if not JDIME_BUILD_JAR.exists():
            raise SetupError(f"JDime build jar missing: {JDIME_BUILD_JAR}")
        require_sha256(JDIME_BUILD_JAR, JDIME_BUILD_SHA256)
        info(f"already built: {JDIME_LAUNCHER.relative_to(REPO_ROOT)} (skipping)")
        return

    if not JDIME_SRC_DIR.exists():
        JDIME_SRC_DIR.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", JDIME_REPO, str(JDIME_SRC_DIR)])
    else:
        info(f"reusing existing clone at {JDIME_SRC_DIR.relative_to(REPO_ROOT)}")
    run(["git", "checkout", "--detach", JDIME_COMMIT], cwd=JDIME_SRC_DIR)
    observed_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=JDIME_SRC_DIR,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if observed_commit != JDIME_COMMIT:
        raise SetupError(
            f"JDime commit mismatch: expected {JDIME_COMMIT}, observed {observed_commit}"
        )

    gradlew = JDIME_SRC_DIR / "gradlew"
    if not gradlew.exists():
        raise SetupError(f"gradlew not found at {gradlew}")
    gradlew.chmod(0o755)

    # Gradle 9.x requires JVM 17+ to run, so point JAVA_HOME at our local
    # JDK 21. JDime's own build still targets JDK 8, which Foojay provisions
    # via the toolchain mechanism.
    jdk21_java = JDK21_DIR / "bin" / "java"
    if not jdk21_java.exists():
        raise SetupError(
            f"JDK 21 not found at {JDK21_DIR}. Run setup.py without "
            "--skip jdk21 to install it before building JDime."
        )
    env = os.environ.copy()
    env["JAVA_HOME"] = str(JDK21_DIR)
    env["PATH"] = f"{JDK21_DIR / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    run([str(gradlew), "installDist", "--no-daemon"], cwd=JDIME_SRC_DIR, env=env)

    if not JDIME_LAUNCHER.exists():
        raise SetupError(f"build finished but launcher missing: {JDIME_LAUNCHER}")
    if not JDIME_BUILD_JAR.exists():
        raise SetupError(f"build finished but jar missing: {JDIME_BUILD_JAR}")
    require_sha256(JDIME_BUILD_JAR, JDIME_BUILD_SHA256)
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
        ("JDK 21 (java binary)", JDK21_DIR / "bin" / "java"),
        ("JDime launcher", JDIME_LAUNCHER),
        ("JDime build jar", JDIME_BUILD_JAR),
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
                        choices=["venv", "intellimerge", "fstmerge", "jdk8", "jdk21", "jdime"],
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
            ("jdk21", step_jdk21),
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
