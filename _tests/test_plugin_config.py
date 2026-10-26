from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'_tools'))
from plugin_config import configure,ConfigurationError
class SettingsTests(unittest.TestCase):
    def schema(self):return {'type':'object','additionalProperties':False,'properties':{'country':{'type':'string','default':'GLOBAL'},'count':{'type':'integer','minimum':1,'maximum':10,'default':2},'on':{'type':'boolean','default':False},'name':{'type':'string','maxLength':20,'default':'Køkken'}}}
    def test_defaults_and_overrides(self):
        self.assertEqual(configure(self.schema(),{'count':5,'on':True})['count'],5)
        self.assertEqual(configure(self.schema())['name'],'Køkken')
    def test_unknown_null_types_ranges_and_nested_values(self):
        for value in [{'token':'private'},{'count':None},{'count':True},{'count':1.2},{'count':11},{'on':1},{'name':{}},{'name':'a'*129},{'name':'a\0b'}]:
            with self.subTest(value=value),self.assertRaises(ConfigurationError):configure(self.schema(),value)
    def test_unsupported_schema_never_silently_skips_validation(self):
        for extra in [{'pattern':'.*'},{'$ref':'https://example.invalid/schema'},{'type':'object'}]:
            schema=self.schema();schema['properties']['name'].update(extra)
            with self.assertRaises(ConfigurationError):configure(schema)
