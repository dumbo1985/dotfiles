"""Application cycling and persistent, output-aware Hyprland window placement.

Layout observation and planning are separate from compositor actions so startup,
status, and dry runs never move a user's existing windows.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import re
import selectors
import shlex
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid


CONFIG = Path(__file__).resolve().parent.parent
SIGNATURE = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE', 'default')
SESSION = hashlib.sha256(SIGNATURE.encode()).hexdigest()[:12]
RUNTIME = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')) / f'hypr-window-memory-{SESSION}'
STATE = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'dotfiles-hyprland'
LAYOUT_FILE = STATE / 'window-layout.json'
SOCKET = RUNTIME / 'layout.sock'
ADDRESS = re.compile(r'0x[0-9a-fA-F]+\Z')
OUTPUT = re.compile(r'[A-Za-z0-9_.:-]{1,128}\Z')
EXCLUDED_APPS = {'org.gnome.nautiluspreviewer', 'nautilus-previewer', 'sushi',
                 'hypr-music-visualizer', 'hyprland-share-picker', 'xdg-desktop-portal-gtk',
                 'org.freedesktop.impl.portal.desktop.gtk', 'pinentry', 'pinentry-gtk-2',
                 'polkit-gnome-authentication-agent-1', 'polkit-kde-authentication-agent-1'}
ALIASES = {'org.wezfurlong.wezterm': 'wezterm', 'org.neovide.neovide': 'neovide',
           'org.gnome.nautilus': 'nautilus', 'org.gnome.evince': 'evince',
           'google-chrome-stable': 'google-chrome', 'chromium-browser': 'chromium',
           'org.mozilla.firefox': 'firefox', 'org.kde.kitty': 'kitty'}


def app_key(client):
    """Normalize known native/app-ID aliases without merging Chromium PWAs."""
    initial = str(client.get('initialClass') or client.get('class') or '').strip().casefold()
    current = str(client.get('class') or initial).strip().casefold()
    if re.search(r'(?:^|[._-])(?:crx|pwa)[_-]', current) and current != initial:
        initial = current
    return ALIASES.get(initial, initial)


def visible_clients(clients):
    return [client for client in clients if isinstance(client, dict)
            and isinstance(client.get('address'), str) and ADDRESS.fullmatch(client['address'])
            and client.get('mapped', True) and not client.get('hidden', False)
            and app_key(client) and app_key(client) not in EXCLUDED_APPS
            and not client.get('pinned', False)]


def _history(client):
    value = client.get('focusHistoryID', 9999)
    value = value if isinstance(value, (int, float)) and math.isfinite(value) else 9999
    return value < 0, value, client['address']


def plan_cycle(clients, active_address=None, previous=None, *, same_app=False, reverse=False, now=None):
    """Return a focus plan and a frozen MRU ring, without reading/writing state."""
    now = time.monotonic() if now is None else now
    clients = sorted(visible_clients(clients), key=_history)
    by_address = {client['address']: client for client in clients}
    if not clients:
        return {'mode': 'windows' if same_app else 'applications', 'target': None, 'count': 0}, {}
    if active_address not in by_address:
        active_address = clients[0]['address']
    active_app = app_key(by_address[active_address])
    mode = 'windows' if same_app else 'applications'
    if same_app:
        candidates = [client for client in clients if app_key(client) == active_app]
    else:
        candidates, seen = [], set()
        for client in clients:
            key = app_key(client)
            if key not in seen:
                candidates.append(client)
                seen.add(key)
    # The current window is the representative of its application even when
    # another window's MRU position is temporarily stale immediately after focus.
    candidates = [by_address[active_address] if app_key(client) == active_app and not same_app else client
                  for client in candidates]
    previous = previous if isinstance(previous, dict) else {}
    old_ring = previous.get('ring', [])
    reusable = (previous.get('mode') == mode and previous.get('last_focus') == active_address
                and isinstance(previous.get('time'), (int, float))
                and 0 <= now - previous['time'] < 1.2 and isinstance(old_ring, list)
                and (not same_app or previous.get('app') == active_app))
    ring = [address for address in old_ring if isinstance(address, str) and address in by_address] if reusable else []
    candidate_keys = {app_key(client) if not same_app else client['address'] for client in candidates}
    ring_keys = {app_key(by_address[address]) if not same_app else address for address in ring}
    if not ring or candidate_keys != ring_keys or active_address not in ring:
        ring = [client['address'] for client in candidates]
    index = ring.index(active_address)
    target = ring[(index + (-1 if reverse else 1)) % len(ring)]
    selected = by_address[target]
    state = {'mode': mode, 'app': active_app if same_app else '', 'ring': ring,
             'last_focus': target, 'time': now}
    return {'mode': mode, 'target': target, 'application': app_key(selected),
            'title': str(selected.get('title') or ''), 'count': len(ring), 'ring': ring}, state


def query(name):
    result = subprocess.run(['hyprctl', '-j', name], capture_output=True, text=True, timeout=2, check=True)
    return json.loads(result.stdout)


def evaluate(code):
    result = subprocess.run(['hyprctl', 'eval', code], capture_output=True, text=True, timeout=3)
    if result.returncode or result.stdout.strip().lower().startswith('error'):
        raise RuntimeError((result.stdout + result.stderr).strip()[:300] or 'Hyprland dispatch failed')


def _lua(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)) and math.isfinite(value):
        return str(value)
    if isinstance(value, str):
        text = value.replace('\\', '\\\\').replace('"', '\\"')
        text = ''.join(f'\\{ord(char):03d}' if ord(char) < 32 else char for char in text)
        return '"' + text + '"'
    if isinstance(value, dict):
        return '{' + ','.join(f'{key}={_lua(item)}' for key, item in value.items()
                              if re.fullmatch(r'[a-z_]+', key)) + '}'
    raise ValueError('Unsupported compositor argument')


def focus_address(address):
    if not ADDRESS.fullmatch(str(address)):
        raise ValueError('Invalid window address')
    evaluate('hl.dispatch(hl.dsp.focus(' + _lua({'window': 'address:' + address}) + '))')


def read_json(path, default):
    try:
        if path.stat().st_size > 2 * 1024 * 1024:
            return copy.deepcopy(default)
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return copy.deepcopy(default)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def cycle_main():
    parser = argparse.ArgumentParser(description='按最近使用顺序切换应用或同应用窗口')
    parser.add_argument('--same-app', action='store_true')
    parser.add_argument('--reverse', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='只打印切换计划，不改变焦点或轮换状态')
    args = parser.parse_args()
    os.umask(0o077)
    RUNTIME.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (RUNTIME / 'cycle.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        clients, active = query('clients'), query('activewindow')
        plan, state = plan_cycle(clients, active.get('address'), read_json(RUNTIME / 'cycle.json', {}),
                                 same_app=args.same_app, reverse=args.reverse)
        if args.dry_run:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        elif plan['target']:
            focus_address(plan['target'])
            write_json(RUNTIME / 'cycle.json', state)


def monitor_bounds(monitor):
    scale = float(monitor.get('scale', 1))
    scale = scale if math.isfinite(scale) and scale > 0 else 1
    width, height = int(monitor.get('width', 1920)), int(monitor.get('height', 1080))
    if int(monitor.get('transform', 0)) % 2:
        width, height = height, width
    return (int(monitor.get('x', 0)), int(monitor.get('y', 0)),
            max(128, round(width / scale)), max(96, round(height / scale)))


def _workspace(client):
    workspace = client.get('workspace') or {}
    if not isinstance(workspace, dict) or workspace.get('type') == 'special':
        return None
    identifier = workspace.get('id')
    if isinstance(identifier, int) and 0 < identifier < 100000:
        return identifier
    name = workspace.get('name')
    if isinstance(name, str) and name and len(name) < 120 and not any(ord(char) < 32 for char in name):
        return 'name:' + name if not name.startswith('name:') else name
    return None


def placement(client, monitors):
    """Capture floating geometry relative to the physical output's logical origin."""
    monitor = next((item for item in monitors if item.get('id') == client.get('monitor')), None)
    if monitor is None or not OUTPUT.fullmatch(str(monitor.get('name', ''))):
        return None
    workspace = _workspace(client)
    if workspace is None:
        return None
    x, y, _, _ = monitor_bounds(monitor)
    at, size = client.get('at', [x, y]), client.get('size', [800, 600])
    if not (isinstance(at, list) and len(at) >= 2 and isinstance(size, list) and len(size) >= 2):
        return None
    try:
        geometry = {'x': round(float(at[0]) - x), 'y': round(float(at[1]) - y),
                    'width': max(1, round(float(size[0]))), 'height': max(1, round(float(size[1])))}
    except (ValueError, TypeError, OverflowError):
        return None
    return {'app': app_key(client), 'class': str(client.get('class') or '')[:200],
            'initial_class': str(client.get('initialClass') or '')[:200],
            'title': str(client.get('title') or '')[:500],
            'initial_title': str(client.get('initialTitle') or '')[:500],
            'workspace': workspace, 'monitor': monitor['name'],
            'floating': bool(client.get('floating')), 'geometry': geometry}


