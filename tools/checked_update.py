"""Fetch the configured repository, test an isolated candidate, then fast-forward."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def run(args,cwd=None,**kwargs):return subprocess.run(args,cwd=cwd or ROOT,check=True,**kwargs)
def update(check_only=False):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():raise ValueError('Working tree must be clean; user changes are never overwritten.')
    old=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    run(['git','fetch','origin','main'])
    candidate=subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=ROOT,text=True).strip()
    run(['git','merge-base','--is-ancestor',old,candidate])
    if old==candidate:return {'status':'current','commit':old}
    with tempfile.TemporaryDirectory(prefix='rasniki-update-') as temp:
        target=Path(temp)/'candidate'
        run(['git','clone','--no-hardlinks','--no-checkout',str(ROOT),str(target)],stdout=subprocess.DEVNULL)
        run(['git','checkout','--detach',candidate],cwd=target,stdout=subprocess.DEVNULL)
        run(['sh','bootstrap.sh'],cwd=target,timeout=600)
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=old or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():raise ValueError('Checkout changed while candidate was tested; update refused.')
    if not check_only:run(['git','merge','--ff-only',candidate])
    return {'status':'tested' if check_only else 'updated','commit':candidate,'restart_required':not check_only}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    print(update(args.check_only))
