#!/usr/bin/env python3
"""Integrity regression tests using only synthetic, disposable local artifacts.

Run with: python3 scripts/test_validate_evidence.py
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


VALIDATOR_PATH = Path(__file__).with_name('validate_evidence.py')
SPEC = importlib.util.spec_from_file_location('evidence_validator_under_test', VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='diligence-validator-test-')
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.root = self.workspace / 'case'
        self.root.mkdir()
        self.html = self.root / 'report.html'
        self.html.write_text(
            '<!doctype html><html><head><style>body{color:#111}</style></head>'
            '<body><h1 id="finding">Synthetic finding</h1>'
            '<a href="#finding">Finding</a><a href="notes.html#receipt">Receipt</a>'
            '<a href="capture.txt">Text capture</a></body></html>', encoding='utf-8')
        (self.root / 'notes.html').write_text('<p id="receipt">Synthetic receipt</p>', encoding='utf-8')
        raw = self.artifact('capture.bin', b'\x00Synthetic raw capture\xff\n')
        extracted = self.artifact('capture.txt', b'Synthetic extracted capture.\n')
        receipt = self.artifact('experiment.log', b'control=success; fault=observed; external_calls=0\n')
        self.data = {
            'schema_version': 1,
            'subject': {'name': 'Synthetic organization', 'as_of': '2000-01-01', 'decision': 'Exercise validation'},
            'sources': [{
                'id': 'S1', 'title': 'Synthetic source', 'accessed_at': '2000-01-01T00:00:00Z',
                'publisher_group': 'synthetic-publisher', 'scope': 'Fixture only',
                'evidence_class': 'provided_document', 'url': None, 'artifacts': [raw, extracted],
            }],
            'experiments': [{
                'id': 'E1', 'revision': 'synthetic-revision', 'environment': 'Isolated fixture',
                'command': 'synthetic-command', 'expected': 'Bounded recovery', 'observed': 'Synthetic failure',
                'control': 'Synthetic normal path succeeds', 'scope_limit': 'No real system tested',
                'artifacts': [receipt],
            }],
            'findings': [{
                'id': 'F1', 'lens': 'reliability', 'title': 'Synthetic finding', 'claim': 'Fixture claim',
                'impact': 'Fixture impact', 'recommendation': 'Fixture recommendation',
                'validation': 'Inspect synthetic receipt', 'boundary': 'Synthetic scope',
                'evidence_grade': 'reproduced', 'severity': 'low', 'confidence': 'high',
                'source_ids': ['S1'], 'experiment_ids': ['E1'],
            }],
            'assumptions': [{'id': 'A1', 'name': 'Synthetic multiplier', 'unit': 'ratio', 'rationale': 'Fixture', 'value': 2}],
            'metrics': [
                self.metric('M1', 'documented', 3, source_ids=['S1']),
                self.metric('M2', 'assumed', 2, assumption_ids=['A1']),
                self.metric('M3', 'derived', 6, formula='M1 * A1', input_ids=['M1', 'A1']),
                self.metric('M4', 'unknown', None),
            ],
        }

    def artifact(self, relative, contents):
        (self.root / relative).write_bytes(contents)
        return {'path': relative, 'sha256': hashlib.sha256(contents).hexdigest()}

    @staticmethod
    def metric(ident, basis, value, **extra):
        return {'id': ident, 'name': 'Synthetic metric', 'unit': 'count', 'period': 'Fixture period',
                'population': 'Synthetic population', 'basis': basis, 'value': value, **extra}

    def check_rejected(self, data=None, message=None, html=False):
        result = VALIDATOR.validate(self.data if data is None else data, self.root, self.html if html else None)
        self.assertEqual(result['status'], 'failed', result)
        self.assertTrue(result['errors'], result)
        if message:
            self.assertTrue(any(message in error for error in result['errors']), result['errors'])
        return result

    def run_cli(self, payload, html=False):
        ledger = self.root / 'ledger.json'
        ledger.write_text(payload, encoding='utf-8')
        command = [sys.executable, str(VALIDATOR_PATH), str(ledger), '--root', str(self.root)]
        if html:
            command.extend(['--html', str(self.html)])
        return subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)

    def test_valid_dataset_and_local_html(self):
        result = VALIDATOR.validate(self.data, self.root, self.html)
        self.assertEqual(result['status'], 'passed', result)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['counts']['artifact_pairs'], 3)
        self.assertEqual(result['counts']['html_links'], 3)
        self.assertTrue(all(capture['matches'] for capture in result['captures']))

    def test_valid_cli_exits_zero(self):
        result = self.run_cli(json.dumps(self.data), html=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)['status'], 'passed')

    def test_raw_and_extracted_text_tampering_are_detected(self):
        for relative in ('capture.bin', 'capture.txt'):
            with self.subTest(artifact=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b'TAMPERED')
                try:
                    result = self.check_rejected(message='hash mismatch')
                    mismatch = [item for item in result['captures'] if not item['matches']]
                    self.assertEqual([item['path'] for item in mismatch], [relative])
                finally:
                    path.write_bytes(original)

    def test_missing_capture_is_rejected(self):
        (self.root / 'capture.bin').unlink()
        self.check_rejected(message='missing file')

    def test_artifact_traversal_is_rejected_even_when_hash_matches(self):
        contents = b'Synthetic external file'
        (self.workspace / 'outside.bin').write_bytes(contents)
        self.data['sources'][0]['artifacts'][0] = {
            'path': '../outside.bin', 'sha256': hashlib.sha256(contents).hexdigest()}
        self.check_rejected(message='path escapes investigation root')

    def test_artifact_symlink_escape_is_rejected(self):
        outside = self.workspace / 'outside.bin'
        contents = b'Synthetic external file'
        outside.write_bytes(contents)
        (self.root / 'escape.bin').symlink_to(outside)
        self.data['sources'][0]['artifacts'][0] = {
            'path': 'escape.bin', 'sha256': hashlib.sha256(contents).hexdigest()}
        self.check_rejected(message='path escapes investigation root')

    def test_html_link_traversal_is_rejected(self):
        (self.workspace / 'outside.txt').write_text('Synthetic outside file', encoding='utf-8')
        self.html.write_text('<a href="%2e%2e/outside.txt">Outside</a>', encoding='utf-8')
        self.check_rejected(message='path escapes investigation root', html=True)

    def test_missing_same_page_and_cross_page_fragments_are_rejected(self):
        for target in ('#absent', 'notes.html#absent'):
            with self.subTest(target=target):
                self.html.write_text(f'<a href="{target}">Missing</a>', encoding='utf-8')
                self.check_rejected(message='missing HTML fragment', html=True)

    def test_unknown_metric_cannot_be_zero(self):
        self.data['metrics'][3]['value'] = 0
        self.check_rejected(message='unknown value must be null')

    def test_reproduced_finding_requires_experiment_reference(self):
        for references in ([], ['E-missing']):
            with self.subTest(references=references):
                self.data['findings'][0]['experiment_ids'] = references
                self.check_rejected(message='experiment_ids')

    def test_experiment_requires_saved_receipt(self):
        self.data['experiments'][0]['artifacts'] = []
        self.check_rejected(message='saved experiment artifacts required')

    def test_derived_metric_requires_resolvable_inputs(self):
        self.data['metrics'][2]['input_ids'] = ['M-missing']
        self.check_rejected(message='unresolved input_ids')

    def test_derived_metric_requires_formula_and_inputs(self):
        self.data['metrics'][2].update(formula='', input_ids=[])
        result = self.check_rejected(message='formula')
        self.assertTrue(any('input_ids must not be empty' in error for error in result['errors']))

    def test_derived_dependency_cycles_are_rejected(self):
        for dependencies in (['M3'], ['M5']):
            with self.subTest(dependencies=dependencies):
                data = copy.deepcopy(self.data)
                data['metrics'][2]['input_ids'] = dependencies
                if dependencies == ['M5']:
                    data['metrics'].append(self.metric('M5', 'derived', 6, formula='M3', input_ids=['M3']))
                self.check_rejected(data, 'dependency cycle')

    def test_duplicate_record_ids_are_rejected(self):
        for collection in ('sources', 'experiments', 'findings', 'metrics', 'assumptions'):
            with self.subTest(collection=collection):
                data = copy.deepcopy(self.data)
                data[collection].append(copy.deepcopy(data[collection][0]))
                self.check_rejected(data, 'duplicate id')

    def test_metric_assumption_id_collision_is_rejected(self):
        self.data['assumptions'][0]['id'] = 'M1'
        self.check_rejected(message='metric and assumption IDs must not collide')

    def test_duplicate_html_ids_are_rejected(self):
        self.html.write_text('<p id="same">One</p><p id="same">Two</p>', encoding='utf-8')
        self.check_rejected(message='HTML IDs must be unique', html=True)

    def test_malformed_root_and_collection_shapes_return_errors(self):
        for data in ([], 'invalid root', {'schema_version': 1, 'sources': {}, 'findings': [None]}):
            with self.subTest(data=data):
                self.check_rejected(data)

    def test_malformed_subject_returns_errors_without_crashing(self):
        for subject in ('invalid subject', ['invalid subject'], 1):
            with self.subTest(subject=subject):
                data = copy.deepcopy(self.data)
                data['subject'] = subject
                self.check_rejected(data, 'subject must be an object')

    def test_malformed_enum_values_return_errors_without_crashing(self):
        for collection, field in (('sources', 'evidence_class'), ('findings', 'evidence_grade'),
                                  ('findings', 'severity'), ('findings', 'confidence'), ('metrics', 'basis')):
            with self.subTest(collection=collection, field=field):
                data = copy.deepcopy(self.data)
                data[collection][0][field] = []
                self.check_rejected(data)

    def test_malformed_derived_id_returns_errors_without_crashing(self):
        self.data['metrics'][2]['id'] = ['invalid id']
        self.check_rejected(message='missing text id')

    def test_malformed_url_returns_errors_without_crashing(self):
        self.data['sources'][0]['url'] = 'https://[invalid-host'
        self.check_rejected(message='url')

    def test_invalid_json_cli_exits_one_with_structured_error(self):
        result = self.run_cli('{invalid json')
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'failed')

    def test_malformed_structure_cli_exits_one_with_structured_error(self):
        self.data['subject'] = 'invalid subject'
        result = self.run_cli(json.dumps(self.data))
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'failed')


if __name__ == '__main__':
    unittest.main(verbosity=2)
