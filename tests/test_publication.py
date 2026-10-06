"""Meaningful integrity, source-preservation, archive and offline-reader checks."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from tools import publication


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.payloads = {
            'README.md': b'# A source\n\nText </script><script>bad()</script> & <b>words</b>\n',
            'LICENSE': b'Original licence bytes\n',
            'language/quilt.k0': bytes(range(256)) + b'\x00\xff',
        }
        mount = self.root / 'vendor/example'
        for name, payload in self.payloads.items():
            destination = mount / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        self.lock = {'format': 'rasniki-hopput-source-lock', 'version': 1,
                     'title': 'Rasniki Hopput </script> science edition', 'edition': '1',
                     'repositories': [{'id': 'example', 'name': 'author/example',
                                       'requested_url': 'https://github.com/author/example',
                                       'url': 'https://github.com/author/example', 'commit': 'a' * 40,
                                       'mount_path': 'vendor/example', 'license_status': 'preserved-source-license',
                                       'files': {name: {'sha256': hashlib.sha256(payload).hexdigest(), 'size': len(payload)}
                                                 for name, payload in self.payloads.items()}}]}
        (self.root / 'publication').mkdir()
        self.write_lock()

    def write_lock(self):
        (self.root / 'publication/source-lock.json').write_text(json.dumps(self.lock), encoding='utf-8')

    def test_four_parallel_editions_retain_complete_body_and_distinct_guides(self):
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        body = (output / 'PUBLICATION.md').read_bytes()
        prefixes = []
        for name in ('MAX-RAWFUL.md', 'MAX-RAW.md', 'MAX-LAW.md', 'MAX-LAWFUL.md'):
            rendition = (output / name).read_bytes()
            self.assertTrue(rendition.endswith(body), name)
            prefixes.append(rendition[:-len(body)])
        self.assertEqual(len(set(prefixes)), 4)
        catalogue = json.loads((output / 'catalogue.json').read_text())
        self.assertEqual(len(catalogue['parallel_editions']), 4)
        self.assertTrue(all(entry['certification'] is False for entry in catalogue['parallel_editions']))
        html = (output / 'index.html').read_text()
        self.assertTrue(all(entry['file'] in html for entry in catalogue['parallel_editions']))

    def test_extra_complete_volume_includes_all_guides_and_full_body(self):
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        body = (output / 'PUBLICATION.md').read_bytes()
        combined = (output / 'EXTRA-COMPLETE.md').read_bytes()
        self.assertTrue(combined.endswith(body))
        preface = combined[:-len(body)].decode('utf-8')
        for name in ('Max Rawful', 'Max Raw', 'Max Law', 'Max Lawful'):
            self.assertIn('### ' + name + '\n', preface)
        catalogue = json.loads((output / 'catalogue.json').read_text())
        self.assertFalse(catalogue['extra_complete_edition']['certification'])
        self.assertIn('EXTRA-COMPLETE.md', (output / 'index.html').read_text())

    def test_rainbow_edition_retains_body_and_publishes_work_artifacts(self):
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        self.assertTrue((output / 'SCIENCERAINBOWRAINBOWSCIENCE.md').read_bytes().endswith((output / 'PUBLICATION.md').read_bytes()))
        paper = (output / 'SCIENCERAINBOWRAINBOWSCIENCE-PAPERWORK.html').read_text()
        self.assertEqual(paper.count('<section>'), 7)
        self.assertIn('299792458 m/s', paper)
        work = json.loads((output / 'SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json').read_text())
        self.assertEqual(work['samples'][0]['frequency_hz'], '428274940000000')
        catalogue = json.loads((output / 'catalogue.json').read_text())
        edition = catalogue['sciencerainbowrainbowscience_edition']
        hashes = json.loads((output / 'release-hashes.json').read_text())
        for key in ('file', 'paperwork', 'computerwork'):
            self.assertIn(edition[key], hashes['outputs'])
            self.assertIn(edition[key], (output / 'index.html').read_text())

    def test_ashram_numbered_edition_preserves_corpus_and_records_outputs(self):
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        body = (output / 'PUBLICATION.md').read_bytes()
        self.assertTrue((output / 'ASHRAM-SEQUENTIAL.md').read_bytes().endswith(body))
        lexicon = json.loads((output / 'ASHRAM-LEXICON.json').read_text())['terms']
        self.assertEqual([entry['number'] for entry in lexicon], list(range(1, len(lexicon) + 1)))
        spec = json.loads((output / 'ASHRAM-SPECIFICATION.json').read_text())
        self.assertEqual(spec['amplification']['ordered_pairs_per_form_and_kind'], 7**16)
        hashes = json.loads((output / 'release-hashes.json').read_text())
        for name in ('ASHRAM-SEQUENTIAL.md', 'ASHRAM-LEXICON.json', 'ASHRAM-SPECIFICATION.json'):
            self.assertIn(name, hashes['outputs'])
        self.assertIn('ASHRAM-SEQUENTIAL.md', (output / 'index.html').read_text())

    def test_huwster_complete_edition_and_full_rank_artifacts(self):
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        self.assertTrue((output / 'HUWSTER-RAWFUL.md').read_bytes().endswith((output / 'PUBLICATION.md').read_bytes()))
        architecture = json.loads((output / 'HUWSTER-ARCHITECTURE.json').read_text())
        self.assertEqual(architecture['default'], 'ostar-rawful')
        self.assertEqual(architecture['document_space'], 7**8)
        self.assertEqual(len(json.loads((output / 'HUWSTER-RANKS.json').read_text())['ranks']), 3087)
        self.assertFalse(json.loads((output / 'RAWFUL-CORPUS.json').read_text())['complete'])
        hashes = json.loads((output / 'release-hashes.json').read_text())
        for name in ('HUWSTER-RAWFUL.md', 'HUWSTER-ARCHITECTURE.json', 'HUWSTER-RANKS.json', 'RAWFUL-CORPUS.json'):
            self.assertIn(name, hashes['outputs'])

    def test_verifies_full_binary_and_licenses(self):
        result = publication.verify_sources(self.root)
        self.assertTrue(result['ok'])
        self.assertEqual(result['files'], 3)
        self.assertEqual(result['repositories'], 1)
        self.assertEqual(result['bytes'], sum(map(len, self.payloads.values())))
        self.assertEqual(result['errors'], [])

    def test_tampered_source_refuses_before_overwriting_outputs(self):
        output = self.root / 'publication/edition'
        output.mkdir()
        (output / 'index.html').write_bytes(b'preserve existing output')
        path = self.root / 'vendor/example/README.md'
        original = path.read_bytes()
        path.write_bytes(original.replace(b'Text', b'Fake'))
        self.assertFalse(publication.verify_sources(self.root)['ok'])
        with self.assertRaises(publication.PublicationError):
            publication.build(self.root)
        self.assertEqual((output / 'index.html').read_bytes(), b'preserve existing output')
        self.assertEqual(sorted(p.name for p in output.iterdir()), ['index.html'])

    def test_path_escape_is_invalid(self):
        self.lock['repositories'][0]['files']['../outside'] = {'sha256': '0' * 64, 'size': 0}
        self.write_lock()
        with self.assertRaises(publication.PublicationError):
            publication.load_lock(self.root)
        self.assertFalse(publication.verify_sources(self.root)['ok'])

    def test_symlink_source_and_overlapping_output_are_rejected(self):
        path = self.root / 'vendor/example/LICENSE'
        path.unlink()
        replacement = self.root / 'licence-copy'
        replacement.write_bytes(self.payloads['LICENSE'])
        path.symlink_to(replacement)
        self.assertFalse(publication.verify_sources(self.root)['ok'])
        path.unlink()
        path.write_bytes(self.payloads['LICENSE'])
        with self.assertRaises(publication.PublicationError):
            publication.build(self.root, 'vendor/example/generated')

    def test_deterministic_build_and_exact_archive_binary_roundtrip(self):
        first = self.root / 'publication/first'
        second = self.root / 'publication/second'
        publication.build(self.root, first)
        publication.build(self.root, second)
        for name in publication.OUTPUT_NAMES:
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)
        with zipfile.ZipFile(first / 'sources.zip') as archive:
            for name, payload in self.payloads.items():
                self.assertEqual(archive.read('example/' + name), payload)
                info = archive.getinfo('example/' + name)
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
            self.assertEqual(archive.read('_publication/source-lock.json'),
                             (self.root / 'publication/source-lock.json').read_bytes())
        for name, payload in self.payloads.items():
            self.assertEqual((self.root / 'vendor/example' / name).read_bytes(), payload)

    def test_offline_html_inerts_payload_and_preserves_text(self):
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        html = (output / 'index.html').read_text('utf-8')
        embedded = html.split('<script id="reader-data" type="application/json">', 1)[1].split('</script>', 1)[0]
        self.assertNotIn('<', embedded)
        data = json.loads(embedded)
        self.assertEqual(data['documents'][0]['text'], self.payloads['README.md'].decode())
        self.assertEqual(data['title'], self.lock['title'])
        self.assertNotIn('innerHTML', html)
        self.assertNotIn('eval(', html)
        self.assertNotIn('fetch(', html)
        self.assertIn('.textContent=doc.text', html)
        if shutil.which('node'):
            script = output / 'reader-check.js'
            script.write_text(html.rsplit('<script>', 1)[1].split('</script>', 1)[0], encoding='utf-8')
            check = subprocess.run(['node', '--check', str(script)], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_sorted_catalogue_and_hashes_current_documents(self):
        (self.root / 'publication/catalogue-source.json').write_text(json.dumps({
            'components': [{'id': 'z'}, {'id': 'a'}], 'glossary': [{'term': 'zeta'}, {'term': 'alpha'}]}))
        (self.root / 'docs').mkdir()
        (self.root / 'docs/MINISTRY.md').write_text('# Ministry\nFictional vocabulary, distinct from K0.\n')
        result = publication.build(self.root)
        output = Path(result['output_dir'])
        catalogue = json.loads((output / 'catalogue.json').read_text())
        self.assertEqual([c['id'] for c in catalogue['components']], ['a', 'z'])
        self.assertEqual([t['term'] for t in catalogue['terms']], ['alpha', 'zeta'])
        hashes = json.loads((output / 'release-hashes.json').read_text())
        self.assertIn('docs/MINISTRY.md', hashes['current_editorial_inputs'])
        for name, record in hashes['outputs'].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), record['sha256'])

    def test_check_detects_changed_output_without_writing(self):
        publication.build(self.root)
        arguments = ['build', '--root', str(self.root), '--check']
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(publication.main(arguments), 0)
        path = self.root / 'publication/edition/PUBLICATION.md'
        path.write_bytes(b'changed')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(publication.main(arguments), 1)
        self.assertEqual(path.read_bytes(), b'changed')

    def test_source_size_budget_is_enforced(self):
        self.lock['repositories'][0]['files']['README.md']['size'] = publication.MAX_SOURCE_BYTES + 1
        self.write_lock()
        with self.assertRaises(publication.PublicationError):
            publication.load_lock(self.root)

    def test_duplicate_markdown_retains_both_source_records(self):
        repository = json.loads(json.dumps(self.lock['repositories'][0]))
        repository.update(id='second', name='author/second', mount_path='vendor/second')
        repository['files'] = {'README.md': repository['files']['README.md']}
        (self.root / 'vendor/second').mkdir()
        (self.root / 'vendor/second/README.md').write_bytes(self.payloads['README.md'])
        self.lock['repositories'].append(repository)
        self.write_lock()
        result = publication.build(self.root)
        reader = json.loads((Path(result['output_dir']) / 'reader-data.json').read_text())
        self.assertEqual(len(reader['documents']), 1)
        self.assertEqual([source['repository'] for source in reader['documents'][0]['sources']], ['example', 'second'])
        self.assertEqual(result['files'], 4)

    def test_malformed_urls_report_explicit_errors(self):
        self.lock['repositories'][0]['url'] = 'https://[invalid'
        self.write_lock()
        result = publication.verify_sources(self.root)
        self.assertFalse(result['ok'])
        self.assertTrue(result['errors'])

    def test_lair_tree_covers_every_source_file_with_unique_parent_links(self):
        self.lock['subtitle'] = 'Lair of Lairs — Recursive Form, Format and Formate'
        self.write_lock()
        (self.root / 'docs').mkdir()
        (self.root / 'docs/LAIR-OF-LAIRS.md').write_text('# Lair\nFinite nested paths.\n')
        result = publication.build(self.root)
        data = json.loads((Path(result['output_dir']) / 'reader-data.json').read_text())
        tree = data['lair']
        nodes = {node['id']: node for node in tree['nodes']}
        self.assertEqual(len(nodes), len(tree['nodes']))
        self.assertEqual(len(nodes), tree['node_count'])
        self.assertIsNone(nodes[tree['root_id']]['parent'])
        self.assertEqual(tree['source_file_count'], len(self.payloads))
        self.assertEqual(tree['editorial_file_count'], 1)
        leaves = [node for node in nodes.values() if node['kind'] == 'file' and node['repository'] == 'example']
        self.assertEqual({node['path'] for node in leaves}, set(self.payloads))
        self.assertEqual({node['archive_path'] for node in leaves}, {'example/' + name for name in self.payloads})
        self.assertEqual(len(data['chambers']), 7)
        self.assertEqual(data['subtitle'], self.lock['subtitle'])
        pending, visited = [tree['root_id']], set()
        while pending:
            node_id = pending.pop()
            self.assertNotIn(node_id, visited)
            visited.add(node_id)
            node = nodes[node_id]
            self.assertLessEqual(node['depth'], publication.MAX_LAIR_DEPTH)
            for child_id in node['children']:
                child = nodes[child_id]
                self.assertEqual(child['parent'], node_id)
                self.assertEqual(child['depth'], node['depth'] + 1)
                pending.append(child_id)
        self.assertEqual(visited, set(nodes))
        binary = next(node for node in leaves if node['path'].endswith('.k0'))
        self.assertNotIn('document_sha256', binary)
        markdown = next(node for node in leaves if node['path'].endswith('.md'))
        self.assertEqual(markdown['document_sha256'], hashlib.sha256(self.payloads['README.md']).hexdigest())
        second = publication.build(self.root, 'publication/second')
        second_tree = json.loads((Path(second['output_dir']) / 'reader-data.json').read_text())['lair']
        self.assertEqual(tree, second_tree)

    def test_lair_depth_and_node_budgets_refuse_unbounded_expansion(self):
        deep = '/'.join(['directory'] * publication.MAX_LAIR_DEPTH + ['file.bin'])
        lock = json.loads(json.dumps(self.lock))
        record = {'sha256': 'a' * 64, 'size': 0}
        lock['repositories'][0]['files'] = {deep: record}
        with self.assertRaises(publication.PublicationError):
            publication._lair(lock, {}, set())
        lock['repositories'][0]['files'] = {f'file-{index}.bin': record for index in range(publication.MAX_LAIR_NODES)}
        with self.assertRaises(publication.PublicationError):
            publication._lair(lock, {}, set())


if __name__ == '__main__':
    unittest.main()
