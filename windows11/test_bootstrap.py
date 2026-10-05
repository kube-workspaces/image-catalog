import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("bootstrap", Path(__file__).with_name("render-bootstrap.py"))
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)
NS = {"u": bootstrap.NS}


class BootstrapTests(unittest.TestCase):
    def test_private_outputs_are_exclusive_and_owner_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credentials.json"
            bootstrap.write_private(path, "private")
            if os.name == "posix":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                bootstrap.write_private(path, "replacement")
            self.assertEqual(path.read_text(), "private")

    def test_clone_does_not_repartition_or_install_media(self):
        xml = bootstrap.answer_file("clone", "KW-CLONE-A", "workspace", 'p&<>"')
        root = ET.fromstring(xml)
        self.assertIsNone(root.find(".//u:DiskConfiguration", NS))
        self.assertIsNone(root.find(".//u:ImageInstall", NS))
        self.assertIsNone(root.find(".//u:AutoLogon", NS))
        self.assertIsNone(root.find(".//u:RunSynchronous", NS))
        self.assertEqual(root.find(".//u:LocalAccount/u:Password/u:Value", NS).text, 'p&<>"')

    def test_install_pins_edition_and_blank_disk_target(self):
        root = ET.fromstring(bootstrap.answer_file("install", "KW-BUILD", "workspace", "test"))
        self.assertEqual(root.find(".//u:Disk/u:DiskID", NS).text, "0")
        self.assertEqual(root.find(".//u:Disk/u:WillWipeDisk", NS).text, "true")
        self.assertEqual(root.find(".//u:MetaData/u:Value", NS).text, "Windows 11 Pro")
        self.assertEqual(root.find(".//u:InstallTo/u:PartitionID", NS).text, "3")
        paths = root.findall("u:settings[@pass='offlineServicing']/u:component/u:DriverPaths/u:PathAndCredentials/u:Path", NS)
        self.assertIn(r"V:\viostor\w11\amd64", [p.text for p in paths])
        self.assertIn("subst V:", root.find(".//u:RunSynchronousCommand/u:Path", NS).text)
        deployment = root.find("u:settings[@pass='specialize']/u:component[@name='Microsoft-Windows-Deployment']", NS)
        command = deployment.find(".//u:Path", NS).text
        self.assertLessEqual(len(command), 259)
        self.assertIn("configure.ps1", command)
        self.assertIn("exit /b !errorlevel!", command)
        self.assertTrue(command.endswith('exit /b 1"'))
        self.assertNotIn("LabConfig", ET.tostring(root, encoding="unicode"))

    def test_invalid_identity_rejected(self):
        for hostname, username in (("TOO-LONG-HOSTNAME", "workspace"), ("1234", "workspace"),
                                   ("KW-A", "Administrator"), ("KW-A", "user/name")):
            with self.subTest(hostname=hostname, username=username), self.assertRaises(ValueError):
                bootstrap.answer_file("clone", hostname, username, "test")


if __name__ == "__main__":
    unittest.main()
