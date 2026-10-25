#!/usr/bin/env python3
"""Validate/package the draft plugin format. Does not execute or sandbox Lua."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import zipfile


class InvalidPlugin(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidPlugin(message)


def load_json(path):
    require(path.is_file() and not path.is_symlink(), f'Missing regular file: {path.name}')
    require(path.stat().st_size <= 16384, f'JSON too large: {path.name}')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError) as error:
        raise InvalidPlugin(f'Invalid JSON: {path.name}') from error


def validate(root):
    root = Path(root).resolve()
    manifest = load_json(root / 'plugin.json')
    require(isinstance(manifest, dict), 'Manifest must be an object')
    expected = {'schemaVersion','id','name','description','version','apiVersion','runtime','entry','license','boards','permissions','limits'}
    require(set(manifest) == expected, 'Unexpected/missing manifest fields')
    require(type(manifest['schemaVersion']) is int and manifest['schemaVersion'] == 1, 'Unsupported schema version')
    require(type(manifest['apiVersion']) is int and manifest['apiVersion'] == 1, 'Unsupported draft API version')
    require(manifest['runtime'] == 'lua-5.4' and manifest['entry'] == 'main.lua', 'Expected Lua source entry main.lua')
    require(isinstance(manifest['id'], str) and re.fullmatch(r'[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+', manifest['id']), 'Use a namespaced plugin id')
    for key, limit in [('name',80), ('description',500), ('license',80)]:
        require(isinstance(manifest[key], str) and 0 < len(manifest[key]) <= limit, f'Invalid {key}')
    require(isinstance(manifest['version'], str) and re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', manifest['version']), 'Expected semantic release version')
    require(manifest['boards'] == ['esp32-p4'], 'This draft template targets esp32-p4')
    permissions = manifest['permissions']
    require(isinstance(permissions,dict) and set(permissions) == {'network','mqttSubscribe','mqttPublish','storageBytes'}, 'Invalid permissions object')
    for key in ['network','mqttSubscribe','mqttPublish']:
        require(isinstance(permissions[key], list) and len(permissions[key]) <= 16 and all(isinstance(x,str) for x in permissions[key]), f'Invalid {key} permissions')
        require(len(set(permissions[key])) == len(permissions[key]), f'Duplicate {key} permission')
    for origin in permissions['network']:
        parts = urlsplit(origin)
        try:
            port = parts.port
        except ValueError as error:
            raise InvalidPlugin('Invalid origin port') from error
        require(parts.scheme in ['http','https'] and parts.hostname and not parts.username and not parts.password and not parts.path and not parts.query and not parts.fragment and '*' not in origin and (port is None or 1 <= port <= 65535), 'Use exact HTTP(S) origins without paths, credentials or wildcards')
    for topic in permissions['mqttSubscribe'] + permissions['mqttPublish']:
        require(0 < len(topic.encode('utf-8')) <= 128 and not any(c in topic for c in '#+\x00'), 'Use exact bounded MQTT topics')
    require(type(permissions['storageBytes']) is int and 0 <= permissions['storageBytes'] <= 65536, 'Storage quota exceeded')
    limits = manifest['limits']
    maxima = {'memoryBytes': 524288, 'instructionsPerCallback': 100000, 'packageBytes': 131072}
    require(isinstance(limits,dict) and set(limits) == set(maxima), 'Invalid limits object')
    for key, maximum in maxima.items():
        require(type(limits[key]) is int and 0 < limits[key] <= maximum, f'Invalid/excessive {key}')
    schema = load_json(root / 'config.schema.json')
    require(isinstance(schema,dict) and schema.get('type') == 'object' and schema.get('additionalProperties') is False, 'Settings schema must be a closed object')
    require(isinstance(schema.get('properties'),dict), 'Settings schema needs properties')
    # This checks packaging, not the entire JSON Schema specification or Lua syntax.
    names = ['plugin.json','main.lua','config.schema.json','LICENSE']
    assets = root / 'assets'
    require(not assets.is_symlink(), 'Asset symlinks are not allowed')
    if assets.exists():
        require(assets.is_dir(), 'assets must be a directory')
        for path in sorted(assets.rglob('*')):
            require(not path.is_symlink(), 'Asset symlinks are not allowed')
            if path.is_dir():
                continue
            require(path.suffix.lower() in ['.png','.jpg','.jpeg'], 'Only image assets are allowed')
            name = path.relative_to(root).as_posix()
            require(all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) and not part.startswith('.') for part in path.relative_to(root).parts), 'Invalid asset path')
            names.append(name)
    require(len(names) <= 64, 'Too many package files')
    payload = []
    for name in sorted(names):
        path = root / name
        require(path.is_file() and not path.is_symlink(), f'Missing regular package file: {name}')
        require(0 < path.stat().st_size <= 65536, f'Empty/oversize file: {name}')
        payload.append((name, path.read_bytes()))
    code = dict(payload)['main.lua']
    require(b'\x00' not in code and not code.startswith(b'\x1bLua'), 'Lua must be text, not bytecode')
    try:
        code.decode('utf-8')
    except UnicodeError as error:
        raise InvalidPlugin('Lua source must be UTF-8') from error
    require(sum(len(data) for _,data in payload) <= limits['packageBytes'], 'Expanded package exceeds manifest quota')
    return manifest, payload


def package(root, output):
    manifest, payload = validate(root)
    output = Path(output)
    # Prevent an output path overwriting a manifest, source or asset input.
    require(output.resolve() not in [(Path(root)/name).resolve() for name,_ in payload], 'Output may not replace plugin inputs')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in payload:
            info = zipfile.ZipInfo(name, date_time=(2026,1,1,0,0,0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--out')
    args = parser.parse_args()
    try:
        manifest, payload = validate(args.root)
        print(f"Draft package valid: {manifest['id']} {manifest['version']} ({len(payload)} files)")
        if args.out:
            print('SHA-256:', package(args.root,args.out))
        print('Packaging validation only. Device execution requires an owner-provisioned development core.')
    except (InvalidPlugin, OSError) as error:
        print(f'Invalid plugin: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
