"""Prevent accidental inclusion of native core source/builds/history in this proposal."""
from pathlib import Path
import json
import os
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PublicBoundary(unittest.TestCase):
    def test_no_core_or_private_build_files(self):
        forbidden={'.c','.cc','.cpp','.h','.hpp','.o','.a','.bin','.elf','.map','.pem','.key'}
        for directory, folders, files in os.walk(ROOT, followlinks=False):
            # This checkout owns its root Git database; copied/nested history is forbidden.
            if Path(directory) == ROOT and '.git' in folders:
                folders.remove('.git')
            for name in folders + files:
                p = Path(directory) / name
                with self.subTest(path=str(p.relative_to(ROOT))):
                    self.assertNotIn(p.name,{'.git','.pio','.env','credentials.json'})
                    self.assertFalse(p.is_symlink())
                    self.assertNotIn(p.suffix.lower(),forbidden)

    def test_no_port_is_claimed_to_be_installable(self):
        catalog=json.loads((ROOT/'catalog.json').read_text())
        self.assertEqual(catalog['installable'],[])
        self.assertEqual(catalog['status'],'draft')
        for name in catalog['plannedPlugins']:
            folder=ROOT/name
            self.assertTrue((folder/'README.md').is_file())
            self.assertTrue((folder/'DEVICE-TEST.md').is_file())
            schema=json.loads((folder/'config.schema.json').read_text())
            self.assertIn('country',schema['properties'])
            self.assertFalse((folder/'main.lua').exists())

if __name__=='__main__':unittest.main()
