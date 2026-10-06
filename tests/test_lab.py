import concurrent.futures
import http.client
import itertools
import json
from pathlib import Path
import struct
import tempfile
import threading
import unittest
from unittest.mock import patch
from madrigal_lab import language, defense, hierarchy
from madrigal_lab.finance import Ledger
from madrigal_lab.runtime import Runtime
from madrigal_lab.server import Lab, Server

HELLO='mark r0, 82\nsignal r0, 0, 1\nsignal r0, 2, 1\n'


class LanguageTests(unittest.TestCase):
    def test_real_fixture_and_roundtrip(self):
        data=language.assemble('start: mark r0, 65\nstep start\n')
        self.assertEqual(data,struct.pack('<BBHHH',1,0,65,0,0)+struct.pack('<BBHHH',5,0,0,0,0))
        self.assertEqual(language.assemble(language.disassemble(data)),data)
        self.assertEqual(language.assemble(language.format_source(HELLO)),language.assemble(HELLO))

    def test_compile_utf8_and_exact(self):
        source=language.compile_script('emit "care 🌿: "\nexact 1 1\nhalt')
        result=language.run(source)
        self.assertEqual((result['status'],result['output']),('halted','care 🌿: 2'))
        for invalid in ('import os','exact 2 1','halt\nemit "x"'):
            with self.assertRaises(ValueError):language.compile_script(invalid)

    def test_distinct_execution_states(self):
        self.assertEqual(language.run('signal r0, 1, 0')['status'],'waiting')
        self.assertEqual(language.run('step 0',budget=3)['status'],'budget-exhausted')
        self.assertEqual(language.run('signal r0, 99, 0')['status'],'fault')
        self.assertEqual(language.run(HELLO)['output'],'R')
        with self.assertRaises(ValueError):language.run(HELLO,budget=True)

    def test_reject_invalid_decode_and_assembly(self):
        for data in (b'x',struct.pack('<BBHHH',1,16,0,0,0),struct.pack('<BBHHH',5,1,0,0,0)):
            with self.assertRaises(ValueError):language.disassemble(data)
        with self.assertRaises(ValueError):language.assemble('evil r0, 2')

    def test_all_quilt_boolean_payloads(self):
        count=0
        for mode in language.MANIFEST['modes']:
            for payload in itertools.product((0,1),repeat=len(mode['payload'])):
                result=language.quilt(mode['name'],list(payload))
                self.assertEqual(result['status'],'halted')
                self.assertTrue(result['output'])
                if mode['name']=='exact-science':self.assertEqual(int(result['output']),sum(payload))
                count+=1
        self.assertEqual(count,30)
        self.assertEqual(language.quilt('counterantonymmakkakah',[1,1])['mode'],'counterantonymmakkkah')
        with self.assertRaises(ValueError):language.quilt('exact-science',[True,1])

    def test_billion_symbolic_sample(self):
        result=hierarchy.sample(8)
        self.assertEqual(result['potential_ops_per_stanza'],1073741824)
        self.assertEqual(len(set(tuple(a) for a in result['addresses'])),8)
        self.assertEqual(result['ops_executed'],0)


class FinanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'demo.sqlite3';self.ledger=Ledger(self.path)
        self.ledger.account('care');self.ledger.account('review')

    def test_conservation_and_persistence(self):
        self.ledger.mint('care',100);self.ledger.transfer('care','review',25)
        report=Ledger(self.path).summary()
        self.assertEqual(report['accounts'],{'care':75,'issuer':-100,'review':25})
        self.assertEqual(report['circulation'],100);self.assertTrue(report['balanced'])
        self.assertEqual(len(self.ledger.transactions()),2)

    def test_failed_transfer_is_atomic(self):
        self.ledger.mint('care',10);before=self.ledger.summary()
        with self.assertRaises(ValueError):self.ledger.transfer('care','review',11)
        self.assertEqual(self.ledger.summary(),before)
        self.assertEqual(len(self.ledger.transactions()),1)
        for amount in (0,-1,1.5,True,10**20):
            with self.assertRaises(ValueError):self.ledger.mint('care',amount)
        with self.assertRaises(ValueError):self.ledger.transfer('issuer','care',1)

    def test_concurrent_double_spend(self):
        self.ledger.mint('care',10)
        def transfer():
            try:self.ledger.transfer('care','review',10);return True
            except ValueError:return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(lambda _:transfer(),range(2)))
        self.assertEqual(sum(outcomes),1)
        self.assertTrue(self.ledger.summary()['balanced'])


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.r=Runtime(self.temp.name)

    def test_document_boundaries(self):
        self.r.write('room/note.txt','care 🌿');self.assertEqual(self.r.read('room/note.txt')['text'],'care 🌿')
        self.assertEqual(len(self.r.files()),1)
        for path in ('../outside','/etc/passwd','.hidden','a/../../b','a\\b'):
            with self.assertRaises(ValueError):self.r.read(path)
        (self.r.root/'linked').symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):self.r.read('linked')
        with self.assertRaises(ValueError):self.r.write('large.txt','x'*65537)
        (self.r.root/'invalid.txt').write_bytes(b'\xff')
        with self.assertRaises(UnicodeError):self.r.read('invalid.txt')

    def test_symlink_document_root_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            state=Path(directory)/'state';state.mkdir()
            (state/'files').symlink_to(self.r.root,target_is_directory=True)
            with self.assertRaises(ValueError):Runtime(state)

    def test_boot_does_not_write_disk(self):
        before=list(Path(self.temp.name).rglob('*'))
        result=self.r.boot(HELLO,'mbr')
        self.assertEqual(result['mbr_signature'],'55aa');self.assertFalse(result['native_bootable'])
        self.assertEqual(result['output'],'R')
        self.assertEqual(list(Path(self.temp.name).rglob('*')),before)

    def test_practice_rules_and_priority_persist(self):
        a=self.r.practice('Normal care');b=self.r.practice('Review urgent need','emergency')
        self.assertEqual(self.r.queue()[0]['id'],b['id'])
        self.r.transition(a['id'],'active','Agreement recorded')
        self.r.transition(a['id'],'releasing','A planned ending')
        self.r.transition(a['id'],'closed','Resources settled')
        with self.assertRaises(ValueError):self.r.transition(a['id'],'active','Reopen')
        rule=self.r.rule('Care','Review before renewal')
        self.r.adopt_rule(rule['id'],'Reviewer')
        child=self.r.rule('Revised care','Review and document changes',rule['id'])
        self.assertEqual(child['parent'],rule['id'])
        restored=Runtime(self.temp.name)
        self.assertEqual(restored.records,self.r.records)

    def test_kernel_jobs(self):
        self.r.job(HELLO,'normal');self.r.job(HELLO,'emergency')
        self.assertEqual(self.r.tick()['id'],2)
        self.assertEqual(self.r.tick()['state'],'halted')
        self.assertEqual(self.r.tick()['state'],'idle')

    def test_local_domain_bot_and_game(self):
        self.r.write('hello.txt','hello')
        self.r.domain('care.lab','hello.txt')
        bot=self.r.intranet_bot('care.lab')
        self.assertEqual(bot['text'],'hello')
        self.assertIn('defense',bot)
        self.assertTrue(self.r.game(7)['solved'])
        for url in ('http://example.org','https://localhost','https://127.0.0.1','https://example.org'):
            with self.assertRaises(ValueError):self.r.internet_bot(url)
        r=Runtime(self.temp.name,['example.org'])
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,size):return b'plain response'
        with patch('urllib.request.OpenerDirector.open',return_value=Response()):
            self.assertEqual(r.internet_bot('https://example.org')['text'],'plain response')

    def test_guardian_scan_and_trusted_comparison(self):
        self.r.write('hello.txt','known good note')
        report=defense.scan(self.r.root)
        self.assertTrue(report['complete']);self.assertEqual(report['file_count'],1)
        baseline=Path(self.temp.name)/'baseline.json'
        with self.assertRaises(ValueError):defense.baseline(self.r.root,baseline)
        defense.baseline(self.r.root,baseline,trusted=True)
        self.r.write('hello.txt','changed note')
        self.assertEqual(defense.check(self.r.root,baseline)['changes']['modified'],['hello.txt'])
        (self.r.root/'test.txt').write_bytes(defense.guardian.EICAR)
        (self.r.root/'outside').symlink_to('/etc/passwd')
        scan=defense.scan(self.r.root)
        self.assertEqual(scan['file_count'],2)
        self.assertTrue(any(f['kind']=='antivirus-test-file' for f in scan['findings']))
        with self.assertRaises(ValueError):defense.baseline(self.r.root,Path(self.temp.name)/'new-baseline',trusted=True)
        payload=defense.inspect_bytes('response.txt',defense.guardian.EICAR)
        self.assertTrue(any(f['kind']=='antivirus-test-file' for f in payload['findings']))


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.server=Server(('127.0.0.1',0),Lab(self.temp.name))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.stop)
        self.port=self.server.server_address[1]

    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)

    def request(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        c.request(method,path,body,headers or {})
        response=c.getresponse();data=response.read();status=response.status;c.close()
        return status,data

    def action(self,action,args):
        return self.request('POST','/api/action',json.dumps({'action':action,'args':args}),{'Content-Type':'application/json','X-Lab-Token':self.server.lab.token})

    def test_functional_http_workflow(self):
        status,body=self.request('GET','/');self.assertEqual(status,200);self.assertIn(b'Huwster Rasnikism',body)
        status,body=self.action('run',{'source':HELLO});self.assertEqual(status,200)
        self.assertEqual(json.loads(body)['result']['output'],'R')
        self.assertEqual(self.action('write',{'path':'note.txt','text':'web note'})[0],200)
        self.assertEqual(json.loads(self.action('read',{'path':'note.txt'})[1])['result']['text'],'web note')
        self.assertEqual(self.action('account',{'name':'web'})[0],200)
        self.assertEqual(self.action('mint',{'account':'web','amount':10})[0],200)
        self.assertEqual(json.loads(self.request('GET','/api/status')[1])['finance']['circulation'],10)
        status,body=self.request('GET','/collection/index.html');self.assertEqual(status,200)

    def test_denials_and_bounded_errors(self):
        body=json.dumps({'action':'write','args':{'path':'evil','text':'x'}})
        self.assertEqual(self.request('POST','/api/action',body,{'Content-Type':'application/json'})[0],403)
        headers={'Content-Type':'application/json','X-Lab-Token':self.server.lab.token,'Origin':'https://evil.example'}
        self.assertEqual(self.request('POST','/api/action',body,headers)[0],403)
        self.assertEqual(self.request('GET','/api/session',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.action('read',{'path':'../outside'})[0],400)
        self.assertEqual(self.action('internet-bot',{'url':'https://example.org'})[0],400)
        for path in ('/.git/config','/collection/../../README.md','/collection/.git/config','/publication/../source-lock.json','/ministry/../../README.md'):
            self.assertNotEqual(self.request('GET',path)[0],200)

    def test_ministry_static_route_and_script_policy(self):
        status,body=self.request('GET','/ministry/')
        self.assertEqual(status,200)
        self.assertIn(b'The Final',body)
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        c.request('GET','/ministry/')
        response=c.getresponse();response.read()
        policy=response.getheader('Content-Security-Policy');c.close()
        self.assertIn("'sha256-",policy)
        self.assertNotIn("script-src 'self' 'unsafe-inline'",policy)

    def test_session_catalogue_and_missing_action(self):
        self.assertEqual(self.request('GET','/api/session')[0],200)
        catalogue=json.loads(self.request('GET','/api/catalogue')[1])
        self.assertTrue(any(g['term']=='counterabolshivik' and g['meaning'] is None for g in catalogue['glossary']))
        self.assertEqual(self.action('unknown',{})[0],400)

    def test_symbolic_comparison_requires_consent_and_retains_no_record(self):
        status, body = self.request('GET','/api/symbolic')
        self.assertEqual(status,200)
        form = json.loads(body)
        self.assertEqual((len(form['archetypes']),len(form['criteria'])),(5,6))
        record = {'archetype':'thaumturgy','title':'Fictional review',
                  'purpose':'Review a voluntary story.','consent':False,'opt_out':False,
                  'support':{c['id']:'Supplied bounded description.' for c in form['criteria']}}
        before = self.server.lab.status()
        self.assertEqual(self.action('symbolic-compare',{'record':record})[0],400)
        record['consent'] = True
        status, body = self.action('symbolic-compare',{'record':record})
        self.assertEqual(status,200)
        result = json.loads(body)['result']
        self.assertEqual(result['record']['archetype'],'thaumaturgy')
        self.assertEqual(result['comparison']['submitted_score'],6)
        self.assertEqual(result['comparison']['documentation_only_score'],4)
        self.assertEqual(result['comparison']['absent_support_score'],0)
        self.assertEqual(self.server.lab.status(),before)
        self.assertEqual(self.action('symbolic-evaluate',{'record':record})[0],200)
        record['opt_out'] = True
        self.assertEqual(self.action('symbolic-compare',{'record':record})[0],400)
        self.assertEqual(self.action('symbolic-evaluate',{'record':record})[0],400)

    def test_local_survey_quest_and_sorted_atlas_http_workflow(self):
        status,body=self.request('GET','/api/atlas');self.assertEqual(status,200)
        self.assertGreater(json.loads(body)['total'],500)
        result=json.loads(self.action('atlas-search',{'query':'womandeanamandean'})[1])['result']
        self.assertTrue(any(item['label']=='womandeanamandean' for item in result['items']))
        record={'kind':'survey','title':'Review time','body':'When shall this fictional group review?',
                'options':['Now','Later'],'consent':False}
        self.assertEqual(self.action('board-create',{'record':record})[0],400)
        record['consent']=True
        identifier=json.loads(self.action('board-create',{'record':record})[1])['result']['id']
        self.assertEqual(self.action('board-vote',{'id':identifier,'option':1,'consent':True})[0],200)
        self.assertEqual(self.action('board-vote',{'id':identifier,'option':2,'consent':True})[0],400)
        survey=json.loads(self.action('board-get',{'id':identifier})[1])['result']['survey']
        self.assertEqual(survey['submissions'],1)
        self.assertFalse(survey['verified_participants'])
        quest={'kind':'quest','title':'Review a draft','body':'Fictional learning task.','points':7,'consent':True}
        identifier=json.loads(self.action('board-create',{'record':quest})[1])['result']['id']
        for state in ('active','done','reviewed'):
            self.assertEqual(self.action('board-transition',{'id':identifier,'state':state,'reason':'Local assertion.','consent':True})[0],200)
        leaderboard=json.loads(self.action('leaderboard',{})[1])['result']
        self.assertEqual(leaderboard['entries'][0]['points'],7)
        self.assertFalse(leaderboard['financial_value'])

    def test_demo_lending_and_finalised_contract_http_workflow(self):
        for name in ('lender','borrower'):self.assertEqual(self.action('account',{'name':name})[0],200)
        self.action('mint',{'account':'lender','amount':100})
        identifier=json.loads(self.action('obligation',{'lender':'lender','borrower':'borrower','amount':25})[1])['result']['id']
        self.assertEqual(self.action('lend',{'id':identifier})[0],200)
        for amount in (10,15):self.assertEqual(self.action('repay',{'id':identifier,'amount':amount})[0],200)
        report=json.loads(self.action('economy-report',{})[1])['result']
        self.assertEqual(report['accounts']['lender'],100)
        self.assertEqual(report['accounts']['borrower'],0)
        self.assertTrue(report['audit']['balanced']);self.assertTrue(report['audit']['obligations_reconciled'])
        identifier=json.loads(self.action('demo-contract',{'title':'Test proposal','text':'A fictional agreement.'})[1])['result']['id']
        self.assertEqual(self.action('review-contract',{'id':identifier,'reviewer':'steward','consent':1})[0],400)
        self.assertEqual(self.action('review-contract',{'id':identifier,'reviewer':'steward','consent':True})[0],200)
        self.assertEqual(self.action('finalise-contract',{'id':identifier,'author':'steward','consent':True})[0],200)
        self.assertTrue(json.loads(self.action('verify-contract',{'id':identifier})[1])['result']['intact'])

    def test_owned_restore_and_malformed_workpaper_inputs_http(self):
        import hashlib
        backup='An owned local backup. 🌿'
        record={'backup':backup,'owner_asserted':True,'target':'restored/note.txt','expected_sha256':'0'*64}
        self.assertEqual(self.action('backup-restore',{'record':record})[0],400)
        self.assertEqual(self.server.lab.runtime.files(),[])
        record['expected_sha256']=hashlib.sha256(backup.encode()).hexdigest()
        status,body=self.action('backup-restore',{'record':record});self.assertEqual(status,200)
        self.assertFalse(json.loads(body)['result']['account_restored'])
        self.assertEqual(self.server.lab.runtime.read(record['target'])['text'],backup)
        self.assertEqual(self.action('backup-restore',{'record':record})[0],400)
        for label,latitude in [('Point',10**400),('Point\x00',0)]:
            self.assertEqual(self.action('map-plot',{'points':[{'label':label,'latitude':latitude,'longitude':0}]})[0],400)
        deep='{"action":"board-create","args":{"record":'+('['*1100)+'0'+(']'*1100)+'}}'
        headers={'Content-Type':'application/json','X-Lab-Token':self.server.lab.token}
        self.assertEqual(self.request('POST','/api/action',deep,headers)[0],400)

if __name__=='__main__':unittest.main()
