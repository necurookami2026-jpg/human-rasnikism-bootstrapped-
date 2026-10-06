"""Loopback desktop/API with bounded requests and a per-session write token."""
import argparse
import hmac
import json
import secrets
import threading
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from . import language, defense, hierarchy
from .catalogue import catalogue
from .finance import Ledger
from .runtime import Runtime

ROOT=Path(__file__).resolve().parents[1]


class Lab:
    def __init__(self,state_dir,allow_hosts=()):
        self.runtime=Runtime(state_dir,allow_hosts)
        self.ledger=Ledger(self.runtime.state/'demo-ledger.sqlite3')
        self.lock=threading.RLock()
        self.token=secrets.token_urlsafe(32)

    def status(self):
        return {'name':'Rasniki Madrigal Lab','version':'0.1.0','native_os':False,
                'files':self.runtime.files(),'practices':self.runtime.queue(),
                'rules':self.runtime.records['rules'],'domains':self.runtime.records['domains'],
                'jobs':[{k:v for k,v in j.items() if k!='source'} for j in self.runtime.records['jobs']],
                'finance':self.ledger.summary(),'game':self.runtime.game(),
                'internet_hosts':sorted(self.runtime.allow_hosts)}

    def action(self,action,args):
        if not isinstance(args,dict):
            raise ValueError('Action arguments must be an object')
        r=self.runtime
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
        # Upstream pages contain inline scripts; only the lab desktop uses this restrictive policy.
        if not self.path.startswith('/collection/'):
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.allowed_host():return self.send(403,{'error':'Loopback Host header required'})
        path=urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        try:
            if path=='/api/session':return self.send(200,{'token':self.server.lab.token})
            if path=='/api/catalogue':return self.send(200,catalogue())
            if path=='/api/status':
                with self.server.lab.lock:return self.send(200,self.server.lab.status())
            if path=='/api/health':return self.send(200,{'status':'ok','local_only':True})
            if path.startswith('/collection/'):
                base=ROOT/'vendor'/'rasnikism';relative=path.removeprefix('/collection/')
            elif path.startswith('/docs/'):
                base=ROOT/'docs';relative=path.removeprefix('/docs/')
            else:
                base=ROOT/'madrigal_lab'/'web';relative='index.html' if path=='/' else path.lstrip('/')
            target=(base/relative).resolve()
            if not target.is_relative_to(base.resolve()) or any(p.startswith('.') for p in Path(relative).parts):
                raise ValueError('Invalid document path')
            types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.md':'text/plain','.json':'application/json','.svg':'image/svg+xml','.io':'text/plain','.kerot':'text/plain','.k0':'application/octet-stream'}
            if target.suffix not in types or not target.is_file() or target.stat().st_size>8*1024*1024:
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
        except (ValueError,KeyError,TypeError,AttributeError,OSError,urllib.error.URLError) as error:
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
    print(f'Rasniki lab listening on local port {server.server_address[1]}; Ctrl+C stops it.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
