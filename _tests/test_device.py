"""Public protocol tests with a synthetic USB peer; no hardware or private source."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('hn_device',Path(__file__).resolve().parents[1]/'_tools/device.py')
device=importlib.util.module_from_spec(spec);spec.loader.exec_module(device)

class Peer:
    def __init__(self):
        self.lines=[];self.calls=[];self.payload=bytearray();self.expected='';self.fail=None
    def write(self, data):
        request=json.loads(data[len(device.PREFIX):]);self.calls.append(request)
        result={'id':request['id'],'ok':True}
        if request['op']=='hello':
            result.update(protocol=1,coreApi=1,development=True)
        elif request['op']=='pair':
            result['token']='a'*64
        elif request.get('token')!='a'*64:
            result.update(ok=False,error='pairing required')
        elif request['op']=='begin':
            self.payload.clear();self.expected=request['sha256'];self.size=request['size']
        elif request['op']=='chunk':
            if request['offset']!=len(self.payload):
                result.update(ok=False,error='offset')
            else:
                self.payload.extend(base64.b64decode(request['data'],validate=True));result['received']=len(self.payload)
        elif request['op']=='commit':
            result.update(active=True,plugin='housenimble.counter')
            result['ok']=len(self.payload)==self.size and hashlib.sha256(self.payload).hexdigest()==self.expected
        if self.fail:
            result.update(self.fail)
        self.lines.extend([b'unrelated core log\n',b'@HN1 {not json}\n',device.PREFIX+json.dumps(result).encode()+b'\n'])
        return len(data)
    def read_until(self,*args):
        return self.lines.pop(0) if self.lines else b''

class DeviceTests(unittest.TestCase):
    def test_chunk_upload_hash_and_no_other_plugins(self):
        peer=Peer();d=device.Device(peer);d.hello();paired=d.pair('123456');self.assertNotIn('token',paired)
        payload=bytes(range(256))*13
        self.assertTrue(d.upload(payload)['active']);self.assertEqual(bytes(peer.payload),payload)
        self.assertTrue(next(x for x in peer.calls if x['op']=='begin')['isolated'])
        self.assertLessEqual(max(len(x.get('data','')) for x in peer.calls),1024)
        d.stop();self.assertEqual(peer.calls[-1]['op'],'stop')
    def test_configuration_is_only_sent_in_begin_not_package_bytes(self):
        peer=Peer();d=device.Device(peer);d.pair('123456');payload=b'x'*30
        config={'latitude':55.6761,'radius_km':30}
        d.upload(payload,config=config)
        self.assertEqual(next(x for x in peer.calls if x['op']=='begin')['config'],config)
        self.assertEqual(bytes(peer.payload),payload)
    def test_unpaired_upload_never_sends(self):
        peer=Peer();d=device.Device(peer)
        with self.assertRaises(device.DeviceError):d.upload(b'x'*30)
        self.assertEqual(peer.calls,[])
    def test_bad_pin_never_sends(self):
        for pin in ['123','1234567','abcdef','１２３４５６']:
            peer=Peer();d=device.Device(peer)
            with self.assertRaises(device.DeviceError):d.pair(pin)
            self.assertEqual(peer.calls,[])
    def test_timeout_is_bounded(self):
        class Silent(Peer):
            def write(self,data):return len(data)
        with self.assertRaisesRegex(device.DeviceError,'timeout'):
            device.Device(Silent(),timeout=0.001).hello(ready_timeout=0.001)
    def test_rejection_explains_without_echoing_token(self):
        peer=Peer();d=device.Device(peer);d.pair('123456');peer.fail={'ok':False,'error':'invalid chunk: '+d.token}
        with self.assertRaises(device.DeviceError) as caught:d.status()
        self.assertNotIn('a'*64,str(caught.exception))
    def test_wrong_ack_aborts_without_commit(self):
        peer=Peer();d=device.Device(peer);d.pair('123456');peer.fail={'received':999}
        with self.assertRaises(device.DeviceError):d.upload(b'x'*30)
        self.assertNotIn('commit',[x['op'] for x in peer.calls])
    def test_hello_retries_a_boot_time_lost_request(self):
        class Booting(Peer):
            dropped=False
            def write(self,payload):
                if not self.dropped:
                    self.dropped=True
                    return len(payload)
                return super().write(payload)
        peer=Booting();d=device.Device(peer,timeout=0.001)
        self.assertTrue(d.hello(ready_timeout=0.02)['development'])
        self.assertEqual(d.sequence,2)

    def test_unsupported_device_rejected(self):
        peer=Peer();peer.fail={'development':False}
        with self.assertRaises(device.DeviceError):device.Device(peer).hello()

if __name__=='__main__':unittest.main()
