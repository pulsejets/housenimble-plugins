#!/usr/bin/env python3
"""Validate, package and test one Lua plugin on an owner-provisioned development core."""
import argparse
import getpass
import json
from pathlib import Path
import sys
import tempfile
import time
from validate_plugin import validate, package, InvalidPlugin
from device import Device, DeviceError, open_serial


def device_subset(manifest,payload):
    files=dict(payload)
    if set(files)!={'plugin.json','main.lua','config.schema.json','LICENSE'}:
        raise InvalidPlugin('Development API 1 currently supports Lua/text UI only; image assets are not supported')
    permissions=manifest['permissions']
    if any(permissions[k] for k in ['network','mqttSubscribe','mqttPublish']):
        raise InvalidPlugin('Development API 1 does not grant HTTP/MQTT capabilities yet')
    if permissions['storageBytes']>4096 or not 32768<=manifest['limits']['memoryBytes']<=262144 or manifest['limits']['instructionsPerCallback']<1000:
        raise InvalidPlugin('Development core supports 32–256 KiB Lua RAM, 1000–100000 instructions and up to 4 KiB storage')
    if len(manifest['id'])>96:
        raise InvalidPlugin('Plugin id exceeds development limit')
    schema=json.loads(files['config.schema.json'])
    if set(schema['properties'])!={'country','language'} or schema['properties']['country'].get('default')!='GLOBAL' or schema['properties']['language'].get('default')!='da':
        raise InvalidPlugin('Development API 1 supports GLOBAL/da defaults only; configurable settings come later')


def run_device(args, blob=None, manifest=None):
    stream=open_serial(args.port)
    device=Device(stream)
    paired=False
    try:
        initial=device.hello()
        if args.command=='status':
            safe={key:initial[key] for key in ['protocol','coreApi','development','build','buildId','active','plugin','memoryBytes','widgets','wifiConnected','received'] if key in initial}
            print(json.dumps(safe,ensure_ascii=False,indent=2))
            return 0
        print('Tryk “USB · par enhed” på skærmen. Koden gælder i 60 sekunder.')
        pin=args.pin or getpass.getpass('USB-kode fra skærmen: ')
        device.pair(pin)
        paired=True
        if args.command=='stop':
            device.stop();print('Plugin stoppet. Core og Wi-Fi fortsætter.');return 0
        started=device.upload(blob)
        if started.get('active') is not True or started.get('plugin')!=manifest['id']:
            raise DeviceError('Unexpected active plugin after upload')
        print(f"Aktivt: {manifest['id']} {manifest['version']} · kun dette plugin")
        print('Ctrl+C stopper pluginet. Hold dette program åbent under testen.')
        began=time.monotonic()
        while args.duration is None or time.monotonic()-began<args.duration:
            state=device.status()
            if state.get('active') is not True:
                raise DeviceError('Plugin stopped: '+str(state.get('error','session expired')))
            print(f"RAM {state.get('memoryBytes',0)} bytes · widgets {state.get('widgets',0)} · Wi-Fi {'tilsluttet' if state.get('wifiConnected') else 'afbrudt'}",flush=True)
            time.sleep(min(5,max(0,args.duration-(time.monotonic()-began))) if args.duration is not None else 5)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        if paired and args.command=='test':
            try:
                device.stop()
                print('Test afsluttet; plugin stoppet.')
            except (DeviceError,OSError):
                print('USB-stop kunne ikke bekræftes. Core stopper automatisk pluginet efter højst 30 sekunder uden heartbeat.',file=sys.stderr)
        device.token=None
        stream.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ['check','pack','test','status','stop']:
        child=sub.add_parser(command)
        if command in ['check','pack','test']:
            child.add_argument('plugin',type=Path)
        if command=='pack':
            child.add_argument('--out',type=Path,required=True)
        if command in ['test','status','stop']:
            child.add_argument('--port',required=True,help='USB serial device path, e.g. /dev/cu.usbmodem... or COM5')
            child.add_argument('--usb',action='store_true',help='USB is the only supported transport')
        if command in ['test','stop']:
            child.add_argument('--pin',help='Six-digit screen code; omit to enter it privately')
        if command=='test':
            child.add_argument('--isolated',action='store_true',required=True)
            child.add_argument('--duration',type=float,help='Stop automatically after this many seconds')
    args=parser.parse_args()
    try:
        if args.command in ['status','stop']:
            return run_device(args)
        manifest,payload=validate(args.plugin)
        if args.command=='test':
            if args.duration is not None and not 0<args.duration<=840:
                raise InvalidPlugin('Duration must be between 0 and 840 seconds; a pairing expires after 15 minutes')
            device_subset(manifest,payload)
            with tempfile.TemporaryDirectory(prefix='hn-plugin-') as temporary:
                output=Path(temporary)/'test.hnplugin'
                package(args.plugin,output)
                return run_device(args,output.read_bytes(),manifest)
        print(f"Gyldig pluginpakke: {manifest['id']} {manifest['version']}")
        if args.command=='pack':
            print('SHA-256:',package(args.plugin,args.out))
        print('Kun lokal pakkevalidering. Intet er uploadet på en enhed.')
        return 0
    except (InvalidPlugin,DeviceError,OSError) as error:
        print('Fejl:',error,file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
