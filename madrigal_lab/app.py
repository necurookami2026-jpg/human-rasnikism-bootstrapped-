"""CLI, browser GUI/HUD and publication reader launcher."""
import argparse
import json
import sys
import threading
import webbrowser
from pathlib import Path
from .server import ROOT, Lab, Server

EDITION_FILES={'rawful':'MAX-RAWFUL.md','raw':'MAX-RAW.md','law':'MAX-LAW.md','lawful':'MAX-LAWFUL.md','complete':'PUBLICATION.md'}

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--state',type=Path,default=Path.cwd()/'.huwster-state')
 commands=parser.add_subparsers(dest='command',required=True)
 for name in ('gui','hud','reader','serve'):
  p=commands.add_parser(name);p.add_argument('--port',type=int,default=0)
 p=commands.add_parser('read');p.add_argument('--edition',choices=EDITION_FILES,default='complete')
 commands.add_parser('catalogue')
 p=commands.add_parser('run');p.add_argument('source',type=Path)
 p=commands.add_parser('action');p.add_argument('name');p.add_argument('--json',default='{}',help='JSON arguments; use @file to read UTF-8 JSON')
 args=parser.parse_args(argv)
 try:
  if args.command=='read':
   sys.stdout.write((ROOT/'publication/edition'/EDITION_FILES[args.edition]).read_text());return 0
  if args.command=='catalogue':
   print((ROOT/'publication/edition/catalogue.json').read_text());return 0
  lab=Lab(args.state)
  if args.command in ('run','action'):
   if args.command=='run':result=lab.action('huwster-run',{'source':args.source.read_text()})
   else:
    text=Path(args.json[1:]).read_text() if args.json.startswith('@') else args.json
    result=lab.action(args.name,json.loads(text))
   print(json.dumps(result,indent=2,ensure_ascii=False));return 0
  server=Server(('127.0.0.1',args.port),lab)
  path='/publication/' if args.command=='reader' else '/'
  url=f'http://127.0.0.1:{server.server_address[1]}{path}'
  print('Huwster Rasnikism: '+url+' (Ctrl+C stops the local app)',flush=True)
  if args.command!='serve':threading.Timer(.3,lambda:webbrowser.open(url)).start()
  try:server.serve_forever()
  except KeyboardInterrupt:pass
  finally:server.server_close()
  return 0
 except (OSError,ValueError,KeyError,TypeError) as error:
  print('Unable to complete this request: '+str(error),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
