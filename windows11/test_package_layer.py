"""Exercise the actual QCOW2 and layer permission contract with qemu-img."""
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("package_layer", Path(__file__).with_name("package-layer.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(shutil.which("qemu-img"), "requires qemu-img")
class PackageLayerTests(unittest.TestCase):
    def test_layer_is_standalone_readable_by_launcher_and_contains_only_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            disk, output = root / "root.qcow2", root / "layer.tar.gz"
            subprocess.run(["qemu-img", "create", "-f", "qcow2", str(disk), "64M"], check=True)
            module.package(disk, output)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            with tarfile.open(output) as archive:
                self.assertEqual(archive.getnames(), ["disk", "disk/disk.qcow2"])
                directory_entry, disk_entry = archive.getmembers()
                self.assertEqual((directory_entry.uid, directory_entry.gid, directory_entry.mode),
                                 (107, 107, 0o755))
                self.assertEqual((disk_entry.uid, disk_entry.gid, disk_entry.mode), (107, 107, 0o440))
                extracted = root / "extracted.qcow2"
                with extracted.open("wb") as destination:
                    shutil.copyfileobj(archive.extractfile(disk_entry), destination)
            subprocess.run(["qemu-img", "check", str(extracted)], check=True)
            info = json.loads(subprocess.check_output(
                ["qemu-img", "info", "--output=json", str(extracted)], text=True))
            self.assertEqual(info["virtual-size"], 64 * 1024 * 1024)
            with self.assertRaisesRegex(ValueError, "already exists"):
                module.package(disk, output)

    def test_backing_disk_is_rejected_before_archive_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            disk, overlay, output = root / "base.qcow2", root / "overlay.qcow2", root / "layer.tar.gz"
            subprocess.run(["qemu-img", "create", "-f", "qcow2", str(disk), "64M"], check=True)
            subprocess.run(["qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
                            "-b", str(disk), str(overlay)], check=True)
            with self.assertRaisesRegex(ValueError, "standalone"):
                module.package(overlay, output)
            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(output.name + ".partial").exists())


if __name__ == "__main__":
    unittest.main()
