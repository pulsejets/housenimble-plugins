import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('promotion', Path(__file__).with_name('promotion.py'))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
SHA = 'a' * 40


def event(base='main', head='test'):
    return {'pull_request': {'base': {'ref': base, 'repo': {'full_name': 'owner/repo'}},
        'head': {'ref': head, 'sha': SHA, 'repo': {'full_name': 'owner/repo'}},
        'body': f'Hardware-tested-commit: {SHA}\nHardware-test-device: P4 rev1.3\nHardware-test-result: Passed offline/reconnect/restart'}}


class PromotionTests(unittest.TestCase):
    def test_expected_route(self):
        policy.validate(event('test', 'dev'))
        policy.validate(event(), 'tree', 'tree')
        policy.validate(event('dev', 'codex/example'))

    def test_skip_test_and_wrong_source_blocked(self):
        for base, head in [('main', 'dev'), ('test', 'codex/example'), ('main', 'hotfix')]:
            with self.subTest(base=base, head=head), self.assertRaises(ValueError):
                policy.validate(event(base, head), 'tree', 'tree')

    def test_fork_cannot_promote(self):
        for base, head in [('main', 'test'), ('test', 'dev')]:
            e = event(base, head)
            e['pull_request']['head']['repo']['full_name'] = 'fork/repo'
            with self.assertRaises(ValueError):
                policy.validate(e, 'tree', 'tree')

    def test_old_or_missing_hardware_evidence_blocked(self):
        for body in ['', 'Hardware-tested-commit: ' + 'b' * 40, event()['pull_request']['body'].replace('P4 rev1.3', '<device>')]:
            e = event()
            e['pull_request']['body'] = body
            with self.assertRaises(ValueError):
                policy.validate(e, 'tree', 'tree')

    def test_new_test_commit_invalidates_evidence(self):
        e = event()
        e['pull_request']['head']['sha'] = 'b' * 40
        with self.assertRaises(ValueError):
            policy.validate(e, 'tree', 'tree')

    def test_untested_merge_changes_blocked(self):
        with self.assertRaises(ValueError):
            policy.validate(event(), 'changed-tree', 'tested-tree')

    def test_missing_tree_proof_blocked(self):
        with self.assertRaises(ValueError):
            policy.validate(event())

    def test_invalid_event_blocked(self):
        with self.assertRaises(ValueError):
            policy.validate({})


if __name__ == '__main__':
    unittest.main()
