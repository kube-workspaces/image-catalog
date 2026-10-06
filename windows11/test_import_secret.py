"""Check CDI's credential key contract and credential-helper failure handling."""
import base64
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("import_secret", Path(__file__).with_name("render-import-secret.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImportSecretTests(unittest.TestCase):
    def test_pod_import_uses_cdi_keys_and_preserves_colons_in_token(self):
        auth = base64.b64encode(b"operator:token:with:colons").decode()
        secret = module.import_secret({"auths": {"registry.example.com:5000": {"auth": auth}}},
                                      "registry.example.com:5000", "proof", "registry-import")
        self.assertEqual(secret["type"], "Opaque")
        self.assertEqual(secret["stringData"], {"accessKeyId": "operator", "secretKey": "token:with:colons"})
        self.assertEqual(secret["metadata"]["namespace"], "proof")

    def test_helper_only_config_and_invalid_auth_are_rejected(self):
        for config in ({"credsStore": "desktop", "auths": {"registry.example.com": {}}},
                       {"auths": {"registry.example.com": {"auth": "not-base64"}}}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                module.import_secret(config, "registry.example.com", "proof", "registry-import")


if __name__ == "__main__":
    unittest.main()
