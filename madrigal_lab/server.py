"""Loopback desktop/API with bounded requests and a per-session write token."""
import argparse
import base64
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import threading
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from . import language, defense, hierarchy, symbolic, atlas, papers, recovery, media, huwster
from .catalogue import catalogue
from .finance import Ledger
from .runtime import Runtime
from .boards import BoardStore, KINDS
from .economy import Economy

ROOT=Path(__file__).resolve().parents[1]


class Lab:
    def __init__(self,state_dir,allow_hosts=()):
        self.runtime=Runtime(state_dir,allow_hosts)
        self.ledger=Ledger(self.runtime.state/'demo-ledger.sqlite3')
        self.economy=Economy(self.ledger)
        self.boards=BoardStore(self.runtime.state/'boards.sqlite3')
        self.lock=threading.RLock()
        self.token=secrets.token_urlsafe(32)

    def status(self):
        return {'name':'Huwster Rasnikism','version':'0.1.0','native_os':False,
                'files':self.runtime.files(),'practices':self.runtime.queue(),
                'rules':self.runtime.records['rules'],'domains':self.runtime.records['domains'],
                'jobs':[{k:v for k,v in j.items() if k!='source'} for j in self.runtime.records['jobs']],
                'finance':self.ledger.summary(),'game':self.runtime.game(),
                'internet_hosts':sorted(self.runtime.allow_hosts),
                'boards':{'records':len(self.boards.list()),'local_only':True,'authenticated_members':False}}

    def action(self,action,args):
        if not isinstance(args,dict):
            raise ValueError('Action arguments must be an object')
        r=self.runtime
        if action=='huwster-run':return huwster.run(args['source'])
        if action=='huwster-compile':return huwster.compile_script(args['source'])
        if action=='huwster-packet':return {'documents':huwster.packet(args['category'],args.get('context','interactive'),args.get('subject','Unspecified subject'),args.get('revision',1))}
        if action=='huwster-document':return huwster.document(args['index'],args.get('subject','Unspecified subject'))
        if action=='huwster-catalogue':return huwster.catalogue()
        if action=='huwster-ranks':return {'ranks':huwster.ranks()}
        if action=='assemble':
            data=language.assemble(args['source'])
            return {'hex':data.hex(),'bytes':len(data)}
        if action=='disassemble':
            encoded=args['hex']
            if not isinstance(encoded,str) or len(encoded)>131072:
                raise ValueError('Bytecode hex too large')
            return {'source':language.disassemble(bytes.fromhex(encoded))}
        if action=='format':return {'source':language.format_source(args['source'])}
        if action=='compile':return {'source':language.compile_script(args['source'])}
        if action=='run':return language.run(args['source'],args.get('input','').encode('utf-8'),args.get('budget',10000))
        if action=='quilt':return language.quilt(args['mode'],args['values'])
        if action=='boot':return r.boot(args['source'],args.get('mode','uefi'),args.get('budget',10000))
        if action=='write':return r.write(args['path'],args['text'])
        if action=='read':return r.read(args['path'])
        if action=='scan':return defense.scan(r.root)
        if action=='baseline':return defense.baseline(r.root,r.state/'trusted-baseline.json',args.get('trusted',False))
        if action=='check':return defense.check(r.root,r.state/'trusted-baseline.json')
        if action=='account':return self.ledger.account(args['name'])
        if action=='mint':return self.ledger.mint(args['account'],args['amount'])
        if action=='transfer':return self.ledger.transfer(args['from'],args['to'],args['amount'])
        if action=='hierarchy':return hierarchy.sample(args.get('limit',16))
        if action=='symbolic-evaluate':return symbolic.evaluate(args['record'])
        if action=='symbolic-compare':return symbolic.compare(args['record'])
        if action=='atlas-search':return atlas.catalogue(args.get('query',''),args.get('limit',128),args.get('offset',0))
        if action=='atlas-tree':return atlas.tree(args.get('depth',3),args.get('limit',256),args.get('query',''))
        if action=='governance-families':return atlas.families()
        if action=='document-types':return atlas.document_types(args.get('limit',32))
        if action=='workpaper':return papers.render(args['record'])
        if action=='fandom-seed':return papers.fandom(args['seed'],args.get('count',4))
        if action=='map-plot':return papers.map_svg(args['points'])
        if action=='data-seed':return media.raw_seed(args['record'])
        if action=='seed-rendition':return media.seed_rendition(args['record'])
        if action=='series-plan':return media.parse_story(args['record'])
        if action=='recovery-plan':return recovery.plan(args['record'])
        if action=='backup-inspect':return recovery.inspect_backup(args['record'])
        if action=='backup-restore':return recovery.restore(r,args['record'])
        if action=='board-create':return self.boards.create(args['record'])
        if action=='board-list':return self.boards.list(args.get('kind'))
        if action=='board-get':return self.boards.get(args['id'])
        if action=='board-tree':return self.boards.tree(args.get('parent'),args.get('depth',8),args.get('limit',256))
        if action=='board-reply':return self.boards.reply(args['id'],args['body'],args.get('consent',False),args.get('member_alias','anonymous'))
        if action=='board-vote':return self.boards.vote(args['id'],args['option'],args.get('consent',False),args.get('member_alias','anonymous'))
        if action=='board-transition':return self.boards.transition(args['id'],args['state'],args['reason'],args.get('consent',False))
        if action=='board-delete':return self.boards.delete(args['id'],args.get('consent',False))
        if action=='leaderboard':return self.boards.leaderboard()
        if action=='obligation':return self.economy.create_obligation(args['lender'],args['borrower'],args['amount'],args.get('title','Demo obligation'))
        if action=='lend':return self.economy.lend(args['id'])
        if action=='repay':return self.economy.repay(args['id'],args['amount'])
        if action=='coupon':return self.economy.create_coupon(args['title'],args['amount'],args.get('kind','discount'))
        if action=='redeem-coupon':return self.economy.redeem_coupon(args['id'],args['account'])
        if action=='demo-contract':return self.economy.create_contract(args['title'],args['text'],args.get('parent'))
        if action=='review-contract':return self.economy.review_contract(args['id'],args['reviewer'],args.get('consent',False))
        if action=='finalise-contract':return self.economy.finalise_contract(args['id'],args['author'],args.get('consent',False))
        if action=='verify-contract':return self.economy.verify_contract(args['id'])
        if action=='economy-report':return self.economy.report()
        if action=='economy':return self.ledger.economic_report()
        if action=='practice':return r.practice(args['purpose'],args.get('priority','normal'))
        if action=='transition':return r.transition(args['id'],args['state'],args['reason'])
        if action=='job':return r.job(args['source'],args.get('priority','normal'))
        if action=='tick':return r.tick(args.get('budget',10000))
        if action=='rule':return r.rule(args['title'],args['content'],args.get('parent'))
        if action=='adopt-rule':return r.adopt_rule(args['id'],args['reviewer'])
        if action=='domain':return r.domain(args['host'],args['document'])
        if action=='intranet-bot':return r.intranet_bot(args['host'])
        if action=='internet-bot':return r.internet_bot(args['url'])
        if action=='game':return r.game(args.get('guess'))
        raise ValueError('Unknown action')


