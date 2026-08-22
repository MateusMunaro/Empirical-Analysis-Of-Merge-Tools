"""Stable hashes for downloaded files and locally built ZIP/JAR artifacts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def sha256_file(path: Path) -> str:
    """Hash the exact bytes of a file."""

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_zip_content(path: Path) -> str:
    """Hash ZIP/JAR entry names and payloads, ignoring container metadata.

    JAR byte hashes can differ across equivalent Gradle builds because ZIP
    timestamps, attributes, entry order, and compression details are not part
    of the executable payload. This digest is stable only when every named,
    uncompressed entry payload is the same. Duplicate names remain distinct.
    """

    digest = hashlib.sha256()
    with ZipFile(path) as archive:
        entries = sorted(
            (entry for entry in archive.infolist() if not entry.is_dir()),
            key=lambda entry: (entry.filename, entry.header_offset),
        )
        for entry in entries:
            name = entry.filename.encode("utf-8")
            content = archive.read(entry)
            digest.update(len(name).to_bytes(8, "big"))
            digest.update(name)
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    try:
        print(f"raw_sha256={sha256_file(args.artifact)}")
        print(f"canonical_zip_content_sha256={sha256_zip_content(args.artifact)}")
    except (OSError, BadZipFile) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
