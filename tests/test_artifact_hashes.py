import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZipInfo

from scripts.artifact_hashes import sha256_file, sha256_zip_content


class ArtifactHashTests(unittest.TestCase):
    def test_zip_content_hash_ignores_order_timestamp_and_compression(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / "first.jar"
            second = root / "second.jar"
            with ZipFile(first, "w") as archive:
                old = ZipInfo("a.txt", date_time=(2001, 1, 1, 0, 0, 0))
                archive.writestr(old, b"alpha")
                archive.writestr("b.txt", b"beta")
            with ZipFile(second, "w") as archive:
                archive.writestr("b.txt", b"beta")
                new = ZipInfo("a.txt", date_time=(2026, 8, 12, 12, 0, 0))
                archive.writestr(new, b"alpha")

            self.assertNotEqual(sha256_file(first), sha256_file(second))
            self.assertEqual(
                sha256_zip_content(first), sha256_zip_content(second)
            )

    def test_zip_content_hash_detects_payload_change(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / "first.jar"
            second = root / "second.jar"
            with ZipFile(first, "w") as archive:
                archive.writestr("a.txt", b"alpha")
            with ZipFile(second, "w") as archive:
                archive.writestr("a.txt", b"changed")

            self.assertNotEqual(
                sha256_zip_content(first), sha256_zip_content(second)
            )


if __name__ == "__main__":
    unittest.main()
