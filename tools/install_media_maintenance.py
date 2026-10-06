"""Install Linux user services for standardisation and daily checked updates."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def install(downloads):
    if sys.platform!='linux' or not shutil.which('systemctl'):raise ValueError('Linux systemd user services are required; use the documented manual commands elsewhere.')
    # A dedicated path avoids shell expansion in systemd command fields.
    for value in (str(ROOT),str(Path(downloads).resolve()),sys.executable):
        if any(c in value for c in '\n\r"%\\'):raise ValueError('Unsupported characters in service path.')
    subprocess.run(['git','diff','--exit-code'],cwd=ROOT,check=True)
    folder=Path.home()/'.config/systemd/user';folder.mkdir(parents=True,exist_ok=True)
    entries={
      'rasniki-media.service':f'''[Unit]
Description=Rasniki original-preserving media archive watcher
[Service]
ExecStart="{sys.executable}" "{ROOT}/tools/media_standardize.py" "{Path(downloads).resolve()}" --watch
Restart=on-failure
RestartSec=10
[Install]
WantedBy=default.target
''',
      'rasniki-update.service':f'''[Unit]
Description=Test Rasniki candidate and fast-forward clean checkout
[Service]
Type=oneshot
ExecStart="{sys.executable}" "{ROOT}/tools/checked_update.py"
ExecStartPost=systemctl --user try-restart rasniki-media.service
''',
      'rasniki-update.timer':'''[Unit]
Description=Daily checked Rasniki repository update
[Timer]
OnBootSec=10min
OnUnitActiveSec=1d
Persistent=true
[Install]
WantedBy=timers.target
'''}
    for name,text in entries.items():
        target=folder/name
        if target.exists():raise ValueError(f'{target} exists; review existing service rather than overwriting it.')
    for name,text in entries.items():(folder/name).write_text(text)
    subprocess.run(['systemctl','--user','daemon-reload'],check=True)
    subprocess.run(['systemctl','--user','enable','--now','rasniki-media.service','rasniki-update.timer'],check=True)
    return folder
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--downloads',type=Path,required=True);args=parser.parse_args();print(install(args.downloads))
