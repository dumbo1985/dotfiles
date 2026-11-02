"""Shared cursor catalogue, preferences and compatibility search paths."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

CONFIG = Path(__file__).resolve().parent.parent
STATE = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'dotfiles-hyprland'
STATE_FILE = STATE / 'cursor.json'
DEFAULTS = {'theme': 'rose-pine', 'mode': 'stretch', 'shake': True, 'size': 28}
MODES = ('stretch', 'tilt', 'rotate', 'none')
SIZES = (24, 28, 32, 36)


def catalog():
    try:
        entries = json.loads((CONFIG / 'cursors/catalog.json').read_text())
    except (OSError, ValueError):
        entries = {'rose-pine': {'name': 'Rosé Pine', 'xcursor': 'BreezeX-RosePine',
                                'hyprcursor': 'rose-pine-hyprcursor', 'description': '玫瑰松配色'}}
    valid = {}
    for key, entry in entries.items():
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', key) or not isinstance(entry, dict):
            continue
        if not all(isinstance(entry.get(field, ''), str) for field in ('name', 'description', 'xcursor', 'hyprcursor')):
            continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', entry.get('xcursor', '')):
            continue
        if entry.get('hyprcursor') and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', entry['hyprcursor']):
            continue
        valid[key] = entry
    return valid


def icon_roots():
    data = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    roots = [data / 'icons', Path.home() / '.icons']
    roots += [Path(part).expanduser() for part in os.environ.get('XCURSOR_PATH', '').split(':') if part]
    roots += [Path(part) / 'icons' for part in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if part]
    return roots


def ensure_legacy_search_path():
    """Expose local themes to libXcursor processes that cached the old path.

    Ubuntu's libXcursor searches ~/.icons but omits XDG_DATA_HOME/icons. An
    environment change cannot update its process-wide cached library path.
    Never replace an existing directory, file or user-owned symlink.
    """
    local = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'icons'
    local.mkdir(parents=True, exist_ok=True)
    legacy = Path.home() / '.icons'
    if not legacy.exists() and not legacy.is_symlink():
        legacy.symlink_to(local, target_is_directory=True)
        return
    if not legacy.is_dir() or legacy.resolve() == local.resolve():
        return
    for entry in catalog().values():
        for name in (entry['xcursor'], entry.get('hyprcursor', '')):
            if not name:
                continue
            target, link = local / name, legacy / name
            if target.is_dir() and not link.exists() and not link.is_symlink():
                link.symlink_to(target, target_is_directory=True)


def cursor_search_path():
    roots = [str(root) for root in icon_roots()] + ['/usr/share/pixmaps']
    return ':'.join(dict.fromkeys(roots))


def installed(name, native=False):
    for root in icon_roots():
        theme = root / name
        if native and any((theme / manifest).is_file() for manifest in ('manifest.hl', 'manifest.toml')):
            return True
        if not native and (theme / 'cursors').is_dir() and any((theme / 'cursors').iterdir()):
            return True
    return False


def available_themes():
    return {key: entry for key, entry in catalog().items()
            if entry.get('available', True) and installed(entry['xcursor'])}


def load_settings():
    result = dict(DEFAULTS)
    try:
        saved = json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        saved = {}
    if not isinstance(saved, dict):
        return result
    theme = saved.get('theme')
    if isinstance(theme, str) and theme in available_themes():
        result['theme'] = theme
    if saved.get('mode') in MODES:
        result['mode'] = saved['mode']
    if isinstance(saved.get('shake'), bool):
        result['shake'] = saved['shake']
    if type(saved.get('size')) is int and saved['size'] in SIZES:
        result['size'] = saved['size']
    return result


def cursor_environment(settings=None):
    settings = settings or load_settings()
    entry = catalog()[settings['theme']]
    native = entry.get('hyprcursor', '')
    if native and not installed(native, native=True):
        native = ''
    return {'XCURSOR_THEME': entry['xcursor'], 'XCURSOR_SIZE': str(settings['size']),
            'HYPRCURSOR_THEME': native, 'HYPRCURSOR_SIZE': str(settings['size']),
            'XCURSOR_PATH': cursor_search_path()}
