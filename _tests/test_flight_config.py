import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tools'))
import hn

class FlightConfigurationTests(unittest.TestCase):
    def test_bounded_nonsecret_settings_pass(self):
        value={'latitude':55.6761,'longitude':12.5683,'radius_km':30,'language':'en','show_ground':False}
        self.assertEqual(hn.flight_configuration(value),value)

    def test_credentials_unknown_values_null_and_bad_types_are_rejected(self):
        for value in [[],{'token':'synthetic'},{'latitude':None},{'latitude':True},{'latitude':float('nan')},
                      {'longitude':181},{'refresh_seconds':1},{'max_aircraft':2.5},{'show_ground':1},{'language':'fr'}]:
            with self.subTest(value=value):
                with self.assertRaises(hn.InvalidPlugin):hn.flight_configuration(value)

    def test_only_flight_provider_is_accepted_by_device_subset(self):
        manifest,files=hn.validate(ROOT/'flight');hn.device_subset(manifest,files)
        manifest['permissions']['network']=['https://example.org']
        with self.assertRaises(hn.InvalidPlugin):hn.device_subset(manifest,files)
        manifest,files=hn.validate(ROOT/'spotify')
        with self.assertRaises(hn.InvalidPlugin):hn.device_subset(manifest,files)
