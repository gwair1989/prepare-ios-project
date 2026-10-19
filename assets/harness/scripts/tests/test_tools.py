import hashlib
import importlib.util
import io
from pathlib import Path
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("installer", Path(__file__).parents[1] / "install_tools.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ToolDownloadTests(unittest.TestCase):
    def test_only_selected_binary_is_returned_without_extracting_paths(self):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            archive.writestr("../../outside", b"unrelated")
            archive.writestr("bin/checker", b"expected executable")
        payload = output.getvalue()
        self.assertEqual(installer.verified_binary(payload, hashlib.sha256(payload).hexdigest(), "checker"),
                         b"expected executable")

    def test_corrupt_download_is_rejected_before_use(self):
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            installer.verified_binary(b"corrupt", "0" * 64, "checker")


if __name__ == "__main__":
    unittest.main()
