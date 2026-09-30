#!/usr/bin/env python3
"""Optional owner-run usage snapshot helper. AGPL-3.0-only. Python 3.10+, POSIX."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time

class NeedsAttention(Exception): pass
class StopRequested(NeedsAttention): pass
class ReadFailure(Exception): pass
class Unsupported(ReadFailure): pass

def utc():
    return iso(time.time())

def iso(seconds):
    if seconds is None: return None
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds):
        raise Unsupported('Invalid timestamp')
    try: return dt.datetime.fromtimestamp(seconds, dt.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    except (ValueError, OverflowError, OSError): raise Unsupported('Invalid timestamp') from None

def stamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None: raise Unsupported('Timestamp lacks timezone')
    return parsed.timestamp()

def atomic(path, data):
    # State directory is private; never write credentials or raw protocol responses.
    fd, name = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as output: json.dump(data, output, indent=2); output.write('\n')
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def read_json(path):
    try: return json.loads(path.read_text())
    except (FileNotFoundError, ValueError): return {}

def identity(account):
    if not isinstance(account, dict) or account.get('type') != 'chatgpt':
        raise NeedsAttention('Existing ChatGPT sign-in required; helper does not sign in')
    # The documented account surface supplies email, not a stable tenant identifier.
    # This detects email changes, not same-email workspace changes. Never persist email.
    email = account.get('email')
    if not isinstance(email, str) or not email.strip():
        raise NeedsAttention('Account identity unavailable; cannot safely pin this reader')
    return hashlib.sha256(email.strip().casefold().encode()).hexdigest()

def normalize(result, fetched):
    if not isinstance(result, dict): raise Unsupported('Unsupported quota response')
    mapping = result.get('rateLimitsByLimitId')
    if mapping is None:
        legacy = result.get('rateLimits')
        mapping = {legacy.get('limitId') or 'codex': legacy} if isinstance(legacy, dict) else {}
    if not isinstance(mapping, dict): raise Unsupported('Unsupported quota schema')
    buckets = []
    for key, data in mapping.items():
        if not isinstance(key, str) or not isinstance(data, dict): raise Unsupported('Unsupported quota schema')
        for slot in ('primary', 'secondary'):
            window = data.get(slot)
            if window is None: continue
            if not isinstance(window, dict): raise Unsupported('Unsupported window schema')
            minutes, used = window.get('windowDurationMins'), window.get('usedPercent')
            if minutes is not None and (isinstance(minutes, bool) or not isinstance(minutes, int) or minutes <= 0):
                raise Unsupported('Invalid quota duration')
            if used is not None and (isinstance(used, bool) or not isinstance(used, (int, float)) or not math.isfinite(used) or not 0 <= used <= 100):
                raise Unsupported('Invalid quota percentage')
            reset = iso(window.get('resetsAt'))
            # A passed reset is not proof of zero usage; keep last good until a new valid read.
            if reset and stamp(reset) <= stamp(fetched): raise Unsupported('Quota reset has expired; await fresh service data')
            duration = 'weekly' if minutes == 10080 else 'five-hour' if minutes == 300 else (str(minutes) + '-minute' if minutes else 'window')
            bucket_id = key if slot == 'primary' else key + ':secondary'
            if len(bucket_id) > 80: raise Unsupported('Quota identifier too long')
            buckets.append({'id': bucket_id, 'label': ('Codex ' + duration)[:80],
                'scope': 'Codex-exposed subscription allowance; not all ChatGPT usage',
                'window_minutes': minutes, 'used_percent': used, 'reset_at': reset,
                'availability': 'available' if used is not None else 'not_returned'})
    if not buckets or len(buckets) > 8 or len({b['id'] for b in buckets}) != len(buckets):
        raise Unsupported('Missing or unsupported quota windows; never infer unlimited access')
    payload = {'source': 'Owner-run local Codex app-server usage reader', 'fetched_at': fetched,
        'buckets': buckets, 'notes': 'Checked locally while helper runs. Missing fields are unknown. Failed reads retain the last good snapshot.'}
    reset = result.get('rateLimitResetCredits')
    if reset is not None:
        if not isinstance(reset, dict): raise Unsupported('Unsupported reset schema')
        count = reset.get('availableCount')
        if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= 1000:
            raise Unsupported('Invalid reset count')
        rows = reset.get('credits')
        records = [{'title': 'Earned Codex resets', 'count': count, 'expires_at': None,
            'status': 'available', 'scope': 'Service-reported aggregate count; individual details may be incomplete'}]
        if rows is not None:
            if not isinstance(rows, list) or len(rows) > 19: raise Unsupported('Unsupported reset detail count')
            for row in rows:
                if not isinstance(row, dict): raise Unsupported('Invalid reset detail')
                expires = iso(row.get('expiresAt'))
                status = row.get('status') if row.get('status') in ('available','used','expired') else 'unknown'
                if expires and stamp(expires) <= stamp(fetched): status = 'expired'
                records.append({'title': 'Earned Codex reset', 'count': 1, 'expires_at': expires,
                    'status': status, 'scope': 'Individual service-returned reset; not additional to aggregate count'})
        payload.update(resets=records, resets_fetched_at=fetched)
    return payload

class Client:
    def __init__(self, config):
        self.config = config
        self.runtime = tempfile.TemporaryDirectory(prefix='dot-panel-usage-')
        self.proc = None
        self.sel = selectors.DefaultSelector()
        self.buffer, self.seq, self.thread = b'', 0, None
        try:
            self.proc = subprocess.Popen([config.get('codex','codex'), 'app-server', '--listen', 'stdio://',
                '-c', 'sqlite_home=' + json.dumps(self.runtime.name)], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.sel.register(self.proc.stdout, selectors.EVENT_READ)
        except Exception:
            self.close(); raise
    def send(self, value):
        self.proc.stdin.write((json.dumps(value) + '\n').encode()); self.proc.stdin.flush()
    def check_stop(self):
        if self.config.get('_stop_path') and Path(self.config['_stop_path']).exists():
            raise StopRequested('Owner requested stop')
    def request(self, method, params=None):
        self.check_stop()
        self.seq += 1
        wanted = self.seq
        msg = {'id': wanted, 'method': method}
        if params is not None: msg['params'] = params
        self.send(msg)
        end = time.monotonic() + 45
        while time.monotonic() < end:
            self.check_stop()
            while b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                try: response = json.loads(line)
                except ValueError: continue
                if not isinstance(response, dict): raise ReadFailure('Invalid protocol response')
                if 'method' in response and 'id' in response:
                    raise NeedsAttention('Server requested additional interaction; helper will not authorize it')
                if response.get('id') == wanted:
                    if 'error' in response: raise ReadFailure('App-server protocol failure')
                    result = response.get('result', {})
                    if not isinstance(result, dict): raise ReadFailure('Invalid protocol result')
                    return result
            if self.proc.poll() is not None: raise ReadFailure('App-server exited')
            if self.sel.select(1):
                chunk = os.read(self.proc.stdout.fileno(), 65536)
                if not chunk: raise ReadFailure('App-server closed output')
                self.buffer += chunk
                if len(self.buffer) > 4_000_000: raise ReadFailure('Response exceeds bounded buffer')
        raise ReadFailure('App-server response timed out')
    def account_identity(self):
        return identity(self.request('account/read', {'refreshToken': False}).get('account'))
    def connect(self):
        self.request('initialize', {'clientInfo': {'name': 'dot_panel_usage_tracker', 'version': '1.0.0'}})
        self.send({'method': 'initialized', 'params': {}})
        account_hash = self.account_identity()
        if self.config.get('account_hash') and account_hash != self.config['account_hash']:
            raise NeedsAttention('Signed-in account changed; review target and reconfigure')
        context = self.request('thread/start', {'ephemeral': True, 'cwd': self.runtime.name,
            'serviceName': 'dot_panel_usage_tracker'}).get('thread', {})
        if not context.get('ephemeral') or context.get('turns') or not context.get('id'):
            raise NeedsAttention('Unexpected context persistence or model turns')
        self.thread = context['id']
        return account_hash
    def tool(self, name, args=None):
        if name not in ('get_touch_status', 'get_usage_snapshot', 'update_usage_snapshot'):
            raise NeedsAttention('Tool outside approved usage scope')
        result = self.request('mcpServer/tool/call', {'threadId': self.thread,
            'server': self.config['server'], 'tool': self.config['tool_prefix'] + name, 'arguments': args or {}})
        if result.get('isError'): raise ReadFailure('Selected panel tool returned an error')
        data = result.get('structuredContent')
        if isinstance(data, dict): return data
        for item in result.get('content', []):
            if item.get('type') == 'text':
                try:
                    data = json.loads(item['text'])
                    if isinstance(data, dict): return data
                except ValueError: pass
        raise ReadFailure('Selected panel returned no structured result')
    def close(self):
        if self.proc:
            if self.proc.poll() is None: self.proc.terminate()
            try: self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired: self.proc.kill(); self.proc.wait()
            for pipe in (self.proc.stdin, self.proc.stdout):
                if pipe: pipe.close()
        self.sel.close(); self.runtime.cleanup()

def cycle(client, config):
    if client.account_identity() != config['account_hash']:
        raise NeedsAttention('Signed-in account changed; no snapshot written')
    if client.tool('get_touch_status').get('dot_display_name') != config['panel_name']:
        raise NeedsAttention('Selected panel name changed; review target before writing')
    payload = normalize(client.request('account/rateLimits/read'), utc())
    before = client.tool('get_usage_snapshot').get('snapshot')
    if before is not None and not isinstance(before, dict): raise ReadFailure('Invalid prior snapshot')
    expected = before.get('fetched_at') if before else None
    if expected and stamp(expected) >= stamp(payload['fetched_at']): raise ReadFailure('Remote snapshot is newer')
    payload['expected_fetched_at'] = expected
    # Recheck account immediately before the only allowed write.
    if client.account_identity() != config['account_hash']: raise NeedsAttention('Account changed during read')
    if config.get('_stop_path') and Path(config['_stop_path']).exists(): raise StopRequested('Owner requested stop')
    client.tool('update_usage_snapshot', payload)
    after = client.tool('get_usage_snapshot').get('snapshot')
    if not isinstance(after, dict) or not after or stamp(after['fetched_at']) != stamp(payload['fetched_at']) or after['buckets'] != payload['buckets']:
        raise ReadFailure('Snapshot read-back mismatch')
    if 'resets' in payload and (after.get('resets') != payload['resets'] or stamp(after.get('resets_fetched_at','')) != stamp(payload['resets_fetched_at'])):
        raise ReadFailure('Reset read-back mismatch')
    return after

def backoff(failures): return min(600, 60 * 2 ** min(max(0, failures-1), 4))

class Lock:
    def __init__(self, root):
        self.file = (root / 'tracker.lock').open('a+')
        try: fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.file.close(); raise NeedsAttention('Tracker already active for this state directory') from None
    def close(self): self.file.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

def active(root):
    if not (root / 'tracker.lock').exists(): return False
    try:
        with Lock(root): return False
    except NeedsAttention: return True

def status(root):
    state = read_json(root / 'status.json')
    state['process_active'] = active(root)
    last = state.get('last_success_at')
    state['freshness'] = 'missing' if not last else ('fresh' if time.time() - stamp(last) < 3600 else 'stale')
    if not state['process_active'] and state.get('status') in ('running','retrying','starting'): state['status'] = 'stopped'
    return state

def run(root, once=False, factory=Client):
    with Lock(root):
        (root / 'stop').unlink(missing_ok=True)
        config = read_json(root / 'config.json')
        if not all(config.get(k) for k in ('server','tool_prefix','panel_name','account_hash')):
            raise NeedsAttention('Configure a verified owner panel before starting')
        config['_stop_path'] = str(root / 'stop')
        state = read_json(root / 'status.json')
        state.update(status='starting', started_at=utc(), consecutive_failures=0)
        atomic(root / 'status.json', state)
        failures = 0
        while not (root / 'stop').exists():
            client = None
            try:
                client = factory(config); client.connect()
                after = cycle(client, config)
                atomic(root / 'last-good.json', after)
                state.update(status='running', last_success_at=utc(), last_error=None, consecutive_failures=0)
                failures, delay = 0, 60
            except StopRequested:
                state.update(status='stopped', stopped_at=utc(), next_attempt_at=None)
                atomic(root / 'status.json', state); return 0
            except NeedsAttention:
                state.update(status='needs_attention', last_error='Account, target or permission interaction requires owner review')
                atomic(root / 'status.json', state); return 2
            except (ReadFailure, OSError, ValueError, KeyError, TypeError):
                failures += 1; delay = backoff(failures)
                state.update(status='unsupported' if isinstance(sys.exc_info()[1], Unsupported) else 'retrying',
                    last_error='Read or upload unavailable; last good snapshot retained', consecutive_failures=failures)
            finally:
                if client: client.close()
            state['next_attempt_at'] = iso(time.time() + delay)
            atomic(root / 'status.json', state)
            if once: return 0 if state['status'] == 'running' else 1
            until = time.monotonic() + delay
            while not (root / 'stop').exists() and time.monotonic() < until:
                time.sleep(min(1, max(0, until-time.monotonic())))
        state.update(status='stopped', stopped_at=utc(), next_attempt_at=None)
        atomic(root / 'status.json', state)
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, required=True, help='Dedicated private local directory outside source repository')
    parser.add_argument('command', choices=['configure','once','run','start','status','stop','uninstall'])
    parser.add_argument('--server'); parser.add_argument('--tool-prefix'); parser.add_argument('--panel-name')
    parser.add_argument('--codex', default='codex')
    args = parser.parse_args()
    os.umask(0o077)
    root = args.state_dir.expanduser().resolve()
    source_root = Path(__file__).resolve().parent.parent
    if root == source_root or source_root in root.parents:
        parser.error('Use a private state directory outside the source repository')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o077:
        parser.error('State directory must be owned by you and accessible only to you (chmod 700)')
    marker = root / '.dot-panel-usage.json'
    owned = read_json(marker) == {'application': 'dot-panel-usage-tracker', 'version': 1}
    try:
        if args.command != 'configure' and not owned:
            raise NeedsAttention('Not a configured tracker directory')
        if args.command == 'configure':
            if not owned and any(root.iterdir()): raise NeedsAttention('Choose an empty dedicated state directory')
            if not all((args.server, args.tool_prefix, args.panel_name)): parser.error('configure requires explicit server, tool-prefix and panel-name')
            with Lock(root):
                # Claim only a previously empty dedicated directory before capability checks,
                # so a failed first connection can be retried without deleting a live lock.
                atomic(marker, {'application': 'dot-panel-usage-tracker', 'version': 1})
                config = {'server': args.server, 'tool_prefix': args.tool_prefix, 'panel_name': args.panel_name, 'codex': args.codex}
                client = Client(config)
                try:
                    config['account_hash'] = client.connect()
                    if client.tool('get_touch_status').get('dot_display_name') != args.panel_name:
                        raise NeedsAttention('Panel name does not match selected target')
                    client.tool('get_usage_snapshot')
                    previous = read_json(root / 'config.json')
                    if previous and any(previous.get(key) != config.get(key) for key in ('account_hash','server','tool_prefix','panel_name')):
                        # An explicit target change invalidates only local evidence for the old target.
                        (root / 'last-good.json').unlink(missing_ok=True)
                        (root / 'status.json').unlink(missing_ok=True)
                    atomic(root / 'config.json', config)
                    atomic(marker, {'application': 'dot-panel-usage-tracker', 'version': 1})
                finally: client.close()
            print('Verified selected panel and pinned local account identity. No snapshot written.')
        elif args.command == 'status': print(json.dumps(status(root), indent=2))
        elif args.command == 'stop':
            if active(root): (root / 'stop').touch(mode=0o600); print('Stop requested; tracking will stop at the next protocol/lifecycle check; verify status before removing files.')
            else: print('Tracker is not active.')
        elif args.command == 'uninstall':
            with Lock(root):
                for name in ('config.json','status.json','last-good.json','stop','tracker.log'):
                    (root / name).unlink(missing_ok=True)
            print('Local tracker configuration and snapshots removed. Remote snapshot and Codex sign-in preserved.')
        elif args.command == 'start':
            # Child owns the lock; concurrent starts cannot produce two active writers.
            if active(root): raise NeedsAttention('Tracker already active')
            if not read_json(root / 'config.json'): raise NeedsAttention('Configure first')
            with (root / 'tracker.log').open('ab') as log:
                subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--state-dir', str(root), 'run'],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
            print('Background start requested; check status to verify. No autostart installed.')
        else: return run(root, args.command == 'once')
    except (NeedsAttention, ReadFailure, OSError, ValueError):
        print('Tracker unavailable: verify existing sign-in, selected panel tools, private state directory and status.', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__': sys.exit(main())
