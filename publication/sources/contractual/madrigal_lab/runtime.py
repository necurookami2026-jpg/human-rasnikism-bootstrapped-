"""Hosted boot emulation, root-confined storage, records and read-only bots."""
import hashlib
import ipaddress
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from . import language, defense

LIMIT = 65536
PRIORITIES = {'emergency': 0, 'urgency': 1, 'aurgency': 1, 'normal': 2, 'review': 3}
TRANSITIONS = {'proposed': {'active','closed'}, 'active': {'active','paused','releasing'},
               'paused': {'active','releasing'}, 'releasing': {'closed','paused'}, 'closed': set()}


def text(value, maximum=LIMIT):
    if not isinstance(value, str) or len(value.encode('utf-8')) > maximum:
        raise ValueError('Expected bounded UTF-8 text')
    return value


class Runtime:
    def __init__(self, state_dir, allow_hosts=()):
        self.state = Path(state_dir).resolve()
        self.state.mkdir(parents=True, exist_ok=True)
        self.root = self.state / 'files'
        self.root.mkdir(exist_ok=True)
        if self.root.is_symlink():
            raise ValueError('Document root must not be a symlink')
        self.allow_hosts = frozenset(h.lower() for h in allow_hosts)
        self.records_path = self.state / 'records.json'
        self.records = json.loads(self.records_path.read_text()) if self.records_path.exists() else {'practices': [], 'rules': [], 'domains': {}, 'jobs': [], 'game': {'target': 7, 'attempts': 0, 'solved': False}}
        self.boots = []

    def save(self):
        # Atomic replace means an interrupted write retains the previous whole record.
        temp = self.records_path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.records, indent=2)+'\n')
        os.replace(temp, self.records_path)

    def path(self, relative):
        text(relative, 512)
        if not relative or '\\' in relative or '\x00' in relative:
            raise ValueError('Invalid relative path')
        p = Path(relative)
        if p.is_absolute() or any(part in ('.','..') or part.startswith('.') for part in p.parts):
            raise ValueError('Hidden paths and root escapes are rejected')
        target = self.root.joinpath(p)
        if not target.resolve().is_relative_to(self.root.resolve()):
            raise ValueError('Path leaves document root')
        cursor = self.root
        for part in p.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError('Symlink documents are unsupported')
        return target

    def write(self, relative, content):
        target = self.path(relative)
        text(content)
        if len(list(self.root.rglob('*'))) >= 256 and not target.exists():
            raise ValueError('Document count limit reached')
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(content)
        return {'path': relative, 'bytes': len(content.encode()), 'sha256': hashlib.sha256(content.encode()).hexdigest()}

    def read(self, relative):
        target = self.path(relative)
        descriptor = os.open(target, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, 'rb') as stream:
            import stat
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError('Only regular documents are supported')
            data = stream.read(LIMIT+1)
        if len(data) > LIMIT:
            raise ValueError('Document exceeds 64 KiB')
        return {'path': relative, 'text': data.decode('utf-8'), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

    def files(self):
        result = []
        for directory, dirs, names in os.walk(self.root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.') and not Path(directory,d).is_symlink())
            for name in sorted(names):
                p = Path(directory,name)
                if not name.startswith('.') and not p.is_symlink() and p.is_file():
                    result.append({'path': p.relative_to(self.root).as_posix(), 'bytes': p.stat().st_size})
                    if len(result) >= 256:
                        return result
        return result

    def boot(self, source, mode='uefi', budget=10000):
        if mode not in ('uefi','mbr','rom'):
            raise ValueError('Select uefi, mbr or rom simulation')
        image = language.assemble(source)
        digest = hashlib.sha256(image).hexdigest()
        sector = bytearray(512)
        sector[0:len(b'RASNIKI-SIM')]=b'RASNIKI-SIM'
        sector[510:512]=b'\x55\xaa'
        trace = [f'{mode.upper()} simulated entry', 'validate pseudo-ROM length and digest', 'allocate fresh K0 memory', 'hand off to bounded interpreter']
        result = language.run(source, budget=budget)
        result.update({'mode': mode, 'simulated': True, 'trace': trace,
                       'rom_sha256': digest, 'rom_bytes': len(image),
                       'mbr_signature': sector[510:].hex() if mode == 'mbr' else None,
                       'native_bootable': False, 'host': 'Python 3'})
        self.boots.append({'mode': mode, 'status': result['status'], 'sha256': digest})
        self.boots = self.boots[-32:]
        return result

    def practice(self, purpose, priority='normal'):
        text(purpose, 1000)
        if not purpose.strip() or priority not in PRIORITIES:
            raise ValueError('Supply purpose and declared priority')
        if len(self.records['practices']) >= 256:
            raise ValueError('Practice limit reached')
        record = {'id': len(self.records['practices'])+1, 'purpose': purpose, 'priority': priority, 'state': 'proposed',
                  'history': [{'action': 'formation', 'state': 'proposed'}]}
        self.records['practices'].append(record)
        self.save()
        return record

    def transition(self, identifier, state, reason):
        text(reason,1000)
        record = next((p for p in self.records['practices'] if p['id']==identifier),None)
        if record is None or state not in TRANSITIONS[record['state']] or not reason.strip():
            raise ValueError('Invalid practice transition or missing reason')
        if len(record['history']) >= 256:
            raise ValueError('Practice history limit reached')
        record['state']=state
        record['history'].append({'action': 'reformation', 'state': state, 'reason': reason})
        self.save()
        return record

    def queue(self):
        return sorted(self.records['practices'], key=lambda p:(PRIORITIES[p['priority']],p['id']))

    def job(self, source, priority='normal'):
        language.assemble(source)
        if priority not in PRIORITIES or len(self.records['jobs'])>=128:
            raise ValueError('Invalid priority or job queue full')
        record={'id':len(self.records['jobs'])+1, 'source':source, 'priority':priority, 'state':'ready'}
        self.records['jobs'].append(record)
        self.save()
        return record

    def tick(self, budget=10000):
        ready=sorted((j for j in self.records['jobs'] if j['state']=='ready'),key=lambda j:(PRIORITIES[j['priority']],j['id']))
        if not ready:
            return {'state':'idle'}
        record=ready[0]
        record['result']=language.run(record['source'],budget=budget)
        record['state']=record['result']['status']
        self.save()
        return record

    def rule(self, title, content, parent=None):
        text(title,100); text(content,4000)
        if not title.strip() or not content.strip() or len(self.records['rules'])>=256:
            raise ValueError('Invalid rule proposal or limit reached')
        if parent is not None and not any(r['id']==parent and r['status']=='adopted' for r in self.records['rules']):
            raise ValueError('Parent must be an adopted rule')
        record={'id':len(self.records['rules'])+1,'title':title,'content':content,'parent':parent,'status':'proposed'}
        self.records['rules'].append(record);self.save()
        return record

    def adopt_rule(self, identifier, reviewer):
        text(reviewer,100)
        record=next((r for r in self.records['rules'] if r['id']==identifier),None)
        if record is None or record['status']!='proposed' or not reviewer.strip():
            raise ValueError('Choose a proposed rule and name its reviewer')
        record.update(status='adopted',reviewer=reviewer)
        self.save()
        return record

    def domain(self, host, document):
        if not isinstance(host,str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,30}\.lab',host):
            raise ValueError('Use a local name ending in .lab')
        self.read(document)
        if len(self.records['domains'])>=128 and host not in self.records['domains']:
            raise ValueError('Local domain registry full')
        self.records['domains'][host]=document;self.save()
        return {'host':host,'document':document,'public_dns':False}

    def intranet_bot(self, host):
        if host not in self.records['domains']:
            raise ValueError('Unknown .lab host')
        result=self.read(self.records['domains'][host])
        result.update(bot='intranet',host=host,read_only=True,defense=defense.inspect_bytes(result['path'],result['text'].encode('utf-8')))
        return result

    def internet_bot(self,url):
        text(url,2048)
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None,443) or parsed.fragment:
            raise ValueError('Use HTTPS without credentials, fragment or custom port')
        host=parsed.hostname.lower()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError('Literal IP targets are not supported')
        if host not in self.allow_hosts or host in ('localhost',) or host.endswith(('.localhost','.local','.internal')):
            raise ValueError('Host is not explicitly enabled for this read-only bot')
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):
                return None
        opener=urllib.request.build_opener(NoRedirect,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'Rasniki-Lab-ReadOnly/0.1'}),timeout=5) as response:
            data=response.read(LIMIT+1)
            if len(data)>LIMIT:
                raise ValueError('Remote response exceeds 64 KiB')
            return {'bot':'internet','url':url,'status':response.status,'text':data.decode('utf-8',errors='replace'),'bytes':len(data),'read_only':True,'defense':defense.inspect_bytes(Path(parsed.path).name or 'response.txt',data)}

    def game(self,guess=None):
        game=self.records['game']
        if guess is not None:
            if type(guess) is not int or not 0<=guess<=9:
                raise ValueError('Guess an integer 0..9')
            game['attempts']+=1;game['solved']=guess==game['target'];self.save()
        return {'name':'shared target demo','attempts':game['attempts'],'solved':game['solved'],'range':[0,9]}