def restore_plan(client, record, monitors):
    """Plan native tiling placement and clamped geometry for floating windows."""
    address = str(client.get('address', ''))
    if not ADDRESS.fullmatch(address):
        return None
    monitor = next((item for item in monitors if item.get('name') == record.get('monitor')), None)
    if monitor is None or not OUTPUT.fullmatch(str(monitor.get('name', ''))):
        return None
    workspace = record.get('workspace')
    if not ((isinstance(workspace, int) and 0 < workspace < 100000) or
            (isinstance(workspace, str) and workspace.startswith('name:') and len(workspace) < 125
             and not any(ord(char) < 32 for char in workspace))):
        return None
    selector = 'address:' + address
    steps = []
    if _workspace(client) != workspace:
        steps.append({'dispatcher': 'window.move', 'args': {'window': selector, 'workspace': workspace, 'follow': False}})
    if client.get('monitor') != monitor.get('id') or _workspace(client) != workspace:
        steps.append({'dispatcher': 'workspace.move', 'args': {'workspace': workspace, 'monitor': record['monitor']}})
    desired_float = bool(record.get('floating'))
    if bool(client.get('floating')) != desired_float:
        steps.append({'dispatcher': 'window.float', 'args': {'window': selector, 'action': 'set' if desired_float else 'unset'}})
    geometry = None
    if desired_float and isinstance(record.get('geometry'), dict) and not client.get('fullscreen'):
        origin_x, origin_y, width, height = monitor_bounds(monitor)
        saved = record['geometry']
        try:
            window_w = min(max(128, int(saved['width'])), max(128, width - 16))
            window_h = min(max(96, int(saved['height'])), max(96, height - 16))
            window_x = origin_x + min(max(8, int(saved['x'])), max(8, width - window_w - 8))
            window_y = origin_y + min(max(8, int(saved['y'])), max(8, height - window_h - 8))
        except (KeyError, ValueError, TypeError, OverflowError):
            return None
        geometry = {'x': window_x, 'y': window_y, 'width': window_w, 'height': window_h}
        if list(client.get('size', [])) != [window_w, window_h]:
            steps.append({'dispatcher': 'window.resize', 'args': {'window': selector, 'x': window_w, 'y': window_h, 'relative': False}})
        if list(client.get('at', [])) != [window_x, window_y]:
            steps.append({'dispatcher': 'window.move', 'args': {'window': selector, 'x': window_x, 'y': window_y, 'relative': False}})
    return {'address': address, 'application': app_key(client), 'workspace': workspace,
            'monitor': record['monitor'], 'floating': desired_float, 'geometry': geometry, 'steps': steps}


