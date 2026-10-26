from pathlib import Path
import unittest
from lupa.lua54 import LuaRuntime

ROOT=Path(__file__).resolve().parents[1]

def aircraft(**values):
    row=dict(hex='abc123',flight='TEST123 ',r='TEST-REG',t='A320',lat=55.68,lon=12.57,seen_pos=2,alt_baro=10000,gs=200,track=90)
    row.update(values);return row

class Host:
    def __init__(self,network=True,config=None):
        self.lua=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
        self.labels={};self.requests=[];self.cancelled=[]
        globals=self.lua.globals()
        globals._widget=lambda spec:self.labels.update({spec['id']:spec['text']})
        globals._text=lambda id,text:self.labels.update({id:text})
        globals._request=self.request
        globals._cancel=lambda id:self.cancelled.append(id)
        self.ctx=self.lua.execute("""return {ui={page=function(spec) end,
            label=function(spec) _widget(spec) end,button=function(spec) _widget(spec) end,
            set_text=function(id,text) _text(id,text) end},
            http={request=function(spec) return _request(spec) end,cancel=function(id) _cancel(id) end}}""")
        if not network:self.ctx.http=None
        self.ctx.config=self.convert(config or {'language':'en'})
        self.plugin=self.lua.execute((ROOT/'main.lua').read_text());self.plugin.create(self.ctx);self.plugin.show(self.ctx)

    def convert(self,value):
        if isinstance(value,dict):return self.lua.table_from({k:self.convert(v) for k,v in value.items()})
        if isinstance(value,list):return self.lua.table_from([self.convert(v) for v in value])
        return value
    def request(self,spec):
        id=len(self.requests)+1;self.requests.append(dict(id=id,tag=spec['tag'],url=spec['url'],method=spec['method']));return id
    def event(self,name,**fields):self.plugin.event(self.ctx,self.convert(dict(name=name,**fields)))
    def answer(self,rows=None,status=200,**fields):
        request=self.requests[-1];self.event('http',id=request['id'],tag=request['tag'],status=status,json={'ac':rows if rows is not None else [aircraft()]},**fields)

class FlightPluginTests(unittest.TestCase):
    def test_live_request_is_readonly_fixed_provider_and_km_become_nm(self):
        h=Host();self.assertEqual(h.requests[0]['method'],'GET')
        self.assertEqual(h.requests[0]['url'],'https://opendata.adsb.fi/api/v3/lat/55.67610/lon/12.56830/dist/16.199')
        self.assertLessEqual(len(h.labels),12)
    def test_missing_host_never_claims_live_data(self):
        h=Host(network=False);self.assertEqual(h.requests,[]);self.assertIn('Requires a newer core',h.labels['status'])
    def test_metric_values_and_callsign_are_real_response_values(self):
        h=Host();h.answer();self.assertIn('TEST123',h.labels['row1']);self.assertIn('3048 m',h.labels['row1']);self.assertIn('370 km/t',h.labels['row1'])
        self.assertIn('TEST-REG',h.labels['details'])
    def test_old_missing_nonfinite_and_distant_positions_are_filtered(self):
        for change in ({'seen_pos':61},{'seen_pos':None},{'lat':None},{'lat':float('nan')},{'lon':180},{'hex':'malicious!'}):
            h=Host();h.answer([aircraft(**change)]);self.assertNotIn('TEST123',h.labels['row1'])
    def test_nearest_sort_duplicate_and_upper_bound(self):
        h=Host(config={'language':'en','max_aircraft':1})
        h.answer([aircraft(hex='def456',flight='FAR',lat=55.8),aircraft(),aircraft()])
        self.assertIn('1 aircraft',h.labels['area']);self.assertIn('TEST123',h.labels['row1'])
    def test_ground_and_unknown_values_are_not_reported_as_zero(self):
        h=Host();h.answer([aircraft(alt_baro='ground')]);self.assertNotIn('TEST123',h.labels['row1'])
        h=Host(config={'language':'en','show_ground':True});h.answer([aircraft(alt_baro='ground',gs=None)])
        self.assertIn('0 m',h.labels['row1']);self.assertIn(' · ? · ',h.labels['row1'])
    def test_first_reply_with_long_core_uptime_does_not_trigger_immediate_refetch(self):
        h=Host();h.answer(now_ms=9000000);h.event('tick',now_ms=9000000)
        self.assertEqual(len(h.requests),1);self.assertIn('Live aircraft',h.labels['status'])
    def test_manual_refresh_cannot_overrun_poll_or_duplicate_pending_request(self):
        h=Host();h.event('refresh');self.assertEqual(len(h.requests),1);h.answer()
        h.event('refresh',now_ms=14999);self.assertEqual(len(h.requests),1)
        h.event('tick',now_ms=15000);self.assertEqual(len(h.requests),2)
    def test_failure_keeps_last_data_and_shows_age(self):
        h=Host();h.answer();h.event('tick',now_ms=15000);h.answer(status=500,now_ms=16000)
        self.assertIn('Could not fetch',h.labels['status']);self.assertIn('16s',h.labels['status']);self.assertIn('TEST123',h.labels['row1'])
    def test_rate_limit_honors_full_retry_after_without_extending_for_button(self):
        h=Host();h.answer(status=429,retry_after_ms=600000)
        h.event('refresh',now_ms=100000);h.event('tick',now_ms=599999);self.assertEqual(len(h.requests),1)
        h.event('tick',now_ms=600000);self.assertEqual(len(h.requests),2)
    def test_hide_stop_and_new_instance_ignore_old_response(self):
        h=Host();old=dict(h.requests[-1]);h.plugin.hide(h.ctx);before=dict(h.labels)
        h.answer();self.assertEqual(h.labels,before);self.assertIn(old['id'],h.cancelled)
        h.plugin.destroy(h.ctx);h.plugin.create(h.ctx);h.plugin.show(h.ctx)
        h.event('http',id=old['id'],tag=old['tag'],status=200,json={'ac':[aircraft()]})
        self.assertNotIn('TEST123',h.labels['row1'])
    def test_units_and_selection_do_not_make_network_requests(self):
        h=Host();h.answer();h.event('units');h.event('next');h.event('previous')
        self.assertIn('10000 ft',h.labels['row1']);self.assertEqual(len(h.requests),1)
    def test_malformed_json_and_large_arrays_never_create_fake_positions(self):
        h=Host();h.event('http',id=1,tag=h.requests[-1]['tag'],status=200,json={})
        self.assertIn('Invalid',h.labels['status'])
        h=Host();h.answer([aircraft()]*81);self.assertIn('Invalid',h.labels['status'])

if __name__=='__main__':unittest.main()
