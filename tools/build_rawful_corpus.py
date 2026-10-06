#!/usr/bin/env python3
"""Generate every numbered Ostar Rawful document as individual archive members."""
import argparse
import concurrent.futures
import gzip
import hashlib
import inspect
import io
import json
from pathlib import Path
import sys
import tarfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from madrigal_lab.huwster import document,N,decode,digits,number,LABELS,CONTEXTS,PURPOSES,FACETS


def generation_inputs():
    return {'template_sha256':hashlib.sha256(inspect.getsource(document).encode()).hexdigest(),
            'addressing_sha256':hashlib.sha256((''.join(inspect.getsource(f) for f in (decode,digits,number))+json.dumps([LABELS,CONTEXTS,PURPOSES,FACETS])).encode()).hexdigest()}


def build_shard(task):
    shard,out=task;out=Path(out);name=f'rawful-{shard+1:02d}.tar.gz';target=out/name;receipt=out/(name+'.json')
    if target.exists() and receipt.exists():
        saved=json.loads(receipt.read_text())
        if all(saved.get(k)==v for k,v in generation_inputs().items()) and hashlib.sha256(target.read_bytes()).hexdigest()==saved['sha256']:return saved
    start=shard*7**6+1;end=min(N,(shard+1)*7**6);temporary=target.with_suffix('.partial')
    with temporary.open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=1,mtime=0) as compressed:
            with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.USTAR_FORMAT) as archive:
                for index in range(start,end+1):
                    data=document(index)['text'].encode();info=tarfile.TarInfo(f'documents/{index:07d}.md');info.size=len(data);info.mode=0o644;info.mtime=0
                    archive.addfile(info,io.BytesIO(data))
    temporary.replace(target)
    result={**generation_inputs(),'file':name,'first':start,'last':end,'documents':end-start+1,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    receipt.write_text(json.dumps(result,indent=2)+'\n');return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=Path('publication/rawful-corpus'));parser.add_argument('--workers',type=int,default=4);parser.add_argument('--shards',type=int,default=49);args=parser.parse_args()
    if not 1<=args.workers<=8 or not 1<=args.shards<=49:parser.error('workers 1..8; shards 1..49')
    args.output.mkdir(parents=True,exist_ok=True);results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(build_shard,[(i,str(args.output)) for i in range(args.shards)]):
            results.append(result);print(f"Shard {len(results)}/{args.shards}: {result['documents']} documents; {result['bytes']} bytes",flush=True)
    manifest={'template_sha256':hashlib.sha256(inspect.getsource(document).encode()).hexdigest(), 'addressing_sha256':hashlib.sha256((''.join(inspect.getsource(f) for f in (decode,digits,number))+json.dumps([LABELS,CONTEXTS,PURPOSES,FACETS])).encode()).hexdigest(), 'format':'huwster-rawful-full-corpus','version':1,'documents':sum(r['documents'] for r in results),'complete':args.shards==49,'per_shard':7**6,'files':results,'scope':'Individual unreviewed drafting documents; archive packaging does not confer legal authority.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