def apply_plan(plan):
    allowed = {'window.move', 'workspace.move', 'window.float', 'window.resize'}
    if not ADDRESS.fullmatch(str(plan.get('address', ''))):
        raise ValueError('Invalid layout window')
    code = []
    for step in plan.get('steps', []):
        dispatcher = step.get('dispatcher')
        if dispatcher not in allowed or not isinstance(step.get('args'), dict):
            raise ValueError('Invalid layout action')
        code.append('hl.dispatch(hl.dsp.' + dispatcher + '(' + _lua(step['args']) + '))')
    if code:
        evaluate('; '.join(code))


class LayoutMemory:
    """Pure state machine: preserve desired outputs through compositor migration."""
    def __init__(self, document=None):
        document = document if isinstance(document, dict) else {}
        self.last_session = document.get('last_session')
        records = document.get('windows', [])
        self.records = {item['id']: copy.deepcopy(item) for item in records[:500]
                        if isinstance(item, dict) and isinstance(item.get('id'), str) and item.get('app')} if isinstance(records, list) else {}
        self.by_address, self.pending, self.inflight, self.suppressed = {}, {}, set(), {}
        self.outputs = None
        self.quiet_until = 0
        self.dirty = False
        self.slot_defaults = {}
        for record in self.records.values():
            key = record.get('app')
            previous = self.slot_defaults.get(key)
            if previous is None or record.get('slot', 0) < previous.get('slot', 0):
                self.slot_defaults[key] = copy.deepcopy(record)

    def document(self):
        records = sorted(self.records.values(), key=lambda record: record.get('seen_at', 0), reverse=True)[:500]
        return {'version': 1, 'last_session': SESSION, 'windows': records}

    def _bind(self, client, monitors):
        address = client['address']
        if address in self.by_address and self.by_address[address] in self.records:
            return self.records[self.by_address[address]], True
        used = set(self.by_address.values())
        same_app = [record for record in self.records.values() if record.get('app') == app_key(client)]
        free = [record for record in same_app if record['id'] not in used]
        title = str(client.get('title') or '')
        exact = [record for record in free if title and record.get('title') == title]
        initial_title = str(client.get('initialTitle') or '')
        initial_exact = [record for record in free if initial_title and record.get('initial_title') == initial_title]
        if len(exact) == 1:
            record, saved = exact[0], True
        elif len(initial_exact) == 1:
            record, saved = initial_exact[0], True
        elif free:
            record, saved = min(free, key=lambda record: record.get('slot', 0)), True
        else:
            current = placement(client, monitors)
            if current is None:
                return None, False
            prototype = self.slot_defaults.get(app_key(client)) or (min(same_app, key=lambda item: item.get('slot', 0)) if same_app else None)
            record = copy.deepcopy(prototype) if prototype else current
            record.update({'id': uuid.uuid4().hex[:16], 'slot': max([item.get('slot', -1) for item in same_app], default=-1) + 1})
            self.records[record['id']] = record
            self.dirty = True
            saved = bool(same_app)
        self.by_address[address] = record['id']
        return record, saved

    def _learn(self, client, record, monitors):
        current = placement(client, monitors)
        if current is None:
            return
        # Keep the last regular geometry while fullscreen/maximized temporarily.
        if client.get('fullscreen') and record.get('geometry'):
            current['geometry'] = record['geometry']
        if not current.get('floating') and not record.get('floating') and record.get('geometry'):
            current['geometry'] = record['geometry']
        if any(record.get(key) != value for key, value in current.items()):
            record.update(current)
            record['seen_at'] = time.time()
            self.dirty = True
            # Only the primary slot defines future per-app defaults. Learning a
            # newly opened secondary slot must not replace that stable template.
            primary = self.slot_defaults.get(record.get('app'))
            if primary is None or record.get('slot', 0) <= primary.get('slot', 0):
                self.slot_defaults[record['app']] = copy.deepcopy(record)

    def observe(self, clients, monitors, *, now=None, baseline=False):
        now = time.monotonic() if now is None else now
        clients = visible_clients(clients)
        current_addresses = {client['address'] for client in clients}
        self.by_address = {key: value for key, value in self.by_address.items() if key in current_addresses}
        self.pending = {key: value for key, value in self.pending.items() if key in current_addresses}
        self.suppressed = {key: value for key, value in self.suppressed.items() if key in current_addresses}
        self.inflight.intersection_update(current_addresses)
        outputs = {monitor.get('name') for monitor in monitors}
        added = outputs - self.outputs if self.outputs is not None else set()
        if self.outputs is not None and outputs != self.outputs:
            self.quiet_until = now + 2.5
        self.outputs = outputs
        plans = []
        for client in clients:
            address = client['address']
            known = address in self.by_address
            record, saved = self._bind(client, monitors)
            if record is None:
                continue
            connected = record.get('monitor') in outputs
            if baseline:
                if known and (address in self.pending or now < max(self.quiet_until, self.suppressed.get(address, 0))):
                    continue
                if connected:
                    self._learn(client, record, monitors)
                continue
            if not known:
                if saved:
                    self.pending[address] = now + .65
                else:
                    self._learn(client, record, monitors)
            if record.get('monitor') in added:
                self.pending[address] = now + .3
            if address in self.pending:
                if connected and now >= self.pending[address] and address not in self.inflight:
                    plan = restore_plan(client, record, monitors)
                    if plan is not None:
                        if plan['steps']:
                            self.inflight.add(address)
                            plans.append(plan)
                        else:
                            self.pending.pop(address, None)
                continue
            if connected and now >= max(self.quiet_until, self.suppressed.get(address, 0)):
                self._learn(client, record, monitors)
        if baseline:
            for record in self.records.values():
                key = record.get('app')
                previous = self.slot_defaults.get(key)
                if previous is None or record.get('slot', 0) <= previous.get('slot', 0):
                    self.slot_defaults[key] = copy.deepcopy(record)
        return plans

    def restore_finished(self, address, success=True, *, now=None):
        now = time.monotonic() if now is None else now
        self.inflight.discard(address)
        if success:
            self.pending.pop(address, None)
            self.suppressed[address] = now + 2
        else:
            self.pending[address] = now + 5

    def explicit_plans(self, clients, monitors):
        plans = []
        for client in visible_clients(clients):
            record, _ = self._bind(client, monitors)
            if record:
                plan = restore_plan(client, record, monitors)
                if plan and plan['steps']:
                    plans.append(plan)
        return plans


