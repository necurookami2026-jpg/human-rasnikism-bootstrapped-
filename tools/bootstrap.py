#!/usr/bin/env python3
"""Verify pinned sources, test the collection, and build the combined edition."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    from tools.publication import build, verify_sources
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'publication'/'edition')
    parser.add_argument('--receipts',type=Path,default=ROOT/'.publication-build'/'bootstrap')
    args=parser.parse_args(argv)
    if sys.version_info<(3,10):
        parser.error('Python 3.10 or newer is required')
    if shutil.which('node') is None or shutil.which('sh') is None:
        parser.error('Node.js and a POSIX shell are required for the documented upstream checks')
    report=verify_sources(ROOT)
    if not report['ok']:
        print(json.dumps(report,indent=2),file=sys.stderr)
        return 1
    mounts=[(ROOT/r['mount_path']).resolve() for r in json.loads((ROOT/'publication'/'source-lock.json').read_text())['repositories']]
    output=args.output.resolve();receipts=args.receipts.resolve()
    for path in (output,receipts):
        if any(path.is_relative_to(mount) for mount in mounts) or path==ROOT:
            parser.error('Outputs and receipts must be outside immutable source roots and the checkout root itself')
    receipts.mkdir(parents=True,exist_ok=True)
    run_dir=Path(tempfile.mkdtemp(prefix='run-',dir=receipts))
    receipt={'format':'rasniki-bootstrap-receipt','version':1,
             'started_at':datetime.now(timezone.utc).isoformat(),
             'hosts':{'python':sys.version.split()[0],
                      'node':subprocess.check_output(['node','--version'],text=True).strip()},
             'source_lock_sha256':digest(ROOT/'publication'/'source-lock.json'),
             'source_verification':report,'checks':[],
             'scope':'Named finite source, construction and test checks; not universal scientific or legal certification'}
    def record():
        (run_dir/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    def run(label,command,cwd=ROOT):
        log=run_dir/(label+'.log')
        with log.open('w') as stream:
            try:
                result=subprocess.run(command,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT,
                                      env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=120)
                status=result.returncode
            except subprocess.TimeoutExpired:
                stream.write('\nBootstrap timeout after 120 seconds.\n')
                status=124
        receipt['checks'].append({'name':label,'command':command,'exit_code':status,'log':log.name})
        record()
        print(f'{label}: '+('passed' if status==0 else f'failed ({status})'),flush=True)
        if status:
            raise RuntimeError(f'{label} failed; inspect {log}')
    try:
        run('lab-and-publication-tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
        run('guardian-tests',[sys.executable,'-m','unittest','-v'],ROOT/'vendor'/'guardian')
        run('ministry-smoke',['node','tests/ministry-smoke.cjs'])
        run('instagram-extension-tests',['node','tests/instagram-orange/core.cjs'])
        run('instagram-content-syntax',['node','--check','extensions/instagram-orange/content.js'])
        run('instagram-popup-syntax',['node','--check','extensions/instagram-orange/popup.js'])
        run('instagram-package',[sys.executable,'tools/package_instagram.py'])
        run('maintenance-script-syntax',[sys.executable,'-m','py_compile','tools/media_standardize.py','tools/checked_update.py','tools/install_media_maintenance.py'])
        run('desktop-script-syntax',['node','--check','madrigal_lab/web/app.js'])
        run('workbench-script-syntax',['node','--check','madrigal_lab/web/workbench.js'])
        run('media-script-syntax',['node','--check','madrigal_lab/web/media-studio.js'])
        with tempfile.TemporaryDirectory(prefix='rasniki-bootstrap-') as temporary:
            contractual=Path(temporary)/'contractual'
            shutil.copytree(ROOT/'publication'/'sources'/'contractual',contractual,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            run('contractual-pinned-tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'],contractual)
            target=Path(temporary)/'rasnikism'
            shutil.copytree(ROOT/'vendor'/'rasnikism',target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            run('rasnikism-full-bootstrap',['sh','bootstrap.sh'],target)
        result=build(ROOT,output)
        if not result.get('ok',True):
            raise RuntimeError('Publication build reported failure')
        with tempfile.TemporaryDirectory(prefix='rasniki-rebuild-') as temporary:
            second=Path(temporary)/'edition'
            build(ROOT,second)
            originals={p.name:digest(p) for p in output.iterdir() if p.is_file()}
            repeated={p.name:digest(p) for p in second.iterdir() if p.is_file()}
            if originals!=repeated:
                raise RuntimeError('Publication outputs are not byte-reproducible')
        receipt['checks'].append({'name':'publication-build-and-repeat','exit_code':0,'outputs':originals})
        final=verify_sources(ROOT)
        if not final['ok']:
            raise RuntimeError('A pinned source changed during bootstrap')
        receipt['completed_at']=datetime.now(timezone.utc).isoformat()
        receipt['checks_passed']=True
        record()
        print('Combined publication built; all named checks passed.',flush=True)
        print(f'Receipt: {run_dir/"receipt.json"}',flush=True)
        return 0
    except (RuntimeError,OSError,ValueError) as error:
        receipt['completed_at']=datetime.now(timezone.utc).isoformat()
        receipt['checks_passed']=False
        receipt['failure']=str(error)
        record()
        print(str(error),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main())
