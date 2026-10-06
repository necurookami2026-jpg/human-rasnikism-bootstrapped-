#!/usr/bin/env python3
"""Verify the fully generated document corpus manifest and archive bytes."""
import hashlib
import inspect
import argparse
import concurrent.futures
import tarfile
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from madrigal_lab.huwster import N,document,decode,digits,number,LABELS,CONTEXTS,PURPOSES,FACETS


def verify(root):
    root=Path(root);manifest=json.loads((root/'manifest.json').read_text());expected=1
    template=hashlib.sha256(inspect.getsource(document).encode()).hexdigest()
    addressing=hashlib.sha256((''.join(inspect.getsource(f) for f in (decode,digits,number))+json.dumps([LABELS,CONTEXTS,PURPOSES,FACETS])).encode()).hexdigest()
    if manifest.get('template_sha256')!=template or manifest.get('addressing_sha256')!=addressing:raise ValueError('Document-generation inputs changed; regenerate the full corpus')
    if manifest.get('documents')!=N or manifest.get('complete') is not True or len(manifest.get('files',[]))!=49:raise ValueError('The complete 49-shard corpus is required')
    for i,row in enumerate(manifest['files']):
        if row['file']!=f'rawful-{i+1:02d}.tar.gz' or row['first']!=expected or row['last']-row['first']+1!=row['documents'] or row['documents']!=7**6:raise ValueError('Corpus range or count mismatch')
        path=root/row['file'];digest=hashlib.sha256()
        with path.open('rb') as stream:
            while chunk:=stream.read(1024*1024):digest.update(chunk)
        if digest.hexdigest()!=row['sha256'] or path.stat().st_size!=row['bytes']:raise ValueError('Archive changed: '+row['file'])
        expected=row['last']+1
    if expected!=N+1:raise ValueError('Incomplete corpus')
    return {'ok':True,'documents':N,'archives':49,'bytes':sum(row['bytes'] for row in manifest['files'])}

def inspect_archive(task):
    root,row=task;count=0
    with tarfile.open(Path(root)/row['file'], 'r|gz') as archive:
        for member in archive:
            index=row['first']+count
            if not member.isfile() or member.name!=f'documents/{index:07d}.md':raise ValueError('Archive document ordering/type mismatch')
            if index in (row['first'],row['last']):
                if archive.extractfile(member).read()!=document(index)['text'].encode():raise ValueError('Archive sample differs from current generated draft')
            count+=1
    if count!=row['documents']:raise ValueError('Individual file count differs from manifest')
    return {'file':row['file'],'individual_files_verified':count}


def deep_verify(root):
    manifest=json.loads((Path(root)/'manifest.json').read_text());rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        for row in pool.map(inspect_archive,[(str(root),r) for r in manifest['files']]):
            rows.append(row);print('Inspected '+row['file']+': '+str(row['individual_files_verified'])+' files',flush=True)
    result={'ok':True,'individual_files_verified':sum(r['individual_files_verified'] for r in rows),'archive_boundaries_match_current_templates':True,'files':rows}
    (Path(root)/'deep-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--deep',action='store_true');args=parser.parse_args()
    try:
        root=Path(__file__).resolve().parents[1]/'publication/rawful-corpus';print(json.dumps(verify(root),indent=2))
        if args.deep:print(json.dumps(deep_verify(root),indent=2))
    except (OSError,ValueError,KeyError) as error:print(str(error),file=sys.stderr);sys.exit(1)
