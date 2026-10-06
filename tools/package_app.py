#!/usr/bin/env python3
"""Build a deterministic Python executable archive with its publication reader."""
import hashlib
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
BOOT='''import atexit, sys, tempfile, zipfile
from pathlib import Path
archive=Path(sys.argv[0]).resolve()
workspace=tempfile.TemporaryDirectory(prefix="huwster-app-")
atexit.register(workspace.cleanup)
with zipfile.ZipFile(archive) as z: z.extractall(workspace.name)
sys.path.insert(0,workspace.name)
from madrigal_lab.app import main
raise SystemExit(main())
'''

def build():
 target=ROOT/'releases/huwster-rasnikism.pyz';target.parent.mkdir(exist_ok=True)
 paths=[]
 for folder in ('madrigal_lab','docs','examples','publication/edition'):
  paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc',) and p.name!='sources.zip')
 for name in ('LICENSE','README.md','publication/source-lock.json'):
  if (ROOT/name).exists():paths.append(ROOT/name)
 # Original pinned sources retain their licences and runtime resources.
 for folder in ('vendor','ministry'):
  if (ROOT/folder).exists():paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts)
 with target.open('wb') as f:f.write(b'#!/usr/bin/env python3\n')
 with zipfile.ZipFile(target,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in [('__main__.py',BOOT.encode())]+[(str(p.relative_to(ROOT)),p.read_bytes()) for p in sorted(set(paths))]:
   info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
 target.chmod(0o755)
 receipt={'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'python_required':'3.10+','native_executable':False,'corpus_archives':'Companion repository files; not embedded','sources_zip':'Companion publication/edition/sources.zip; not embedded'}
 (target.parent/'huwster-app-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt))
if __name__=='__main__':build()
