"""Execute the actual plugin in Lua 5.4 with an offline proposed HTTP host.

No Spotify account, Sonos device, source project or private core is accessed.
"""
from pathlib import Path
import unittest
from lupa.lua54 import LuaRuntime

ROOT=Path(__file__).resolve().parents[1]


def room(id='room-a',name='Kitchen',**extra):
    return dict(id=id,name=name,is_restricted=False,supports_volume=True,**extra)


def playback(id='room-a',volume=40,**extra):
    return dict(device=dict(id=id,is_restricted=False,volume_percent=volume),
                is_playing=True,shuffle_state=False,repeat_state='off',
                item=dict(name='Test song',artists=[dict(name='Test artist')]),**extra)


class Host:
    def __init__(self, config=None, network=True):
        self.lua=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
        self.widgets={}; self.requests=[]; self.cancelled=[]
        g=self.lua.globals()
        g._ui=lambda kind,spec:self.widgets.update({spec['id']:spec['text']})
        g._text=lambda id,text:self.widgets.update({id:text})
        g._request=self.request
        g._cancel=lambda id:self.cancelled.append(id)
        self.ctx=self.lua.execute("""return {
            ui={page=function(spec) end,
                label=function(spec) _ui('label',spec) end,
                button=function(spec) _ui('button',spec) end,
                set_text=function(id,text) _text(id,text) end},
            http={request=function(spec) return _request(spec) end,
                  cancel=function(id) _cancel(id) end}}
        """)
        if not network:self.ctx.http=None
        self.ctx.config=self.to_lua(config or {'language':'en'})
        for key in ('io','os','package','require','debug','load','loadfile','dofile','python'):
            g[key]=None
        self.plugin=self.lua.execute((ROOT/'main.lua').read_text())
        self.plugin.create(self.ctx)
        self.plugin.show(self.ctx)

    def to_lua(self,value):
        if isinstance(value,dict):return self.lua.table_from({k:self.to_lua(v) for k,v in value.items()})
        if isinstance(value,list):return self.lua.table_from([self.to_lua(v) for v in value])
        return value

    def request(self,spec):
        id=len(self.requests)+1
        self.requests.append(dict(id=id,tag=spec['tag'],url=spec['url'],method=spec['method'],json=spec['json'],credential=spec['credential']))
        return id

    def event(self,name,**values):
        self.plugin.event(self.ctx,self.to_lua(dict(name=name,**values)))

    def answer(self,status=200,json=None,**extra):
        request=self.requests[-1]
        self.event('http',id=request['id'],tag=request['tag'],status=status,json=json,**extra)

    def ready(self,volume=40):
        self.answer(json={'devices':[room()]})
        self.answer(json=playback(volume=volume))

    def writes(self):return [r for r in self.requests if r['method']!='GET']


