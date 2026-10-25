#!/usr/bin/env python3
"""Package integrity regressions; no Lua execution or device access."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]/'counter'
spec = importlib.util.spec_from_file_location('validator', ROOT.parent/'_tools/validate_plugin.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'plugin'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__'))

    def change_manifest(self, change):
        path = self.root/'plugin.json'
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def test_deterministic_package_excludes_docs_tests_and_secrets(self):
        (self.root/'private-token.txt').write_text('synthetic-secret')
        first,second = Path(self.tmp.name)/'a.hnplugin',Path(self.tmp.name)/'b.hnplugin'
        self.assertEqual(validator.package(self.root,first),validator.package(self.root,second))
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(archive.namelist(),['LICENSE','config.schema.json','main.lua','plugin.json'])
            self.assertNotIn(b'synthetic-secret',first.read_bytes())

    def test_entry_path_cannot_escape_package(self):
        self.change_manifest(lambda m:m.update(entry='../core.lua'))
        with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)

    def test_origins_cannot_carry_credentials_or_wildcards(self):
        for origin in ['https://*.example.org','https://user:password@example.org','https://example.org/path']:
            self.change_manifest(lambda m:m['permissions'].update(network=[origin]))
            with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)

    def test_quota_is_not_an_unbounded_or_boolean_request(self):
        for quota in [True,0,99999999]:
            self.change_manifest(lambda m:m['limits'].update(memoryBytes=quota))
            with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)

    def test_asset_symlink_cannot_include_a_core_file(self):
        assets=self.root/'assets';assets.mkdir();(assets/'core.png').symlink_to(self.root/'main.lua')
        with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)

    def test_binary_lua_is_rejected(self):
        (self.root/'main.lua').write_bytes(b'\x1bLua\x00')
        with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)

    def test_missing_license_and_unknown_api_are_rejected(self):
        (self.root/'LICENSE').unlink()
        with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)
        self.change_manifest(lambda m:m.update(apiVersion=999))
        with self.assertRaises(validator.InvalidPlugin): validator.validate(self.root)

    def test_output_cannot_overwrite_source(self):
        original=(self.root/'main.lua').read_bytes()
        with self.assertRaises(validator.InvalidPlugin): validator.package(self.root,self.root/'main.lua')
        self.assertEqual((self.root/'main.lua').read_bytes(),original)


if __name__ == '__main__':
    unittest.main()
