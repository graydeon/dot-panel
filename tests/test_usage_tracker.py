# SPDX-License-Identifier: AGPL-3.0-only
"""Synthetic stdlib tests; never invoke real Codex, sign-in, or panel services."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'usage-tracker.py'
SPEC = importlib.util.spec_from_file_location('dot_panel_usage_tracker_test', SOURCE)
tracker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tracker)
FETCHED = '2026-09-30T12:00:00.000Z'
OLD = '2026-09-30T11:00:00.000Z'
QUOTA = {'rateLimitsByLimitId': {'fixture': {'primary': {'windowDurationMins': 300, 'usedPercent': 25, 'resetsAt': 4102444800}, 'secondary': {'windowDurationMins': 10080, 'usedPercent': 60, 'resetsAt': 4103049600}}}}
HASH = hashlib.sha256(b'fixture@example.invalid').hexdigest()
CONFIG = {'server': 'fixture-only-server', 'tool_prefix': 'fixture_', 'panel_name': 'Synthetic Panel', 'account_hash': HASH}

class FakeClient:
    def __init__(self, config, *, identities=None, panel='Synthetic Panel', quota=None, before=None, mismatch=False, reset_mismatch=False, error=None):
        self.identities = list(identities or [HASH, HASH])
        self.panel, self.quota = panel, copy.deepcopy(QUOTA if quota is None else quota)
        self.before, self.after = copy.deepcopy(before), None
        self.mismatch, self.reset_mismatch, self.error = mismatch, reset_mismatch, error
        self.calls, self.closed = [], False
    def connect(self): return HASH
    def account_identity(self): return self.identities.pop(0) if len(self.identities)>1 else self.identities[0]
    def request(self, method):
        self.calls.append((method, None))
        if self.error: raise self.error
        if method != 'account/rateLimits/read': raise AssertionError(method)
        return copy.deepcopy(self.quota)
    def tool(self, name, args=None):
        self.calls.append((name, copy.deepcopy(args)))
        if name == 'get_touch_status': return {'dot_display_name': self.panel}
        if name == 'get_usage_snapshot': return {'snapshot': copy.deepcopy(self.after if self.after is not None else self.before)}
        if name == 'update_usage_snapshot':
            self.after = copy.deepcopy(args)
            if self.mismatch: self.after['buckets'][0]['used_percent'] = 99
            if self.reset_mismatch: self.after.pop('resets', None)
            return self.after
        raise AssertionError(name)
    def close(self): self.closed = True

class SchemaTests(unittest.TestCase):
    def test_multi_and_legacy_match(self):
        multi=tracker.normalize(QUOTA,FETCHED)
        legacy=tracker.normalize({'rateLimits':{'limitId':'fixture',**QUOTA['rateLimitsByLimitId']['fixture']}},FETCHED)
        self.assertEqual(multi,legacy)
        self.assertEqual([x['used_percent'] for x in multi['buckets']],[25,60])
        self.assertEqual([x['window_minutes'] for x in multi['buckets']],[300,10080])
    def test_missing_is_unknown_never_unlimited(self):
        quota={'rateLimitsByLimitId':{'fixture':{'primary':{'usedPercent':None}}}}
        bucket=tracker.normalize(quota,FETCHED)['buckets'][0]
        self.assertEqual(bucket['availability'],'not_returned')
        self.assertIsNone(bucket['used_percent']);self.assertIsNone(bucket['window_minutes']);self.assertIsNone(bucket['reset_at'])
        self.assertEqual(len(tracker.normalize(quota,FETCHED)['buckets']),1)
        for missing in [{},{'rateLimits':None},{'rateLimitsByLimitId':{}},{'rateLimitsByLimitId':{'fixture':{'primary':None,'secondary':None}}}]:
            with self.subTest(missing=missing), self.assertRaises(tracker.Unsupported): tracker.normalize(missing,FETCHED)
    def test_invalid_schema_and_fields(self):
        for field,values in [('usedPercent',[True,-1,101,float('nan'),float('inf'),'25']),('windowDurationMins',[True,0,-1,1.5,'300']),('resetsAt',[True,'soon',float('nan'),1e100])]:
            for value in values:
                quota=copy.deepcopy(QUOTA);quota['rateLimitsByLimitId']['fixture']['primary'][field]=value
                with self.subTest(field=field,value=value),self.assertRaises(tracker.Unsupported): tracker.normalize(quota,FETCHED)
        for mapping in [[],{'fixture':[]},{'fixture':{'primary':[]}}, {'x'*81:{'primary':{'usedPercent':1}}}]:
            with self.subTest(mapping=mapping),self.assertRaises(tracker.Unsupported): tracker.normalize({'rateLimitsByLimitId':mapping},FETCHED)
        many={str(i):{'primary':{'usedPercent':1}} for i in range(9)}
        with self.assertRaises(tracker.Unsupported): tracker.normalize({'rateLimitsByLimitId':many},FETCHED)
    def test_nondict_quota_response_fails_safely(self):
        for value in [None,[],[1],1,'bad']:
            with self.subTest(value=value),self.assertRaises(tracker.Unsupported): tracker.normalize(value,FETCHED)
    def test_expired_quota_keeps_unknown_not_zero(self):
        quota=copy.deepcopy(QUOTA);quota['rateLimitsByLimitId']['fixture']['primary']['resetsAt']=0
        with self.assertRaises(tracker.Unsupported): tracker.normalize(quota,FETCHED)
    def test_reset_aggregate_and_details_not_added(self):
        quota=copy.deepcopy(QUOTA);quota['rateLimitResetCredits']={'availableCount':2,'credits':[{'status':'available','expiresAt':4102444800},{'status':'used','expiresAt':0},{'status':'unrecognized'}]}
        rows=tracker.normalize(quota,FETCHED)['resets']
        self.assertEqual(rows[0]['count'],2);self.assertEqual([r['status'] for r in rows[1:]],['available','expired','unknown'])
        self.assertIn('not additional',rows[1]['scope'])
        self.assertNotIn('resets',tracker.normalize(QUOTA,FETCHED))
        for count in [True,-1,1001,1.5,None]:
            quota['rateLimitResetCredits']={'availableCount':count}
            with self.subTest(count=count),self.assertRaises(tracker.Unsupported): tracker.normalize(quota,FETCHED)
    def test_identity_normalized_hash_and_auth_required(self):
        self.assertEqual(tracker.identity({'type':'chatgpt','email':' FIXTURE@EXAMPLE.INVALID '}),HASH)
        for account in [None,{}, {'type':'apiKey'}, {'type':'chatgpt','email':''}]:
            with self.subTest(account=account),self.assertRaises(tracker.NeedsAttention): tracker.identity(account)
        self.assertNotIn('@',HASH)

class CycleTests(unittest.TestCase):
    def cycle(self,client):
        with patch.object(tracker,'utc',return_value=FETCHED): return tracker.cycle(client,CONFIG)
    def test_guarded_write_and_readback(self):
        client=FakeClient(CONFIG,before={'fetched_at':OLD})
        result=self.cycle(client)
        writes=[args for name,args in client.calls if name=='update_usage_snapshot']
        self.assertEqual(len(writes),1);self.assertEqual(writes[0]['expected_fetched_at'],OLD)
        self.assertEqual(result['buckets'],tracker.normalize(QUOTA,FETCHED)['buckets'])
    def test_changed_identity_or_target_never_writes(self):
        for kwargs in [{'identities':['different']},{'identities':[HASH,'different']},{'panel':'Different Panel'}]:
            client=FakeClient(CONFIG,**kwargs)
            with self.subTest(kwargs=kwargs),self.assertRaises(tracker.NeedsAttention): self.cycle(client)
            self.assertFalse(any(name=='update_usage_snapshot' for name,_ in client.calls))
    def test_newer_remote_and_invalid_quota_never_write(self):
        for kwargs in [{'before':{'fetched_at':'2030-01-01T00:00:00Z'}},{'quota':{}}]:
            client=FakeClient(CONFIG,**kwargs)
            with self.subTest(kwargs=kwargs),self.assertRaises(tracker.ReadFailure): self.cycle(client)
            self.assertFalse(any(name=='update_usage_snapshot' for name,_ in client.calls))
    def test_mismatched_readback_is_failure(self):
        with self.assertRaises(tracker.ReadFailure): self.cycle(FakeClient(CONFIG,mismatch=True))
        quota=copy.deepcopy(QUOTA);quota['rateLimitResetCredits']={'availableCount':1}
        with self.assertRaises(tracker.ReadFailure): self.cycle(FakeClient(CONFIG,quota=quota,reset_mismatch=True))
    def test_malformed_snapshot_shapes_fail_safely(self):
        for shape in [[1],1,'bad']:
            client=FakeClient(CONFIG,before=shape)
            with self.subTest(phase='before',shape=shape),self.assertRaises(tracker.ReadFailure): self.cycle(client)
            self.assertFalse(any(name=='update_usage_snapshot' for name,_ in client.calls))
            class InvalidAfter(FakeClient):
                def tool(self,name,args=None):
                    result=super().tool(name,args)
                    return {'snapshot':shape} if name=='get_usage_snapshot' and self.after is not None else result
            with self.subTest(phase='after',shape=shape),self.assertRaises(tracker.ReadFailure): self.cycle(InvalidAfter(CONFIG))
    def test_run_once_and_lastgood_retained_on_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);tracker.atomic(root/'config.json',CONFIG)
            good=FakeClient(CONFIG)
            with patch.object(tracker,'utc',return_value=FETCHED): self.assertEqual(tracker.run(root,once=True,factory=lambda config:good),0)
            self.assertTrue(good.closed);last=(root/'last-good.json').read_bytes()
            self.assertEqual(tracker.status(root)['status'],'stopped')
            for kwargs,code,label in [({'error':tracker.ReadFailure('fixture')},1,'retrying'),({'quota':{}},1,'unsupported'),({'identities':['different']},2,'needs_attention'),({'mismatch':True},1,'retrying')]:
                client=FakeClient(CONFIG,**kwargs)
                with self.subTest(kwargs=kwargs),patch.object(tracker,'utc',return_value=FETCHED): self.assertEqual(tracker.run(root,once=True,factory=lambda config:client),code)
                self.assertTrue(client.closed);self.assertEqual((root/'last-good.json').read_bytes(),last)
                self.assertEqual(tracker.read_json(root/'status.json')['status'],label)
            self.assertFalse(tracker.active(root))
    def test_stop_before_write_and_run_closes_without_replacing_lastgood(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);stop=root/'stop';config={**CONFIG,'_stop_path':str(stop)}
            client=FakeClient(config);stop.touch()
            with patch.object(tracker,'utc',return_value=FETCHED),self.assertRaises(tracker.StopRequested): tracker.cycle(client,config)
            self.assertFalse(any(name=='update_usage_snapshot' for name,_ in client.calls))
            tracker.atomic(root/'config.json',CONFIG);tracker.atomic(root/'last-good.json',{'fixture':'keep'})
            class StopDuringRead(FakeClient):
                def tool(self,name,args=None):
                    result=super().tool(name,args)
                    if name=='get_usage_snapshot' and self.after is None: stop.touch()
                    return result
            client=StopDuringRead(config)
            with patch.object(tracker,'utc',return_value=FETCHED): self.assertEqual(tracker.run(root,once=True,factory=lambda config:client),0)
            self.assertTrue(client.closed);self.assertFalse(any(name=='update_usage_snapshot' for name,_ in client.calls))
            self.assertEqual(tracker.read_json(root/'last-good.json'),{'fixture':'keep'});self.assertEqual(tracker.read_json(root/'status.json')['status'],'stopped')
    def test_backoff_bounded(self): self.assertEqual([tracker.backoff(n) for n in range(1,9)],[60,120,240,480,600,600,600,600])

class ProcessTests(unittest.TestCase):
    def cli(self,root,command):
        return subprocess.run([sys.executable,str(SOURCE),'--state-dir',str(root),command],capture_output=True,text=True,timeout=10)
    def test_lock_status_stop_and_uninstall_only_local_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);tracker.atomic(root/'.dot-panel-usage.json',{'application':'dot-panel-usage-tracker','version':1});tracker.atomic(root/'status.json',{'status':'running','last_success_at':tracker.utc()})
            with tracker.Lock(root):
                self.assertTrue(tracker.active(root));self.assertTrue(tracker.status(root)['process_active'])
                with self.assertRaises(tracker.NeedsAttention): tracker.Lock(root)
                self.assertEqual(self.cli(root,'stop').returncode,0);self.assertTrue((root/'stop').exists())
                self.assertEqual(self.cli(root,'uninstall').returncode,2)
            self.assertFalse(tracker.active(root));self.assertEqual(tracker.status(root)['status'],'stopped')
            for name in ['config.json','last-good.json','tracker.log']: (root/name).write_text('synthetic')
            (root/'unrelated-file').write_text('preserve')
            self.assertEqual(self.cli(root,'uninstall').returncode,0)
            for name in ['config.json','status.json','last-good.json','tracker.log','stop']: self.assertFalse((root/name).exists())
            self.assertEqual((root/'unrelated-file').read_text(),'preserve')
    def test_unmarked_private_directory_uninstall_preserves_everything(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ['config.json','status.json','last-good.json','tracker.log']: (root/name).write_text('unrelated private data')
            before={file.name:file.read_bytes() for file in root.iterdir()}
            self.assertEqual(self.cli(root,'uninstall').returncode,2)
            self.assertEqual({file.name:file.read_bytes() for file in root.iterdir()},before)
            result=subprocess.run([sys.executable,str(SOURCE),'--state-dir',str(root),'configure','--server','fixture','--tool-prefix','fixture_','--panel-name','Synthetic','--codex','/nonexistent-fixture-only'],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2)
            self.assertEqual({file.name:file.read_bytes() for file in root.iterdir()},before)
    def test_private_repository_root_rejected_without_touching_real_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=Path(temp)/'synthetic-repo';(repo/'scripts').mkdir(parents=True,mode=0o700);repo.chmod(0o700)
            script=repo/'scripts'/'usage-tracker.py';script.write_text(SOURCE.read_text())
            sentinel=repo/'config.json';sentinel.write_text('unrelated source')
            result=subprocess.run([sys.executable,str(script),'--state-dir',str(repo),'uninstall'],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2);self.assertIn('outside the source repository',result.stderr)
            self.assertEqual(sentinel.read_text(),'unrelated source');self.assertFalse((repo/'tracker.lock').exists())
    def test_failed_first_configure_can_retry_without_unverified_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'state';root.mkdir(mode=0o700)
            arguments=[sys.executable,str(SOURCE),'--state-dir',str(root),'configure','--server',CONFIG['server'],'--tool-prefix',CONFIG['tool_prefix'],'--panel-name',CONFIG['panel_name']]
            failed=subprocess.run([*arguments,'--codex','/nonexistent-fixture-only'],capture_output=True,text=True,timeout=10)
            self.assertEqual(failed.returncode,2);self.assertFalse((root/'config.json').exists())
            self.assertEqual(tracker.read_json(root/'.dot-panel-usage.json'),{'application':'dot-panel-usage-tracker','version':1})
            protocol=Path(temp)/'protocol';protocol.mkdir();config,log=ProtocolTests().fake(protocol)
            retry=subprocess.run([*arguments,'--codex',config['codex']],capture_output=True,text=True,timeout=10)
            self.assertEqual(retry.returncode,0,retry.stderr)
            stored=tracker.read_json(root/'config.json');self.assertEqual(stored['account_hash'],HASH);self.assertEqual(stored['server'],CONFIG['server'])
            self.assertNotIn('fixture@example.invalid',(root/'config.json').read_text())
            messages=[json.loads(line) for line in log.read_text().splitlines()]
            tools=[msg['params']['tool'] for msg in messages if msg['method']=='mcpServer/tool/call']
            self.assertEqual(tools,['fixture_get_touch_status','fixture_get_usage_snapshot'])
            self.assertFalse((root/'last-good.json').exists(),'Configure does not upload/write snapshots')
            tracker.atomic(root/'last-good.json',{'fixture':'previous verified target snapshot'})
            tracker.atomic(root/'status.json',{'fixture':'previous verified target status'})
            evidence={name:(root/name).read_bytes() for name in ['last-good.json','status.json']}
            same=subprocess.run([*arguments,'--codex',config['codex']],capture_output=True,text=True,timeout=10)
            self.assertEqual(same.returncode,0,same.stderr)
            self.assertEqual({name:(root/name).read_bytes() for name in evidence},evidence,'Same verified configuration preserves local evidence')
            failure=subprocess.run([*arguments,'--codex','/nonexistent-fixture-only'],capture_output=True,text=True,timeout=10)
            self.assertEqual(failure.returncode,2)
            self.assertEqual({name:(root/name).read_bytes() for name in evidence},evidence,'Failed verification preserves last-good evidence')
            changed_arguments=arguments.copy();changed_arguments[changed_arguments.index('--server')+1]='fixture-second-explicit-server'
            changed=subprocess.run([*changed_arguments,'--codex',config['codex']],capture_output=True,text=True,timeout=10)
            self.assertEqual(changed.returncode,0,changed.stderr)
            self.assertEqual(tracker.read_json(root/'config.json')['server'],'fixture-second-explicit-server')
            self.assertFalse((root/'last-good.json').exists());self.assertFalse((root/'status.json').exists())
            messages=[json.loads(line) for line in log.read_text().splitlines()]
            self.assertFalse(any(msg.get('params',{}).get('tool')=='fixture_update_usage_snapshot' for msg in messages),'Target configuration never changes either remote snapshot')

    def test_status_missing_and_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.assertEqual(tracker.status(root)['freshness'],'missing')
            tracker.atomic(root/'status.json',{'last_success_at':'2000-01-01T00:00:00Z'})
            self.assertEqual(tracker.status(root)['freshness'],'stale')

class ProtocolTests(unittest.TestCase):
    def fake(self,root,mode='normal'):
        executable=root/'fake-app-server';log=root/'outgoing.jsonl'
        executable.write_text('#!'+sys.executable+'\n'+f'''import json,sys
log={str(log)!r}
mode={mode!r}
for line in sys.stdin:
 msg=json.loads(line)
 with open(log,'a') as file: file.write(json.dumps(msg)+'\\n')
 method=msg.get('method')
 if 'id' not in msg: continue
 if mode=='blocked': continue
 if mode=='invalidpacket':
  print(json.dumps([]),flush=True);continue
 if mode=='approval' and method=='account/read':
  print(json.dumps({{'id':999,'method':'item/commandExecution/requestApproval','params':{{}}}}),flush=True);continue
 result={{}}
 if method=='account/read': result={{'account':{{'type':'chatgpt','email':'fixture@example.invalid'}}}}
 if method=='thread/start': result={{'thread':{{'id':'fixture-thread','ephemeral':mode!='persistent','turns':[{{'id':'forbidden'}}] if mode=='turns' else []}}}}
 if method=='mcpServer/tool/call': result={{'structuredContent':{{'dot_display_name':'Synthetic Panel'}}}}
 print(json.dumps({{'id':msg['id'],'result':result}}),flush=True)
''')
        executable.chmod(0o700)
        return {**CONFIG,'codex':str(executable)},log
    def test_stdio_refresh_false_ephemeral_no_turns_and_explicit_target(self):
        with tempfile.TemporaryDirectory() as temp:
            config,log=self.fake(Path(temp));client=tracker.Client(config)
            try:
                self.assertEqual(client.connect(),HASH)
                self.assertEqual(client.tool('get_touch_status')['dot_display_name'],'Synthetic Panel')
                before=log.read_text()
                with self.assertRaises(tracker.NeedsAttention): client.tool('delete_everything')
                self.assertEqual(log.read_text(),before)
            finally: client.close()
            messages=[json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(messages[0]['method'],'initialize');self.assertEqual(messages[1]['method'],'initialized')
            account=next(m for m in messages if m['method']=='account/read');self.assertEqual(account['params'],{'refreshToken':False})
            thread=next(m for m in messages if m['method']=='thread/start');self.assertTrue(thread['params']['ephemeral'])
            tool=next(m for m in messages if m['method']=='mcpServer/tool/call')
            self.assertEqual(tool['params']['server'],CONFIG['server']);self.assertEqual(tool['params']['tool'],'fixture_get_touch_status');self.assertEqual(tool['params']['threadId'],'fixture-thread')
            self.assertFalse(any(m['method'].startswith('turn/') for m in messages))
            self.assertFalse(Path(thread['params']['cwd']).exists(),'Ephemeral runtime directory removed')
    def test_stop_interrupts_waiting_protocol_without_approval_or_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);config,log=self.fake(root,'blocked');config['_stop_path']=str(root/'stop');client=tracker.Client(config)
            timer=threading.Timer(0.1,lambda:(root/'stop').touch());timer.start();started=time.monotonic()
            try:
                with self.assertRaises(tracker.StopRequested): client.connect()
                self.assertLess(time.monotonic()-started,3,'Stop checked during protocol wait rather than 45s timeout')
            finally: timer.cancel();timer.join();client.close()
            messages=[json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual([message['method'] for message in messages],['initialize'])
    def test_nondict_protocol_packet_fails_safely(self):
        with tempfile.TemporaryDirectory() as temp:
            config,log=self.fake(Path(temp),'invalidpacket');client=tracker.Client(config)
            try:
                with self.assertRaises(tracker.ReadFailure): client.connect()
            finally: client.close()
    def test_approval_or_persistent_context_stops(self):
        for mode in ['approval','persistent','turns']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as temp:
                config,log=self.fake(Path(temp),mode);client=tracker.Client(config)
                try:
                    with self.assertRaises(tracker.NeedsAttention): client.connect()
                finally: client.close()
                messages=[json.loads(line) for line in log.read_text().splitlines()]
                self.assertFalse(any(m['method']=='mcpServer/tool/call' for m in messages))
                self.assertFalse(any(m.get('id')==999 for m in messages),'No approval response sent')

if __name__=='__main__': unittest.main(verbosity=2)
