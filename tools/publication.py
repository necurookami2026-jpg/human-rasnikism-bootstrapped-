#!/usr/bin/env python3
"""Verify pinned source snapshots and build an offline Rasniki publication.

Source files are data: this tool neither imports nor executes their contents.
Only its named derived outputs may be replaced. No network is used.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from urllib.parse import quote, urlsplit
import zipfile


MAX_SOURCE_BYTES = 25 * 1024 * 1024
MAX_LAIR_DEPTH = 32
MAX_LAIR_NODES = 4096
OUTPUT_NAMES = (
    'SCIENCERAINBOWRAINBOWSCIENCE.md', 'SCIENCERAINBOWRAINBOWSCIENCE-PAPERWORK.html',
    'SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json',
    'catalogue.json', 'reader-data.json', 'index.html', 'PUBLICATION.md',
    'sources.zip', 'release-hashes.json',
    'MAX-RAWFUL.md', 'MAX-RAW.md', 'MAX-LAW.md', 'MAX-LAWFUL.md', 'EXTRA-COMPLETE.md',
)
CURRENT_DOCUMENTS = (
    'docs/IOBOT-SCIENTIFIC-RESPONSES.md',
    'docs/EXACT-SCIENCERAINBOWRAINBOWSCIENCE.md',
    'docs/REPUBLICATION.md',
    'docs/FOUR-PARALLEL-EDITIONS.md',
    'docs/OFFLINE-ADULT-ROMANCE-AND-COPING.md',
    'docs/MEDIA-STANDARDISATION-AND-UPDATES.md', 'extensions/instagram-orange/README.md',
    'docs/BOOTSTRAP.md', 'docs/CONFLICT-PROTECTION-LIBRARY.md', 'docs/IMPLEMENTATION.md',
    'docs/LAIR-OF-LAIRS.md', 'docs/MINISTRY.md', 'docs/OMNIARCHY.md', 'docs/PROVENANCE.md',
    'docs/SPIRITUAL-SYMBOLIC-WORKBENCH.md', 'docs/conflict/README.md',
    'docs/conflict/01-purpose-and-scope.md', 'docs/conflict/02-access-and-participation.md',
    'docs/conflict/03-consent-and-boundaries.md', 'docs/conflict/04-incident-notes.md',
    'docs/conflict/05-de-escalation-and-dialogue.md', 'docs/conflict/06-evidence-custody.md',
    'docs/conflict/07-correction-and-review.md', 'docs/conflict/08-civilian-aid-coordination.md',
    'docs/conflict/09-simulation-and-learning.md', 'docs/conflict/10-handover-and-continuity.md',
    'docs/DEMO-ECONOMY-CONTRACTS.md', 'docs/OWNER-RECOVERY.md',
    'docs/MEDIA-DATA-RENDITION.md', 'docs/SAFEGUARDING-AND-DEVICE-SCOPE.md',
    'docs/RECURSIVE-SYSTEMS-ATLAS.md', 'docs/RECURSIVE-WORKBENCH.md', 'docs/handbooks/README.md',
    'docs/handbooks/01-advice-and-guidance.md', 'docs/handbooks/02-immanuel-emmanuel-manual.md',
    'docs/handbooks/03-family-and-classical-governance.md', 'docs/handbooks/04-logistics-and-rudder.md',
    'docs/handbooks/05-fandom-merchandise-and-number-seeds.md', 'docs/handbooks/06-media-radio-and-pixel-notation.md',
    'docs/handbooks/07-learning-mentoring-and-recipes.md', 'docs/handbooks/08-mapping-time-and-adaptation.md',
    'docs/handbooks/09-community-surveys-and-quests.md', 'docs/handbooks/10-self-reported-preferences.md',
    'docs/handbooks/11-accessible-guardrails-and-recovery.md', 'docs/handbooks/12-document-types-and-workpapers.md',
)
CHAMBERS = (
    {'id': 'threshold', 'name': 'Threshold · dictionary', 'query': 'glossary', 'guide': 'Find terms, aliases and definitions before adopting their use.'},
    {'id': 'memory', 'name': 'Memory · provenance', 'query': 'provenance', 'guide': 'Trace a source, its pinned revision and the record of its inclusion.'},
    {'id': 'workroom', 'name': 'Workroom · maintenance', 'query': 'maintenance', 'guide': 'Inspect repeatable upkeep and the limits of an implementation.'},
    {'id': 'turning', 'name': 'Turning · reform', 'query': 'reform', 'guide': 'Review changes of substance and changes of representation.'},
    {'id': 'gathering', 'name': 'Gathering · curriculum', 'query': 'curriculum', 'guide': 'Choose a learning exercise with concrete acceptance evidence.'},
    {'id': 'writing', 'name': 'Writing · prose', 'query': 'prose', 'guide': 'Read the charter, explanatory stanzas and editorial formation.'},
    {'id': 'machine', 'name': 'Machine · code', 'query': 'kerot', 'guide': 'Follow source programs and their declared host and ISA boundaries.'},
)


class PublicationError(ValueError):
    """Invalid metadata, changed source, or unsafe output destination."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def _relative(value, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or '\\' in value or any(ord(c) < 32 for c in value):
        raise PublicationError(f'{label}: expected a safe relative POSIX path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise PublicationError(f'{label}: absolute paths and path traversal are forbidden')
    return path


def _source_path(root: Path, relative: str) -> Path:
    parts = _relative(relative, 'source path').parts
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise PublicationError(f'Source symlink is forbidden: {relative}')
    if not path.resolve().is_relative_to(root):
        raise PublicationError(f'Source escapes publication root: {relative}')
    return path


def _url(value, label: str):
    if not isinstance(value, str):
        raise PublicationError(f'{label}: expected an HTTPS URL')
    try:
        parsed = urlsplit(value)
    except ValueError as error:
        raise PublicationError(f'{label}: malformed URL') from error
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise PublicationError(f'{label}: expected an HTTPS URL without credentials')


def load_lock(root) -> dict:
    """Load and validate publication/source-lock.json without reading payloads."""
    root = Path(root).resolve()
    try:
        data = json.loads(_source_path(root, 'publication/source-lock.json').read_text('utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicationError(f'Cannot read source lock: {error}') from error
    if not isinstance(data, dict) or data.get('format') != 'rasniki-hopput-source-lock' or type(data.get('version')) is not int or data['version'] != 1:
        raise PublicationError('Unsupported source-lock format or version')
    if not isinstance(data.get('title'), str) or not data['title'] or not isinstance(data.get('edition'), str):
        raise PublicationError('Source lock requires a title and string edition')
    if 'subtitle' in data and (not isinstance(data['subtitle'], str) or not data['subtitle']):
        raise PublicationError('Source-lock subtitle must be a nonempty string')
    repositories = data.get('repositories')
    if not isinstance(repositories, list) or not repositories:
        raise PublicationError('Source lock requires at least one repository')
    ids, mounts, total = set(), [], 0
    for repository in repositories:
        if not isinstance(repository, dict):
            raise PublicationError('Repository record must be an object')
        repo_id = repository.get('id')
        if not isinstance(repo_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', repo_id) or repo_id in ids:
            raise PublicationError('Repository IDs must be unique safe lowercase identifiers')
        ids.add(repo_id)
        for field in ('name', 'license_status'):
            if not isinstance(repository.get(field), str) or not repository[field]:
                raise PublicationError(f'{repo_id}: missing {field}')
        for field in ('requested_url', 'url'):
            _url(repository.get(field), f'{repo_id} {field}')
        if not isinstance(repository.get('commit'), str) or not re.fullmatch(r'[0-9a-f]{40}', repository['commit']):
            raise PublicationError(f'{repo_id}: expected a full lowercase Git commit SHA')
        mount = _relative(repository.get('mount_path'), f'{repo_id} mount_path')
        mounts.append(mount)
        files = repository.get('files')
        if not isinstance(files, dict) or not files:
            raise PublicationError(f'{repo_id}: files must be a nonempty object')
        for relative, record in files.items():
            _relative(relative, f'{repo_id} file')
            if not isinstance(record, dict):
                raise PublicationError(f'{repo_id}/{relative}: missing size and sha256')
            size, digest = record.get('size'), record.get('sha256')
            if type(size) is not int or size < 0:
                raise PublicationError(f'{repo_id}/{relative}: invalid byte size')
            if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise PublicationError(f'{repo_id}/{relative}: invalid SHA-256')
            total += size
    for index, left in enumerate(mounts):
        for right in mounts[index + 1:]:
            if left == right or left in right.parents or right in left.parents:
                raise PublicationError('Repository snapshot mounts must not overlap')
    if total > MAX_SOURCE_BYTES:
        raise PublicationError(f'Pinned source bytes exceed {MAX_SOURCE_BYTES}')
    return data


def _capture(root: Path, lock: dict) -> tuple[dict, dict]:
    result = {'ok': True, 'repositories': 0, 'files': 0, 'bytes': 0, 'errors': []}
    captured = {}
    for repository in sorted(lock['repositories'], key=lambda item: (item['name'].casefold(), item['id'])):
        repo_ok = True
        for relative, record in sorted(repository['files'].items()):
            source_name = repository['mount_path'] + '/' + relative
            try:
                source = _source_path(root, source_name)
                if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
                    raise PublicationError(f'Not a regular source file: {source_name}')
                if source.stat().st_size != record['size']:
                    raise PublicationError(f'Size mismatch: {source_name}')
                with source.open('rb') as stream:
                    payload = stream.read(record['size'] + 1)
                if len(payload) != record['size'] or _sha(payload) != record['sha256']:
                    raise PublicationError(f'SHA-256 or size mismatch: {source_name}')
                captured[(repository['id'], relative)] = payload
                result['files'] += 1
                result['bytes'] += len(payload)
            except (OSError, PublicationError) as error:
                repo_ok = False
                result['errors'].append(str(error))
        result['repositories'] += int(repo_ok)
    result['ok'] = not result['errors']
    return result, captured


def verify_sources(root) -> dict:
    """Return explicit verified counts, bytes, and errors for all pinned sources."""
    root = Path(root).resolve()
    try:
        lock = load_lock(root)
        return _capture(root, lock)[0]
    except (OSError, PublicationError) as error:
        return {'ok': False, 'repositories': 0, 'files': 0, 'bytes': 0, 'errors': [str(error)]}


def _local_data(root: Path) -> tuple[dict, dict, dict]:
    catalogue, documents, hashes = {}, {}, {}
    for name in ('publication/catalogue-source.json', 'docs/franchise-manifest.json'):
        path = _source_path(root, name)
        if path.is_file():
            payload = path.read_bytes()
            try:
                catalogue = json.loads(payload)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise PublicationError(f'Invalid catalogue source {name}: {error}') from error
            if not isinstance(catalogue, dict):
                raise PublicationError(f'Catalogue source {name} must be an object')
            hashes[name] = {'sha256': _sha(payload), 'size': len(payload)}
            break
    for name in CURRENT_DOCUMENTS:
        path = _source_path(root, name)
        if path.is_file():
            payload = path.read_bytes()
            try:
                documents[name] = payload.decode('utf-8')
            except UnicodeError as error:
                raise PublicationError(f'Invalid UTF-8 document {name}') from error
            hashes[name] = {'sha256': _sha(payload), 'size': len(payload)}
    return catalogue, documents, hashes


def _lair(lock: dict, current: dict, markdown_hashes: set) -> dict:
    """Index every original source path with bounded depth and explicit parents."""
    nodes = {}

    def add(node):
        if node['id'] in nodes:
            raise PublicationError('Duplicate lair node ID')
        if node['depth'] > MAX_LAIR_DEPTH:
            raise PublicationError(f'Lair depth exceeds {MAX_LAIR_DEPTH}: {node.get("path", node["id"])}')
        if len(nodes) >= MAX_LAIR_NODES:
            raise PublicationError(f'Lair node count exceeds {MAX_LAIR_NODES}')
        node['children'] = []
        nodes[node['id']] = node
        if node['parent'] is not None:
            nodes[node['parent']]['children'].append(node['id'])
        return node['id']

    def stable_id(scope, kind, path):
        return 'lair-' + kind + '-' + _sha((scope + '\0' + kind + '\0' + path).encode('utf-8'))

    root_id = add({'id': 'lair-collection', 'kind': 'collection', 'name': lock['title'], 'parent': None, 'depth': 0, 'path': ''})

    def add_files(scope, parent, files, repository=None):
        directories = {'': parent}
        for path, record in sorted(files.items()):
            parts = _relative(path, 'lair file').parts
            for index in range(1, len(parts)):
                directory = '/'.join(parts[:index])
                if directory not in directories:
                    previous = '/'.join(parts[:index - 1])
                    directories[directory] = add({'id': stable_id(scope, 'directory', directory),
                                                  'kind': 'directory', 'name': parts[index - 1], 'path': directory,
                                                  'parent': directories[previous], 'depth': index + 1, 'repository': scope})
            previous = '/'.join(parts[:-1])
            node = {'id': stable_id(scope, 'file', path), 'kind': 'file', 'name': parts[-1], 'path': path,
                    'parent': directories[previous], 'depth': len(parts) + 1, 'repository': scope,
                    'sha256': record['sha256'], 'size': record['size'],
                    'content_kind': 'readable-markdown' if record['sha256'] in markdown_hashes and PurePosixPath(path).suffix.lower() == '.md' else 'archive-source'}
            if node['content_kind'] == 'readable-markdown':
                node['document_sha256'] = record['sha256']
            if repository is not None:
                node['archive_path'] = repository['id'] + '/' + path
                node['url'] = repository['url'].rstrip('/') + '/blob/' + repository['commit'] + '/' + quote(path, safe='/')
            else:
                node['content_kind'] = 'editorial-markdown'
                node['archive_path'] = None
            add(node)

    for repository in sorted(lock['repositories'], key=lambda item: (item['name'].casefold(), item['id'])):
        source_id = add({'id': 'lair-source-' + repository['id'], 'kind': 'source', 'name': repository['name'],
                         'path': '', 'parent': root_id, 'depth': 1, 'repository': repository['id'],
                         'commit': repository['commit'], 'license_status': repository['license_status'], 'url': repository['url']})
        add_files(repository['id'], source_id, repository['files'], repository)
    if current:
        editorial_id = add({'id': 'lair-editorial', 'kind': 'editorial', 'name': 'Current editorial documentation',
                            'path': '', 'parent': root_id, 'depth': 1, 'repository': 'current-editorial'})
        add_files('current-editorial', editorial_id,
                  {path: {'sha256': _sha(text.encode('utf-8')), 'size': len(text.encode('utf-8'))} for path, text in current.items()})
    for node in nodes.values():
        node['children'].sort(key=lambda child: (nodes[child]['kind'] == 'file', nodes[child]['name'].casefold(), child))
    return {'format': 'rasniki-lair-tree', 'version': 1, 'root_id': root_id, 'nodes': list(nodes.values()),
            'max_depth': MAX_LAIR_DEPTH, 'max_nodes': MAX_LAIR_NODES, 'node_count': len(nodes),
            'source_file_count': sum(len(repository['files']) for repository in lock['repositories']),
            'editorial_file_count': len(current), 'scope': 'Finite indexed paths; no infinite expansion or source execution.'}


def _reader(lock: dict, captured: dict, current: dict) -> dict:
    by_hash = {}
    for repository in sorted(lock['repositories'], key=lambda item: (item['name'].casefold(), item['id'])):
        for relative in sorted(repository['files']):
            if PurePosixPath(relative).suffix.lower() != '.md':
                continue
            payload = captured[(repository['id'], relative)]
            try:
                text = payload.decode('utf-8')
            except UnicodeError as error:
                raise PublicationError(f'Cannot read Markdown as UTF-8: {repository["id"]}/{relative}') from error
            digest = _sha(payload)
            record = by_hash.setdefault(digest, {'sha256': digest, 'text': text, 'sources': []})
            record['sources'].append({
                'repository': repository['id'], 'name': repository['name'], 'path': relative,
                'commit': repository['commit'], 'license_status': repository['license_status'],
                'url': repository['url'].rstrip('/') + '/blob/' + repository['commit'] + '/' + quote(relative, safe='/'),
                'kind': 'pinned-source',
            })
    for name, text in sorted(current.items()):
        digest = _sha(text.encode('utf-8'))
        record = by_hash.setdefault(digest, {'sha256': digest, 'text': text, 'sources': []})
        record['sources'].append({'repository': 'current-editorial', 'name': 'Current publication documentation',
                                  'path': name, 'kind': 'editorial-document'})
    documents = list(by_hash.values())
    for document in documents:
        document['sources'].sort(key=lambda item: (item['name'].casefold(), item['path']))
        document['title'] = document['sources'][0]['path'] + ' — ' + document['sources'][0]['name']
    documents.sort(key=lambda item: (item['title'].casefold(), item['sha256']))
    return {'format': 'rasniki-offline-reader', 'version': 1, 'title': lock['title'],
            'subtitle': lock.get('subtitle', 'Lair of Lairs — Recursive Form, Format and Formate'),
            'edition': lock['edition'], 'documents': documents,
            'chambers': list(CHAMBERS), 'lair': _lair(lock, current, set(by_hash)),
            'scope': 'Markdown is displayed as text. The ZIP preserves every pinned source byte, including binary files and licences.'}


def _html(reader: dict) -> bytes:
    embedded = json.dumps(reader, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    embedded = embedded.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rasniki Hopput publication</title><style>
:root{color-scheme:light dark;font-family:system-ui,sans-serif}body{margin:0 auto;max-width:100rem;padding:1.25rem}h1{font-size:clamp(1.4rem,3vw,2.1rem);overflow-wrap:anywhere}h2{overflow-wrap:anywhere}a{color:LinkText}label{display:block;margin-bottom:.4rem}input{box-sizing:border-box;width:100%;padding:.7rem;font:inherit}main{display:grid;grid-template-columns:minmax(14rem,28%) minmax(0,1fr);gap:1.5rem}aside,article{min-width:0}nav{max-height:42vh;overflow:auto}button{display:block;text-align:left;width:100%;font:inherit;overflow-wrap:anywhere;padding:.6rem;margin:.3rem 0}button[aria-current=true]{font-weight:bold}pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.6}#provenance{font-size:.85rem;overflow-wrap:anywhere}#provenance p{margin:.4rem 0}#chambers{display:grid;grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));gap:.5rem;margin:1rem 0;max-height:none}#chambers button{border:1px solid currentColor;border-top:4px solid var(--accent);border-radius:.3rem}#chambers button:nth-child(1){--accent:#ab5964}#chambers button:nth-child(2){--accent:#b47940}#chambers button:nth-child(3){--accent:#a79446}#chambers button:nth-child(4){--accent:#578967}#chambers button:nth-child(5){--accent:#598ca2}#chambers button:nth-child(6){--accent:#697aaa}#chambers button:nth-child(7){--accent:#9270a4}#lair{max-height:45vh;overflow:auto}#lair details{margin:.3rem 0 .3rem .8rem}#lair summary{cursor:pointer;overflow-wrap:anywhere}#lair button{font-size:.85rem;padding:.3rem}#returns{display:flex;flex-wrap:wrap;gap:.5rem}#returns button{width:auto}#breadcrumb{font-size:.85rem;overflow-wrap:anywhere}#nested-links{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.3rem}@media(max-width:700px){main{grid-template-columns:minmax(0,1fr)}nav{max-height:30vh}body{padding:.8rem}} </style></head>
<body><header><h1 id="title"></h1><h2 id="subtitle"></h2><p>Offline reading edition. Edition labels identify the collection; observed checks establish its finite verification claims.</p><p>The ministry's fictional Kerot vocabulary is distinct from the executable K0 instruction set. Native OS boot and real finance remain simulations.</p><p><a href="SCIENCERAINBOWRAINBOWSCIENCE.md">Exact Sciencerainbowrainbowscience</a> · <a href="SCIENCERAINBOWRAINBOWSCIENCE-PAPERWORK.html">Printable paperwork</a> · <a href="SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json">Computerwork</a> · <a href="PUBLICATION.md">Full prose collection</a> · <a href="EXTRA-COMPLETE.md">Extra complete edition</a> · <a href="MAX-RAWFUL.md">Max Rawful</a> · <a href="MAX-RAW.md">Max Raw</a> · <a href="MAX-LAW.md">Max Law</a> · <a href="MAX-LAWFUL.md">Max Lawful</a> · <a href="catalogue.json">Sorted catalogue</a> · <a href="sources.zip">Exact source archive</a> · <a href="release-hashes.json">Release hashes</a></p><p>Seven chambers offer a reading guide through the finite collection.</p><nav id="chambers" aria-label="Seven reading chambers"></nav></header>
<label for="search">Search document names and full text</label><input id="search" type="search" placeholder="Search this edition"><p id="count" aria-live="polite"></p>
<div id="returns"><button id="return-root" type="button">Return to collection</button><button id="return-parent" type="button">Return to parent lair</button></div><p id="breadcrumb"></p>
<main><aside><h2>Source lairs</h2><div id="lair"></div><h2>Matching prose</h2><nav id="documents" aria-label="Documents"></nav></aside><article><h2 id="document-title"></h2><div id="provenance"></div><div id="nested-links"></div><pre id="text"></pre></article></main>
<script id="reader-data" type="application/json">__READER_DATA__</script><script>
'use strict';
const data=JSON.parse(document.getElementById('reader-data').textContent);
const byId=id=>document.getElementById(id);let selected=null;let activeNode=data.lair.root_id;
const nodes=new Map(data.lair.nodes.map(node=>[node.id,node]));const documentsByHash=new Map(data.documents.map(doc=>[doc.sha256,doc]));
byId('title').textContent=data.title;byId('subtitle').textContent=data.subtitle;document.title=data.title+' — '+data.subtitle;
function position(node){activeNode=node.id;byId('return-parent').disabled=node.parent===null;const names=[];let current=node;let depth=0;while(current&&depth++<=data.lair.max_depth){names.unshift(current.name);current=current.parent===null?null:nodes.get(current.parent)}byId('breadcrumb').textContent=names.join(' / ')}
function show(doc){selected=doc;byId('document-title').textContent=doc.title;byId('text').textContent=doc.text;byId('provenance').replaceChildren();byId('nested-links').replaceChildren();
for(const source of doc.sources){const p=document.createElement('p');p.textContent=source.name+' · '+source.path+' · '+source.kind+(source.commit?' · '+source.commit:'')+(source.license_status?' · '+source.license_status:'');if(source.url){const a=document.createElement('a');a.textContent=' View pinned source';a.href=source.url;a.rel='noopener noreferrer';p.append(a)}byId('provenance').append(p)}
for(const button of byId('documents').children)button.setAttribute('aria-current',String(button.dataset.hash===doc.sha256));const leaf=data.lair.nodes.find(node=>node.document_sha256===doc.sha256);if(leaf)position(leaf)}
function inspect(node){if(!node)return;position(node);const doc=node.document_sha256&&documentsByHash.get(node.document_sha256);if(doc){show(doc);position(node);return}selected=null;byId('document-title').textContent=node.name;byId('provenance').replaceChildren();byId('nested-links').replaceChildren();const metadata={kind:node.kind,path:node.path,repository:node.repository||null,commit:node.commit||null,license_status:node.license_status||null,size:node.size===undefined?null:node.size,sha256:node.sha256||null,archive_path:node.archive_path||null};byId('text').textContent=JSON.stringify(metadata,null,2)+(node.kind==='file'?'\n\nThis source is retained in the archive as data. The reader never executes it.':'\n\nChoose a nested lair or file. This index is finite and bounded.');if(node.url){const p=document.createElement('p');const link=document.createElement('a');link.href=node.url;link.textContent='View pinned source';link.rel='noopener noreferrer';p.append(link);byId('provenance').append(p)}for(const childId of node.children){const child=nodes.get(childId);const button=document.createElement('button');button.type='button';button.textContent=child.name+(child.kind==='file'?' · '+child.size+' bytes':' · '+child.kind);button.addEventListener('click',()=>inspect(child));byId('nested-links').append(button)}}
let rendered=0;function renderNode(id,depth,ancestry){if(depth>data.lair.max_depth||rendered++>=data.lair.max_nodes||ancestry.has(id))return document.createTextNode('Traversal limit reached');const node=nodes.get(id);if(!node)return document.createTextNode('Missing index node');if(node.kind==='file'){const button=document.createElement('button');button.type='button';button.textContent=node.name+' · '+node.size+' bytes';button.addEventListener('click',()=>inspect(node));return button}const details=document.createElement('details');details.open=depth===0;const summary=document.createElement('summary');summary.textContent=node.name;summary.addEventListener('click',()=>inspect(node));details.append(summary);const next=new Set(ancestry);next.add(id);for(const child of node.children)details.append(renderNode(child,depth+1,next));return details}
byId('lair').append(renderNode(data.lair.root_id,0,new Set()));byId('return-root').addEventListener('click',()=>inspect(nodes.get(data.lair.root_id)));byId('return-parent').addEventListener('click',()=>{const node=nodes.get(activeNode);if(node&&node.parent!==null)inspect(nodes.get(node.parent))});
for(const chamber of data.chambers){const button=document.createElement('button');button.type='button';button.textContent=chamber.name;button.title=chamber.guide;button.addEventListener('click',()=>{byId('search').value=chamber.query;filter()});byId('chambers').append(button)}
function filter(){const query=byId('search').value.trim().toLocaleLowerCase();const docs=data.documents.filter(doc=>(doc.title+' '+doc.text+' '+doc.sources.map(s=>s.name+' '+s.path).join(' ')).toLocaleLowerCase().includes(query));byId('documents').replaceChildren();
for(const doc of docs){const button=document.createElement('button');button.type='button';button.textContent=doc.title;button.dataset.hash=doc.sha256;button.setAttribute('aria-current',String(selected&&selected.sha256===doc.sha256));button.addEventListener('click',()=>show(doc));byId('documents').append(button)}byId('count').textContent=docs.length+' of '+data.documents.length+' unique Markdown documents';if(docs.length&&(!selected||!docs.includes(selected)))show(docs[0]);if(!docs.length){selected=null;byId('document-title').textContent='No matching documents';byId('text').textContent='';byId('provenance').replaceChildren();byId('nested-links').replaceChildren()}}
byId('search').addEventListener('input',filter);filter();
</script></body></html>
'''
    return template.replace('__READER_DATA__', embedded).encode('utf-8')


def _archive(lock: dict, captured: dict, lock_bytes: bytes) -> bytes:
    stream = io.BytesIO()
    entries = {'_publication/source-lock.json': lock_bytes}
    for (repo_id, relative), payload in captured.items():
        entries[repo_id + '/' + relative] = payload
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, payload in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, payload)
    return stream.getvalue()


def _output_directory(root: Path, output, lock: dict) -> Path:
    raw = Path(output)
    if not raw.is_absolute():
        raw = root / raw
    for part in (raw, *raw.parents):
        if part.is_symlink():
            raise PublicationError(f'Output directory contains a symlink: {part}')
    path = raw.resolve()
    for repository in lock['repositories']:
        source = _source_path(root, repository['mount_path']).resolve()
        if path == source or path.is_relative_to(source) or source.is_relative_to(path):
            raise PublicationError('Output directory must not overlap a source snapshot')
    if path == root / 'publication':
        raise PublicationError('Use a separate derived-output directory under publication')
    if path.exists() and not path.is_dir():
        raise PublicationError('Output destination is not a directory')
    for name in OUTPUT_NAMES:
        destination = path / name
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            raise PublicationError(f'Unsafe existing output: {destination}')
    return path


def build(root, output_dir='publication/edition') -> dict:
    """Verify first; atomically replace only named deterministic derived files."""
    root = Path(root).resolve()
    lock = load_lock(root)
    verification, captured = _capture(root, lock)
    if not verification['ok']:
        raise PublicationError('Source verification failed: ' + '; '.join(verification['errors']))
    output = _output_directory(root, output_dir, lock)
    local, current, local_hashes = _local_data(root)
    repositories = sorted(lock['repositories'], key=lambda item: (item['name'].casefold(), item['id']))
    components = local.get('components', [])
    terms = local.get('terms', local.get('glossary', []))
    if not isinstance(components, list) or not isinstance(terms, list) or any(not isinstance(i, dict) for i in components + terms):
        raise PublicationError('Catalogue components and terms must be arrays of objects')
    catalogue = {'format': 'rasniki-hopput-catalogue', 'version': 1, 'title': lock['title'],
                 'subtitle': lock.get('subtitle', 'Lair of Lairs — Recursive Form, Format and Formate'),
                 'edition': lock['edition'],
                 'repositories': [{key: repository[key] for key in ('id', 'name', 'requested_url', 'url', 'commit', 'mount_path', 'license_status')} for repository in repositories],
                 'components': sorted(components, key=lambda item: (str(item.get('id', '')).casefold(), json.dumps(item, sort_keys=True))),
                 'terms': sorted(terms, key=lambda item: (str(item.get('term', '')).casefold(), json.dumps(item, sort_keys=True))),
                 'language_boundary': 'Ministry fictional Kerot vocabulary does not extend or redefine the executable K0 ISA.',
                 'scope': 'Edition labels are distinct from finite observed verification and simulated capabilities.'}
    reader = _reader(lock, captured, current)
    lock_bytes = _source_path(root, 'publication/source-lock.json').read_bytes()
    try:
        if json.loads(lock_bytes) != lock:
            raise PublicationError('Source lock changed during the build')
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PublicationError('Source lock changed during the build') from error
    lines = ['# ' + lock['title'], '', '## ' + reader['subtitle'], '', 'Edition ' + lock['edition'] + '.', '',
             f'This reproducible offline edition verifies {verification["files"]} pinned files ({verification["bytes"]} bytes) in {verification["repositories"]} source snapshots.', '',
             'The title preserves the requested edition labels. Exact-science claims are limited to the declared finite checks; sovereignty, franchise, firmware boot and financial authority retain their documented proposal or simulation status.', '',
             'The ministry’s fictional Kerot vocabulary remains distinct from the executable K0 instruction set.', '',
             '## Pinned sources', '']
    for repository in repositories:
        lines += ['- ' + repository['name'] + ': ' + repository['url'] + '; commit `' + repository['commit'] + '`; license status: ' + repository['license_status'] + '.']
    lines += ['', '## Offline artifacts', '',
              '- `index.html`: self-contained searchable reader; Markdown is displayed as inert text.',
              '- `reader-data.json`: deduplicated Markdown text, retained source references, seven reading chambers and a bounded recursively nested file tree.',
              '- `catalogue.json`: sorted sources, terms and components.',
              '- `EXTRA-COMPLETE.md`: extra combined volume with all four reading guides and the complete collected prose.',
              '- `MAX-RAWFUL.md`, `MAX-RAW.md`, `MAX-LAW.md`, `MAX-LAWFUL.md`: four full-collection reading editions with distinct editorial review guides.',
              '- `sources.zip`: exact original files under each repository ID, including licenses and binary bytecode; `_publication/source-lock.json` preserves the registry.',
              '- `release-hashes.json`: SHA-256 and byte sizes for the other outputs, source lock and included current editorial inputs.', '',
              'No network requests or source-program execution are performed by this builder. Verification compares pinned sizes and SHA-256 hashes; it does not certify malware absence, legal authority, universal science or native operating-system readiness.', '',
              'Current editorial documents are separately hash-recorded; they are not silently substituted for pinned source snapshots.', '',
              '## Seven reading chambers', '',
              'These chambers are a reading guide through the finite collection.', '']
    for chamber in CHAMBERS:
        lines += ['- ' + chamber['name'] + ': ' + chamber['guide']]
    lines += ['', 'The source lairs index collection, repository, directory and file with explicit parent links. Current editorial documents have a separate lair. Traversal is bounded to depth 32 and 4,096 nodes; every pinned source file has a leaf, including binary files.', '',
              '## Sorted reading collection', '',
              'The following Markdown sources are deduplicated by their exact SHA-256. All matching source references remain recorded. Original source text follows each editorial provenance entry; exact pinned-source bytes remain in the archive.', '',
              'Relative links inside retained source documents are source-local references. They may not resolve in this concatenated book. Pinned-source headings supply actual revision URLs so the original document and its links can be read in their source context.', '']
    for index, document in enumerate(reader['documents'], start=1):
        lines += [f'### Document {index:03d} — {document["title"]}', '',
                  'SHA-256: `' + document['sha256'] + '`.', '']
        for source in document['sources']:
            location = source.get('url', source['path'])
            lines += ['Source: ' + source['name'] + ' · ' + source['kind'] + ' · ' + location + '.', '']
        lines += [document['text'].rstrip('\n'), '', '---', '']
    outputs = {'catalogue.json': _json_bytes(catalogue), 'reader-data.json': _json_bytes(reader),
               'index.html': _html(reader), 'PUBLICATION.md': '\n'.join(lines).encode('utf-8'),
               'sources.zip': _archive(lock, captured, lock_bytes)}
    perspectives = {
        'MAX-RAWFUL.md': ('Max Rawful', 'Read each retained source together with its provenance and implementation status. Keep the complete record visible, including unresolved vocabulary, fictional terminology and finite verification limits.'),
        'MAX-RAW.md': ('Max Raw', 'Read the unabridged collected Markdown text as recorded. This is a textual reading edition, not camera RAW, executable firmware or an alternative source snapshot. Exact binary and original file bytes remain in sources.zip.'),
        'MAX-LAW.md': ('Max Law', 'Review ownership and licensing, consent and personal-data handling, platform access terms, consumer claims, financial representations and jurisdiction-specific duties for every relevant chapter. No jurisdiction or legal clearance is assumed; obtain qualified advice before making legal claims.'),
        'MAX-LAWFUL.md': ('Max Lawful', 'Use documented permissions, original or licensed assets, reversible consent, authorised access and preserved audit evidence. Keep simulations and proposed features labelled. Record which applicable rules were actually reviewed, by whom and when; decline to claim compliance without that evidence. This label is not certification.'),
    }
    catalogue['parallel_editions'] = [{'file': name, 'title': title, 'coverage': 'Complete collected Markdown corpus', 'certification': False} for name, (title, guide) in perspectives.items()]
    outputs['catalogue.json'] = _json_bytes(catalogue)
    for name, (title, guide) in perspectives.items():
        preface = '# ' + title + ' — full collection\n\nPublication edition ' + lock['edition'] + '.\n\n' + guide + '\n\nAll four editions retain the same complete collected body below. Their review guides differ; they do not introduce new implemented capabilities or remove source limitations. Historical original file bytes and licences remain in sources.zip.\n\n---\n\n'
        outputs[name] = preface.encode('utf-8') + outputs['PUBLICATION.md']
    combined = ['# Extra complete publication — edition ' + lock['edition'], '',
                'This additional volume combines Max Rawful, Max Raw, Max Law and Max Lawful reading guides with the full collected prose. All previously documented implementation, consent, privacy and verification limits remain in force. Legal labels are not compliance certification.', '',
                '## Four reading guides', '']
    for title, guide in perspectives.values():
        combined += ['### ' + title, '', guide, '']
    combined += ['## Complete collected publication', '', 'The complete standard body follows once, preserving every included document and source reference.', '', '---', '']
    outputs['EXTRA-COMPLETE.md'] = '\n'.join(combined).encode('utf-8') + outputs['PUBLICATION.md']
    catalogue['extra_complete_edition'] = {'file': 'EXTRA-COMPLETE.md', 'coverage': 'All four guides and complete collected Markdown corpus', 'certification': False}
    outputs['catalogue.json'] = _json_bytes(catalogue)
    guide = current.get('docs/EXACT-SCIENCERAINBOWRAINBOWSCIENCE.md', '# Exact Sciencerainbowrainbowscience\n\nExact finite checks under declared assumptions.\n')
    outputs['SCIENCERAINBOWRAINBOWSCIENCE.md'] = (guide + '\n\n---\n\n## Complete collected publication\n\n').encode('utf-8') + outputs['PUBLICATION.md']
    # Both direct script execution and module imports use the sibling tool.
    try:
        from tools.rainbow import record
    except ModuleNotFoundError:
        from rainbow import record
    exercise = record()
    outputs['SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json'] = _json_bytes(exercise)
    import html
    colours = ('Red — question and scope', 'Orange — source and provenance', 'Yellow — assumptions and method', 'Green — computerwork and observations', 'Blue — comparison and falsification', 'Indigo — review and correction', 'Violet — publication and reproduction')
    sheets = []
    for title, sample in zip(colours, exercise['samples']):
        fields = ''.join('<tr><th>' + label + '</th><td></td></tr>' for label in ('Question / acceptance criterion', 'Input / units', 'Assumptions / method', 'Expected result', 'Actual result', 'Evidence path / SHA-256', 'Measurement uncertainty / limits', 'Reviewer / date', 'Correction / revision'))
        sheets.append('<section><h2>' + title + '</h2><p>Declared sample: ' + sample['wavelength_nm'] + ' nm; exact vacuum frequency: ' + sample['frequency_hz'] + ' Hz.</p><table>' + fields + '</table></section>')
    paperwork = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sciencerainbowrainbowscience paperwork</title><style>body{font:16px system-ui;max-width:900px;margin:2rem auto;padding:1rem;color:#17243a}table{border-collapse:collapse;width:100%}th,td{border:1px solid #68778d;padding:1rem;text-align:left}th{width:35%}td{height:2rem}section{margin:3rem 0}@media print{section{break-before:page}body{margin:0;padding:0}a{color:inherit}}</style><h1>Exact Sciencerainbowrainbowscience</h1><p>Edition ' + html.escape(lock['edition']) + ' · Seven printable workpapers</p><p>Use the browser Print command to print or save as PDF. These chosen samples organise a finite exercise; colours have no universal sharp spectral boundaries. Frequency assumes vacuum propagation and the defined SI speed of light, 299792458 m/s.</p><p><a href="SCIENCERAINBOWRAINBOWSCIENCE.md">Complete reading edition</a> · <a href="SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json">Exact computerwork</a> · <a href="index.html">Collection reader</a></p>' + ''.join(sheets) + '</html>'
    outputs['SCIENCERAINBOWRAINBOWSCIENCE-PAPERWORK.html'] = paperwork.encode('utf-8')
    catalogue['sciencerainbowrainbowscience_edition'] = {'file': 'SCIENCERAINBOWRAINBOWSCIENCE.md', 'paperwork': 'SCIENCERAINBOWRAINBOWSCIENCE-PAPERWORK.html', 'computerwork': 'SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json', 'coverage': 'Complete collected Markdown corpus and seven finite workpapers', 'certification': False}
    outputs['catalogue.json'] = _json_bytes(catalogue)
    hashes = {name: {'sha256': _sha(payload), 'size': len(payload)} for name, payload in sorted(outputs.items())}
    release = {'format': 'rasniki-hopput-release-hashes', 'version': 1, 'edition': lock['edition'],
               'source_lock': {'sha256': _sha(lock_bytes), 'size': len(lock_bytes)},
               'current_editorial_inputs': local_hashes, 'outputs': hashes,
               'self_hash': 'Excluded to avoid a circular hash; hash this file independently when archiving the release.'}
    outputs['release-hashes.json'] = _json_bytes(release)
    output.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_NAMES:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=output, prefix='.' + name + '.', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(outputs[name])
            os.replace(temporary, output / name)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return {**verification, 'output_dir': str(output), 'documents': len(reader['documents']),
            'lair_nodes': reader['lair']['node_count'], 'lair_source_files': reader['lair']['source_file_count'],
            'outputs': {name: {'sha256': _sha(payload), 'size': len(payload)} for name, payload in sorted(outputs.items())}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'verify'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, default=Path('publication/edition'))
    parser.add_argument('--check', action='store_true', help='Compare existing outputs against a temporary deterministic build')
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            if args.check:
                raise PublicationError('--check applies to build only')
            result = verify_sources(args.root)
        elif args.check:
            root = args.root.resolve()
            lock = load_lock(root)
            output = _output_directory(root, args.output, lock)
            with tempfile.TemporaryDirectory(prefix='rasniki-publication-check-') as temporary:
                result = build(root, temporary)
                errors = []
                for name in OUTPUT_NAMES:
                    expected = output / name
                    if not expected.is_file() or expected.read_bytes() != (Path(temporary) / name).read_bytes():
                        errors.append('Missing or changed derived output: ' + name)
                result.update(ok=not errors, errors=errors, output_dir=str(output))
        else:
            result = build(args.root, args.output)
    except (OSError, PublicationError) as error:
        result = {'ok': False, 'errors': [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
