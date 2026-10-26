"""Keep the public catalog's display categories complete and unambiguous."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class CategoryConfiguration(unittest.TestCase):
    def test_every_plugin_folder_belongs_to_one_category(self):
        catalog=json.loads((ROOT/'catalog.json').read_text())
        groups=catalog['categories']
        names=[g['name'] for g in groups]
        self.assertEqual(names,['Dit hjem','Energi','Hverdag','Hobby','På farten','Eksempler'])
        self.assertEqual(len(names),len(set(names)))
        members=[p for g in groups for p in g['plugins']]
        self.assertEqual(len(members),len(set(members)))
        folders={p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(('_','.'))
                 and (p/'README.md').is_file() and (p/'config.schema.json').is_file()}
        self.assertEqual(set(members),folders)
        self.assertIn('counter',groups[-1]['plugins'])
        self.assertEqual(catalog['installable'],[])


if __name__=='__main__':
    unittest.main()
