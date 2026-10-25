#!/usr/bin/env python3
"""Draft public SDK: validation and packaging work; device transport is not implemented."""
import argparse
from pathlib import Path
import sys
from validate_plugin import validate, package, InvalidPlugin


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ['check','pack','test']:
        child=sub.add_parser(command)
        child.add_argument('plugin',type=Path)
        if command=='pack':child.add_argument('--out',type=Path,required=True)
        if command=='test':child.add_argument('--usb',action='store_true');child.add_argument('--isolated',action='store_true')
    args=parser.parse_args()
    if args.command=='test':
        print('Afventer den nye private core: Lua-loader og parret USB-transport er endnu ikke implementeret.',file=sys.stderr)
        return 2
    try:
        manifest,_=validate(args.plugin)
        print(f"Gyldig udkastspakke: {manifest['id']} {manifest['version']}")
        if args.command=='pack':print('SHA-256:',package(args.plugin,args.out))
        print('Kun lokal pakkevalidering. Intet er kørt eller uploadet på en enhed.')
        return 0
    except (InvalidPlugin,OSError) as error:
        print('Ugyldigt plugin:',error,file=sys.stderr)
        return 1


if __name__=='__main__':raise SystemExit(main())