class Handler(BaseHTTPRequestHandler):
    server_version='RasnikiLab/0.1'

    def log_message(self,*args):pass

    def allowed_host(self):
        host=self.headers.get('Host','')
        port=self.server.server_address[1]
        return host in (f'127.0.0.1:{port}',f'localhost:{port}')

    def send(self,code,data,content_type='application/json; charset=utf-8'):
        body=json.dumps(data,ensure_ascii=False).encode() if not isinstance(data,bytes) else data
        self.send_response(code)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Referrer-Policy','no-referrer')
        if self.path.startswith(('/publication/','/ministry/')) and content_type.startswith('text/html'):
            # Permit only the script bytes in the reviewed or generated page.
            hashes=[]
            for script in re.findall(rb'<script\b[^>]*>([\s\S]*?)</script>',body,re.I):
                hashes.append("'sha256-"+base64.b64encode(hashlib.sha256(script).digest()).decode()+"'")
            policy="default-src 'self'; script-src 'self' "+' '.join(hashes)+"; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
            self.send_header('Content-Security-Policy',policy)
        elif not self.path.startswith('/collection/'):
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; media-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.allowed_host():return self.send(403,{'error':'Loopback Host header required'})
        path=urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        try:
            if path=='/api/session':return self.send(200,{'token':self.server.lab.token})
            if path=='/api/huwster':return self.send(200,huwster.catalogue())
            if path=='/api/catalogue':return self.send(200,catalogue())
            if path=='/api/symbolic':return self.send(200,symbolic.catalogue())
            if path=='/api/atlas':return self.send(200,atlas.catalogue())
            if path=='/api/boards':return self.send(200,{'kinds':list(KINDS),'local_only':True,'record_limit':256,'depth_limit':8,'authenticated_members':False})
            if path=='/api/workpapers':return self.send(200,papers.catalogue())
            if path=='/api/status':
                with self.server.lab.lock:return self.send(200,self.server.lab.status())
            if path=='/api/health':return self.send(200,{'status':'ok','local_only':True})
            if path.startswith('/collection/'):
                base=ROOT/'vendor'/'rasnikism';relative=path.removeprefix('/collection/')
            elif path.startswith('/rawful-corpus/'):
                base=ROOT/'publication'/'rawful-corpus';relative=path.removeprefix('/rawful-corpus/')
            elif path.startswith('/publication/'):
                base=ROOT/'publication'/'edition';relative=path.removeprefix('/publication/') or 'index.html'
            elif path.startswith('/ministry/'):
                base=ROOT/'vendor'/'internetwomanagementministry'/'site';relative=path.removeprefix('/ministry/') or 'index.html'
            elif path.startswith('/docs/'):
                base=ROOT/'docs';relative=path.removeprefix('/docs/')
            else:
                base=ROOT/'madrigal_lab'/'web';relative='index.html' if path=='/' else path.lstrip('/')
            target=(base/relative).resolve()
            if not target.is_relative_to(base.resolve()) or any(p.startswith('.') for p in Path(relative).parts):
                raise ValueError('Invalid document path')
            types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.md':'text/plain','.json':'application/json','.svg':'image/svg+xml','.io':'text/plain','.kerot':'text/plain','.k0':'application/octet-stream'}
            if path.startswith('/publication/'):
                types['.zip']='application/zip'
            if path.startswith('/rawful-corpus/'):
                types['.gz']='application/gzip'
            maximum=96*1024*1024 if path.startswith('/rawful-corpus/') else 32*1024*1024 if path.startswith('/publication/') else 8*1024*1024
            if target.suffix not in types or not target.is_file() or target.stat().st_size>maximum:
                return self.send(404,{'error':'Document not served'})
            return self.send(200,target.read_bytes(),types[target.suffix]+'; charset=utf-8')
        except (OSError,ValueError):return self.send(404,{'error':'Document not available'})

    def do_POST(self):
        if not self.allowed_host():return self.send(403,{'error':'Loopback Host header required'})
        origin=self.headers.get('Origin')
        host=self.headers.get('Host')
        if origin is not None and origin!=f'http://{host}':
            return self.send(403,{'error':'Cross-origin request rejected'})
        if self.headers.get('Sec-Fetch-Site')=='cross-site':
            return self.send(403,{'error':'Cross-site request rejected'})
        if not hmac.compare_digest(self.headers.get('X-Lab-Token',''),self.server.lab.token):
            return self.send(403,{'error':'Session write token required'})
        if self.path!='/api/action' or self.headers.get('Content-Type','').split(';')[0]!='application/json':
            return self.send(415,{'error':'Use JSON at /api/action'})
        try:
            if self.headers.get('Transfer-Encoding'):
                raise ValueError('Chunked requests unsupported')
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=150000:
                raise ValueError('Request body must be 1..150000 bytes')
            self.connection.settimeout(5)
            body=self.rfile.read(length)
            if len(body)!=length:
                raise ValueError('Incomplete request body')
            data=json.loads(body)
            if not isinstance(data,dict) or not isinstance(data.get('action'),str):
                raise ValueError('Provide action and args')
            with self.server.lab.lock:
                result=self.server.lab.action(data['action'],data.get('args',{}))
            return self.send(200,{'result':result})
        except (ValueError,KeyError,TypeError,AttributeError,OSError,urllib.error.URLError,sqlite3.Error,RecursionError) as error:
            return self.send(400,{'error':str(error)[:1000]})


class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,lab):
        if address[0]!='127.0.0.1':raise ValueError('This development server binds only 127.0.0.1')
        self.lab=lab
        super().__init__(address,Handler)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--state',type=Path,default=ROOT/'.lab-state')
    parser.add_argument('--allow-host',action='append',default=[],help='Explicit HTTPS destination for read-only internet bot')
    args=parser.parse_args(argv)
    server=Server(('127.0.0.1',args.port),Lab(args.state,args.allow_host))
    print(f'Huwster Rasnikism listening on local port {server.server_address[1]}; Ctrl+C stops it.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
