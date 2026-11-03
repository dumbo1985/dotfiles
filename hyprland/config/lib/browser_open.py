"""Open external web links in Chrome and follow its window across workspaces."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


CHROME = '/usr/bin/google-chrome-stable'
CLASSES = {'google-chrome', 'google-chrome-stable', 'com.google.chrome'}
ADDRESS = re.compile(r'0x[0-9a-fA-F]+\Z')
DESKTOP_MARKER = 'X-Dotfiles-Browser-Focus=true'


def chrome_clients(clients):
    """Exclude browser PWAs, unmapped windows and non-browser helper windows."""
    result = []
    for client in clients:
        if not isinstance(client, dict):
            continue
        address = client.get('address', '')
        if not isinstance(address, str) or not ADDRESS.fullmatch(address):
            continue
        if not client.get('mapped', True) or client.get('hidden', False):
            continue
        current = str(client.get('class') or '').casefold()
        initial = str(client.get('initialClass') or current).casefold()
        if current in CLASSES and initial in CLASSES:
            result.append(client)
    return result


def history(client):
    value = client.get('focusHistoryID', -1)
    return value if isinstance(value, (int, float)) and value >= 0 else float('inf')


def choose_target(before, after):
    previous = {client['address']: client for client in chrome_clients(before)}
    candidates = chrome_clients(after)
    def priority(client):
        old = previous.get(client['address'])
        changed = old is not None and client.get('title') != old.get('title')
        return (0 if old is None else 1 if changed else 2, history(client))
    return min(candidates, key=priority) if candidates else None


def query_clients():
    result = subprocess.run(['hyprctl', 'clients', '-j'], capture_output=True,
                            text=True, timeout=1, check=True)
    clients = json.loads(result.stdout)
    return clients if isinstance(clients, list) else []


def focus_window(address):
    if not ADDRESS.fullmatch(address):
        raise ValueError('Invalid browser window address')
    selector = json.dumps('address:' + address)
    expression = 'hl.dispatch(hl.dsp.focus({window=' + selector + '}))'
    result = subprocess.run(['hyprctl', 'eval', expression], capture_output=True,
                            text=True, timeout=2, check=True)
    if result.stdout.strip().lower().startswith('error'):
        raise RuntimeError('Browser focus failed')


def open_browser(arguments):
    follow = bool(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')) and any(
        value.casefold().startswith(('http://', 'https://')) for value in arguments)
    try:
        before = query_clients() if follow else []
    except (OSError, ValueError, subprocess.SubprocessError):
        before = []
    # Use Chrome's native launcher directly; xdg-open here would recurse through
    # our desktop entry. Arguments are never interpreted as shell commands.
    process = subprocess.Popen([CHROME, *arguments], stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               start_new_session=True)
    if not follow:
        return 0
    deadline = time.monotonic() + 8
    ready_after = time.monotonic() + .35
    previous = {client['address']: client for client in chrome_clients(before)}
    while time.monotonic() < deadline:
        time.sleep(.1)
        status = process.poll()
        if status is not None and status != 0:
            return status
        try:
            target = choose_target(before, query_clients())
            if target is None:
                continue
            old = previous.get(target['address'])
            changed = old is None or target.get('title') != old.get('title')
            # Chrome usually forwards immediately to an existing process. Give
            # it a moment to select its new tab, or wait for a cold-start window.
            if changed or time.monotonic() >= ready_after:
                focus_window(target['address'])
                return 0
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
            # Opening the link still succeeds if the compositor is unavailable.
            return 0
    return 0


def install_desktop_entry(config, data, source=Path('/usr/share/applications/google-chrome.desktop')):
    """Keep Chrome's desktop identity/defaults and its native window actions."""
    source = Path(source)
    if not source.is_file():
        return False
    target = Path(data) / 'applications/google-chrome.desktop'
    if target.exists() and DESKTOP_MARKER not in target.read_text():
        print('Chrome 已有自定义启动入口，保留该文件。', file=sys.stderr)
        return False
    executable = str(Path(config) / 'bin/browser-open').replace('%', '%%')
    # Ubuntu's generic xdg-open treats quotes around the first word literally.
    # Use a bare absolute path for ordinary paths; quote only when required by
    # the desktop-entry format (GIO supports those paths as well).
    if not re.fullmatch(r'[A-Za-z0-9_./:%+-]+', executable):
        executable = '"' + re.sub(r'([\\"`$])', r'\\\1', executable) + '"'
    content = source.read_text()
    content = re.sub(r'(?m)^Exec=.*$', lambda _: 'Exec=' + executable + ' %U', content, count=1)
    content = content.replace('[Desktop Entry]\n', '[Desktop Entry]\n' + DESKTOP_MARKER + '\n', 1)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_text() != content:
        target.write_text(content)
    return True


def main(argv=None):
    try:
        return open_browser(list(sys.argv[1:] if argv is None else argv))
    except OSError:
        print('无法启动 Google Chrome。', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
