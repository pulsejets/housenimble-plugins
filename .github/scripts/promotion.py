#!/usr/bin/env python3
"""Validate the dev -> test -> main route; never deploy or use secrets."""
import json
import os
from pathlib import Path
import re
import subprocess


def validate(event, merged_tree=None, tested_tree=None):
    pr = event.get('pull_request')
    if not pr:
        raise ValueError('Expected a pull_request event')
    base = pr['base']['ref']
    head = pr['head']['ref']
    if base not in {'dev', 'test', 'main'}:
        raise ValueError('Unsupported target branch')
    expected = {'test': 'dev', 'main': 'test'}.get(base)
    if expected:
        if head != expected:
            raise ValueError(f'{base} accepts only {expected}')
        if pr['head'].get('repo', {}).get('full_name') != pr['base']['repo']['full_name']:
            raise ValueError('Promotion must originate in this repository')
    if base == 'main':
        sha = pr['head']['sha']
        if not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('Invalid test commit SHA')
        if f'Hardware-tested-commit: {sha}' not in (pr.get('body') or '').splitlines():
            raise ValueError('Record the exact physically tested test commit in the PR body')
        for field in ('Hardware-test-device', 'Hardware-test-result'):
            values = [line.partition(':')[2].strip() for line in (pr.get('body') or '').splitlines()
                      if line.startswith(field + ':')]
            if not values or not values[0] or values[0].startswith('<'):
                raise ValueError(f'Missing {field}')
        if not merged_tree or not tested_tree or merged_tree != tested_tree:
            raise ValueError('The production merge changes tested files; return changes to dev and retest')


def main():
    if os.environ.get('GITHUB_EVENT_NAME') != 'pull_request':
        print('No promotion PR. Direct-push prevention requires GitHub branch rules.')
        return
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    merged_tree = tested_tree = None
    if event['pull_request']['base']['ref'] == 'main':
        sha = event['pull_request']['head']['sha']
        if not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('Invalid test commit SHA')
        merged_tree = subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], text=True).strip()
        tested_tree = subprocess.check_output(['git', 'rev-parse', sha + '^{tree}'], text=True).strip()
    validate(event, merged_tree, tested_tree)
    print('Promotion route and required test evidence validated. Evidence is a human attestation.')


if __name__ == '__main__':
    main()