class SpotifyPluginTests(unittest.TestCase):
    def host(self,**kwargs):
        return Host(config={'language':'en','device_id':'room-a'},**kwargs)

    def test_missing_host_reports_requirement_without_fake_connection(self):
        host=Host(network=False)
        self.assertEqual(len(host.widgets),12)
        self.assertIn('Waiting for core',host.widgets['status'])
        for name in ('play','next','devices','library'):
            host.event(name)
        self.assertEqual(host.requests,[])
        self.assertIn('Not connected',host.widgets['status'])

    def test_startup_reads_only_and_does_not_choose_implicit_active_device(self):
        host=Host()
        host.answer(json={'devices':[room(),room('room-b','Living room')]})
        self.assertEqual(len(host.requests),1)
        self.assertIn('Choose a speaker',host.widgets['detail'])
        self.assertEqual(host.writes(),[])

    def test_selected_room_status_and_explicit_verified_transport(self):
        host=self.host();host.ready()
        self.assertEqual(host.widgets['title'],'Test song')
        self.assertIn('Kitchen',host.widgets['detail'])
        host.event('next')
        self.assertTrue(host.requests[-1]['url'].endswith('/me/player/devices'))
        self.assertEqual(host.writes(),[])
        host.answer(json={'devices':[room()]})
        self.assertTrue(host.requests[-1]['url'].endswith('/next?device_id=room-a'))
        self.assertEqual(host.requests[-1]['credential'],'spotify')
        host.answer(status=204)
        self.assertTrue(host.requests[-1]['url'].endswith('/me/player'))
        self.assertEqual(len(host.writes()),1)

    def test_rapid_next_is_not_coalesced_and_status_runs_after_queue_drains(self):
        host=self.host();host.ready()
        host.event('next');host.event('previous');host.event('next')
        for _ in range(3):
            host.answer(json={'devices':[room()]})
            host.answer(status=204)
        self.assertEqual([r['url'].split('/me/player/')[1].split('?')[0] for r in host.writes()],['next','previous','next'])
        self.assertTrue(host.requests[-1]['url'].endswith('/me/player'))

    def test_missing_restricted_or_duplicate_room_never_sends_control(self):
        for devices in ([],[dict(room(),is_restricted=True)],[room(),room()]):
            host=self.host();host.ready();host.event('next')
            host.answer(json={'devices':devices})
            self.assertEqual(host.writes(),[])

    def test_control_timeout_drops_queue_and_is_never_replayed(self):
        host=self.host();host.ready();host.event('next');host.event('next')
        host.answer(json={'devices':[room()]})
        host.answer(status=0,error='timeout')
        host.event('tick',now_ms=100)
        self.assertEqual(len(host.writes()),1)
        self.assertIn('No automatic retry',host.widgets['status'])

    def test_retry_after_is_not_shortened_or_extended_by_blocked_buttons(self):
        host=self.host();host.ready();host.event('next')
        host.answer(status=429,retry_after_ms=600000,now_ms=1000)
        count=len(host.requests)
        host.event('next',now_ms=200000)
        host.event('tick',now_ms=600999)
        self.assertEqual(len(host.requests),count)
        host.event('tick',now_ms=601000)
        self.assertGreater(len(host.requests),count)
        self.assertEqual(host.writes(),[])

    def test_other_active_device_clears_track_instead_of_mislabeling_it(self):
        host=self.host();host.ready()
        host.event('tick',now_ms=15000)
        host.answer(json=playback(id='room-b'))
        self.assertNotEqual(host.widgets['title'],'Test song')
        self.assertIn('Another speaker',host.widgets['status'])

    def test_null_volume_does_not_become_zero_and_two_steps_accumulate(self):
        host=self.host();host.ready(volume=None)
        host.event('louder');self.assertEqual(host.writes(),[])
        self.assertIn('unavailable',host.widgets['status'])
        host=self.host();host.ready(volume=94)
        host.event('louder');host.event('louder')
        host.answer(json={'devices':[room()]});host.answer(status=204)
        host.answer(json={'devices':[room()]})
        self.assertIn('volume_percent=99',host.writes()[0]['url'])
        self.assertIn('volume_percent=100',host.writes()[1]['url'])

    def test_shuffle_and_repeat_use_confirmed_state(self):
        host=self.host();host.ready();host.event('shuffle')
        host.answer(json={'devices':[room()]})
        self.assertIn('/shuffle?state=true&device_id=room-a',host.writes()[-1]['url'])
        host.answer(status=204);host.answer(json=playback())
        host.event('repeat');host.answer(json={'devices':[room()]})
        self.assertIn('/repeat?state=context&device_id=room-a',host.writes()[-1]['url'])

    def test_cancelled_response_cannot_repopulate_new_page_or_write(self):
        host=self.host();host.ready()
        host.event('library');old=host.requests[-1]
        host.event('devices')
        host.event('http',id=old['id'],tag=old['tag'],status=200,json={'items':[dict(name='Old',uri='spotify:track:abc')]})
        self.assertNotEqual(host.widgets['title'],'Old')
        self.assertIn(old['id'],host.cancelled)
        self.assertEqual(host.writes(),[])

    def test_hide_and_destroy_cancel_and_ignore_late_responses(self):
        host=self.host();request=host.requests[-1]
        host.plugin.hide(host.ctx)
        before=dict(host.widgets)
        host.answer(json={'devices':[room()]})
        self.assertEqual(host.widgets,before)
        self.assertIn(request['id'],host.cancelled)
        host.plugin.destroy(host.ctx)
        host.event('next');self.assertEqual(host.writes(),[])

    def test_library_plays_only_validated_uri_on_explicit_target(self):
        host=self.host();host.ready();host.event('library')
        host.answer(json={'items':[dict(name='Playlist',uri='spotify:playlist:ABC123')]})
        host.event('play');host.answer(json={'devices':[room()]})
        self.assertEqual(host.writes()[-1]['json']['context_uri'],'spotify:playlist:ABC123')
        self.assertTrue(host.writes()[-1]['url'].endswith('device_id=room-a'))

    def test_untrusted_library_and_search_links_are_never_followed(self):
        host=self.host();host.ready();host.event('library')
        host.answer(json={'items':[dict(name='Bad',uri='https://evil.test/private')]})
        host.event('play')
        self.assertEqual(host.writes(),[])
        self.assertTrue(all(r['url'].startswith('https://api.spotify.com/v1/') for r in host.requests))

    def test_bad_metadata_and_no_content_do_not_crash_or_invent_playback(self):
        for body in (None,{}, {'device':None}, {'device':{'id':'room-a'},'is_playing':'yes'}):
            host=self.host();host.answer(json={'devices':[room()]});host.answer(json=body)
            self.assertIn('Invalid',host.widgets['status'])
            self.assertNotEqual(host.widgets['title'],'Test song')
        host=self.host();host.answer(json={'devices':[room()]});host.answer(status=204)
        self.assertIn('Nothing',host.widgets['status'])

    def test_queue_is_bounded_and_unicode_labels_stay_valid_utf8(self):
        host=self.host();host.ready();host.event('next')
        for _ in range(12):host.event('next')
        self.assertIn('full',host.widgets['status'])
        host=Host(config={'language':'da','device_id':'room-a'})
        host.answer(json={'devices':[room(name='Køkken')]})
        data=playback();data['item']['name']='Ø'*100
        host.answer(json=data)
        self.assertTrue(host.widgets['title'].startswith('Ø'))
        self.assertLessEqual(len(host.widgets['title'].encode()),120)


if __name__=='__main__':unittest.main()
