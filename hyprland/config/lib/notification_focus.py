"""Focus the existing window behind a clicked SwayNC notification.

Only app identity is used. Notification text is neither inspected nor stored,
and the application's own notification action continues to run normally.
"""
from __future__ import annotations

import argparse
import configparser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata


ADDRESS = re.compile(r'0x[0-9a-fA-F]+\Z')
APP_ALIASES = (
    ('飞书', 'Feishu', 'Bytedance-feishu', 'bytedance-feishu-stable',
     'Lark', 'Bytedance-lark'),
    ('微信', 'WeChat', 'com.tencent.wechat'),
    ('WezTerm', 'org.wezfurlong.wezterm'),
    ('Google Chrome', 'google-chrome', 'com.google.Chrome'),
    ('Firefox', 'org.mozilla.firefox'),
)


def identity(value):
    value = unicodedata.normalize('NFKC', str(value or '')).casefold().strip()
    if value.endswith('.desktop'):
        value = value[:-8]
    return ''.join(character for character in value if character.isalnum())


def aliases(value):
    key = identity(value)
    if not key:
        return set()
    for group in APP_ALIASES:
        keys = {identity(name) for name in group}
        if key in keys:
            return keys
    return {key}


def desktop_directories():
    data = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    roots = [data, *(Path(root) for root in os.environ.get(
        'XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if root),
        data / 'flatpak/exports/share', Path('/var/lib/flatpak/exports/share')]
    return list(dict.fromkeys(root / 'applications' for root in roots))


def app_identities(app_name, desktop_entry='', directories=None):
    """Match complete app IDs and desktop-file metadata, never title substrings."""
    names, entries = aliases(app_name), aliases(desktop_entry)
    scores = {key: 60 for key in names}
    scores.update({key: 100 for key in entries})
    if not scores:
        return scores
    seen = set()
    for directory in desktop_directories() if directories is None else directories:
        for path in sorted(Path(directory).glob('*.desktop')):
            if path.name in seen:
                continue
            seen.add(path.name)
            try:
                parser = configparser.ConfigParser(interpolation=None, strict=False)
                parser.read(path, encoding='utf-8')
                section = parser['Desktop Entry']
                if section.get('Type') != 'Application':
                    continue
                entry_names = set().union(*(aliases(value) for key, value in section.items()
                                          if key == 'name' or key.startswith('name[')))
                entry_ids = aliases(path.name)
                if not (entry_ids & entries if entries else (entry_ids | entry_names) & names):
                    continue
                for value, score in ((path.name, 100), (section.get('StartupWMClass'), 110)):
                    for key in aliases(value):
                        scores[key] = max(scores.get(key, 0), score)
                for key in entry_names:
                    scores[key] = max(scores.get(key, 0), 70)
            except (OSError, UnicodeError, configparser.Error, KeyError):
                continue
    return scores


def choose_client(clients, scores):
    candidates = []
    for client in clients:
        if not isinstance(client, dict):
            continue
        address = client.get('address', '')
        if not isinstance(address, str) or not ADDRESS.fullmatch(address):
            continue
        if not client.get('mapped', True) or client.get('hidden', False):
            continue
        score = max((scores.get(identity(client.get(field)), 0)
                     for field in ('class', 'initialClass')), default=0)
        if not score:
            continue
        history = client.get('focusHistoryID', -1)
        history = history if isinstance(history, (int, float)) and history >= 0 else float('inf')
        candidates.append((score, -history, address, client))
    return max(candidates, key=lambda row: row[:3])[3] if candidates else None


def command(arguments, **kwargs):
    return subprocess.run(arguments, check=True, timeout=2, capture_output=True,
                          text=True, **kwargs)


def activate(client):
    # A notification without a default action does not close SwayNC itself.
    command(['swaync-client', '--close-panel'])
    time.sleep(.20)
    selector = json.dumps('address:' + client['address'])
    command(['hyprctl', 'eval', 'hl.dispatch(hl.dsp.focus({window=' + selector + '}))'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='show the target without changing focus')
    args = parser.parse_args(argv)
    app_name = os.environ.get('SWAYNC_APP_NAME', '')
    desktop_entry = os.environ.get('SWAYNC_DESKTOP_ENTRY', '')
    if not app_name and not desktop_entry:
        return 0
    try:
        # SwayNC starts the hook just before delivering the application's action.
        # Let it choose/map its own target first, then fill in compositor focus.
        if not args.dry_run:
            time.sleep(.18)
        scores = app_identities(app_name, desktop_entry)
        clients = json.loads(command(['hyprctl', 'clients', '-j']).stdout)
        client = choose_client(clients, scores)
        if args.dry_run:
            print(json.dumps({key: client.get(key) for key in ('address', 'class', 'workspace')}
                             if client else None, ensure_ascii=False))
        elif client:
            activate(client)
        return 0
    except (OSError, ValueError, subprocess.SubprocessError):
        # Old history may outlive its app/window. Never reopen apps or notify
        # recursively; the application's own action is still delivered.
        print('Notification window focus unavailable', file=sys.stderr)
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