def load_memory():
    return LayoutMemory(read_json(LAYOUT_FILE, {'version': 1, 'windows': []}))


def send_layout(action, timeout=5):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout)
        connection.connect(str(SOCKET))
        connection.sendall(json.dumps({'action': action}).encode() + b'\n')
        data = b''
        while b'\n' not in data and len(data) < 128 * 1024:
            part = connection.recv(8192)
            if not part:
                break
            data += part
        response = json.loads(data.partition(b'\n')[0])
        if response.get('error'):
            raise RuntimeError(response['error'])
        return response


def start_layout():
    RUNTIME.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (RUNTIME / 'start.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            return send_layout('status', timeout=.3)
        except (OSError, ValueError, RuntimeError):
            pass
        command = shlex.join(['/usr/bin/python3', '-u', str(CONFIG / 'bin/window-layout'), '--daemon'])
        command += ' >' + shlex.quote(str(STATE / 'window-layout.log')) + ' 2>&1'
        evaluate('hl.exec_cmd(' + _lua(command) + ')')
        for _ in range(50):
            time.sleep(.05)
            try:
                return send_layout('status', timeout=.3)
            except (OSError, ValueError, RuntimeError):
                pass
    raise RuntimeError('窗口布局服务未启动，请查看 window-layout.log')


class LayoutService:
    def __init__(self):
        self.memory = load_memory()
        self.running, self.last_error = True, ''
        self.started = time.monotonic()
        self.clients, self.monitors = query('clients'), query('monitors')
        # First installation and same-login restarts capture the current baseline.
        # At a new login, preserve saved placements and queue an ordinary delayed
        # restore, including apps that were already mapped before this service.
        baseline = not self.memory.records or self.memory.last_session == SESSION
        self.memory.observe(self.clients, self.monitors, baseline=baseline)
        self.memory.dirty = True
        self.flush()
        self.next_poll, self.last_write = time.monotonic() + (.7 if not baseline else 2), time.monotonic()

    def flush(self):
        if self.memory.dirty:
            write_json(LAYOUT_FILE, self.memory.document())
            self.memory.dirty = False

    def status(self):
        return {'running': self.running, 'pid': os.getpid(), 'records': len(self.memory.records),
                'tracked_windows': len(self.memory.by_address),
                'outputs': sorted(self.memory.outputs or []), 'state_file': str(LAYOUT_FILE),
                'uptime_seconds': round(time.monotonic() - self.started), 'last_error': self.last_error}

    def snapshot(self):
        self.clients, self.monitors = query('clients'), query('monitors')

    def apply(self, plans):
        applied = 0
        for plan in plans:
            try:
                apply_plan(plan)
                self.memory.restore_finished(plan['address'])
                applied += 1
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
                self.last_error = str(error)[:250]
                logging.warning('Cannot restore window placement: %s', self.last_error)
                self.memory.restore_finished(plan['address'], False)
        return applied

    def request(self, action):
        if action == 'status':
            return self.status()
        if action == 'stop':
            self.running = False
            return {'stopped': True}
        if action == 'save':
            self.snapshot()
            self.memory.observe(self.clients, self.monitors, baseline=True)
            self.flush()
            return {'saved': True, 'records': len(self.memory.records)}
        if action == 'restore':
            self.snapshot()
            return {'restored': self.apply(self.memory.explicit_plans(self.clients, self.monitors))}
        return {'error': 'Unknown layout service action'}

    def poll(self):
        try:
            self.snapshot()
            self.apply(self.memory.observe(self.clients, self.monitors))
            if time.monotonic() - self.last_write > 2:
                self.flush()
                self.last_write = time.monotonic()
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            self.last_error = str(error)[:250]
            logging.warning('Cannot inspect current window layout: %s', self.last_error)


def layout_daemon():
    os.umask(0o077)
    RUNTIME.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = (RUNTIME / 'daemon.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    logging.basicConfig(filename=str(STATE / 'window-layout.log'), level=logging.WARNING,
                        format='%(asctime)s %(levelname)s %(message)s')
    service = LayoutService()
    signal.signal(signal.SIGTERM, lambda *_: setattr(service, 'running', False))
    signal.signal(signal.SIGINT, lambda *_: setattr(service, 'running', False))
    selector = selectors.DefaultSelector()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    SOCKET.unlink(missing_ok=True)
    server.bind(str(SOCKET))
    os.chmod(SOCKET, 0o600)
    server.listen(4)
    server.setblocking(False)
    selector.register(server, selectors.EVENT_READ, 'control')
    events, event_data, reconnect_at = None, b'', 0
    event_path = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')) / 'hypr' / SIGNATURE / '.socket2.sock'
    relevant = {'openwindow', 'closewindow', 'movewindowv2', 'changefloatingmode',
                'windowtitlev2', 'monitoradded', 'monitoraddedv2', 'monitorremoved',
                'moveworkspace', 'moveworkspacev2', 'fullscreen', 'configreloaded'}
    try:
        while service.running:
            now = time.monotonic()
            if events is None and now >= reconnect_at:
                try:
                    events = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    events.settimeout(.2)
                    events.connect(str(event_path))
                    events.setblocking(False)
                    selector.register(events, selectors.EVENT_READ, 'events')
                except OSError:
                    if events is not None:
                        events.close()
                    events, reconnect_at = None, now + 5
            for key, _ in selector.select(min(.3, max(0, service.next_poll - now))):
                if key.data == 'control':
                    connection, _ = server.accept()
                    with connection:
                        connection.settimeout(.3)
                        try:
                            raw = connection.recv(4096)
                            request = json.loads(raw.partition(b'\n')[0])
                            response = service.request(request.get('action', ''))
                        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
                            response = {'error': str(error)[:250]}
                        try:
                            connection.sendall(json.dumps(response).encode() + b'\n')
                        except OSError:
                            pass
                else:
                    try:
                        data = events.recv(65536)
                    except OSError:
                        data = b''
                    if not data:
                        selector.unregister(events)
                        events.close()
                        events, reconnect_at = None, now + 2
                        continue
                    event_data += data
                    lines = event_data.split(b'\n')
                    event_data = lines.pop()[-65536:]
                    if any(line.partition(b'>>')[0].decode('ascii', 'ignore') in relevant for line in lines):
                        service.next_poll = min(service.next_poll, now + .35)
            if time.monotonic() >= service.next_poll:
                service.poll()
                # Pending new windows settle their title/size before restoration.
                pending = [deadline for deadline in service.memory.pending.values() if deadline > time.monotonic()]
                service.next_poll = min([time.monotonic() + 2] + pending)
    finally:
        service.flush()
        selector.close()
        server.close()
        if events is not None:
            events.close()
        SOCKET.unlink(missing_ok=True)
        lock.close()


def layout_main():
    parser = argparse.ArgumentParser(description='记住应用的显示器、工作区与浮动窗口位置，不自动启动应用')
    group = parser.add_mutually_exclusive_group()
    for option in ('start', 'daemon', 'status', 'save', 'restore', 'stop', 'restart'):
        group.add_argument('--' + option, action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='与 --restore 合用，只打印布局计划')
    args = parser.parse_args()
    if args.dry_run and not args.restore:
        parser.error('--dry-run 需要与 --restore 合用')
    if args.daemon:
        layout_daemon()
        return
    if args.restore and args.dry_run:
        memory = load_memory()
        print(json.dumps({'plans': memory.explicit_plans(query('clients'), query('monitors'))}, ensure_ascii=False, indent=2))
        return
    if args.start or args.restart:
        if args.restart:
            try:
                send_layout('stop')
                for _ in range(30):
                    if not SOCKET.exists():
                        break
                    time.sleep(.05)
            except (OSError, ValueError, RuntimeError):
                pass
        response = start_layout()
    else:
        action = 'save' if args.save else ('restore' if args.restore else ('stop' if args.stop else 'status'))
        try:
            response = send_layout(action)
        except (OSError, ValueError):
            if action == 'save':
                memory = load_memory()
                memory.observe(query('clients'), query('monitors'), baseline=True)
                write_json(LAYOUT_FILE, memory.document())
                response = {'saved': True, 'records': len(memory.records), 'running': False}
            elif action == 'restore':
                memory = load_memory()
                plans = memory.explicit_plans(query('clients'), query('monitors'))
                for plan in plans:
                    apply_plan(plan)
                response = {'restored': len(plans), 'running': False}
            else:
                response = {'running': False, 'records': len(load_memory().records), 'state_file': str(LAYOUT_FILE)}
    print(json.dumps(response, ensure_ascii=False, indent=2))
