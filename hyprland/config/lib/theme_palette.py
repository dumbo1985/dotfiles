"""Shared desktop palettes. Reading this module never changes the session."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

CONFIG = Path(__file__).resolve().parent.parent
STATE = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'dotfiles-hyprland'
STATE_FILE = STATE / 'theme.json'
PALETTES_FILE = CONFIG / 'themes/palettes.json'


def palettes():
    return json.loads(PALETTES_FILE.read_text())


def settings():
    try:
        result = json.loads(STATE_FILE.read_text())
        return result if isinstance(result, dict) else {}
    except (OSError, ValueError):
        return {}


def selected_palette():
    available = palettes()
    name = settings().get('name', 'tokyo-night')
    if not isinstance(name, str):
        name = 'tokyo-night'
    return available.get(name, available['tokyo-night'])


def luminance(color):
    values = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4 for value in values]
    return sum(value * weight for value, weight in zip(linear, (.2126, .7152, .0722)))


def contrast(first, second):
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + .05) / (low + .05)


def selection_text(palette, *roles):
    """Choose readable light or dark text, including on two-color gradients."""
    colors = palette['colors']
    backgrounds = [colors[role] for role in roles or ('blue',)]
    return max((colors['black'], colors['white']),
               key=lambda candidate: min(contrast(candidate, background) for background in backgrounds))


# Secondary Tokyo Night surface shades appear across the original components.
# Mapping each by role preserves legible text, shadows and borders in all themes.
COLOR_ROLES = {
    '1a1b26':'bg', '16161e':'black', '14151e':'black', '15161e':'black',
    '111118':'black', '0d0f19':'black', '080c16':'black', '080d1b':'black',
    '161925':'black', '171b2e':'bg', '101426':'bg', '090e1b':'black',
    '24283b':'surface', '1e2132':'surface', '202333':'surface', '202437':'surface',
    '282e45':'surface', '303751':'overlay',
    '292e42':'surface', '303752':'overlay', '343a55':'overlay',
    '343b58':'overlay', '343c5b':'overlay', '3b4261':'overlay',
    '414868':'overlay', '565f89':'comment', '737aa2':'comment',
    '9aa5ce':'muted', 'a9b1d6':'muted', 'c0caf5':'fg',
    '7aa2f7':'blue', 'bb9af7':'purple', '9d7cd8':'purple',
    '7dcfff':'cyan', '73daca':'cyan', '9ece6a':'green',
    'f7768e':'red', 'ff9e9e':'red', 'e0af68':'yellow',
    'ff9e64':'orange', 'ffffff':'white', '000000':'black',
    '33467c':'overlay', '7ba2f7':'blue', 'c8d3f5':'fg',
}
HEX = re.compile(r'(?i)(?<![a-z0-9])#([0-9a-f]{6})([0-9a-f]{2})?\b')
RGB = re.compile(r'(?i)\b(rgb|rgba)\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(\s*,\s*[.\d]+)?\s*\)')
HYPR = re.compile(r'(?i)\b(rgb|rgba)\(([0-9a-f]{6})([0-9a-f]{2})?\)')
ANSI = re.compile(r'38;2;(\d{1,3});(\d{1,3});(\d{1,3})')


def recolor(text, palette=None):
    """Replace canonical colors in one pass, preserving alpha and all syntax."""
    palette = palette or selected_palette()
    if palette == palettes()['tokyo-night']:
        return text
    colors = palette['colors']
    def target(value):
        role = COLOR_ROLES.get(value.lower())
        return colors[role][1:] if role else value
    text = HEX.sub(lambda m: '#' + target(m[1]) + (m[2] or ''), text)
    # Numeric RGB is processed against the source map, never the resulting hex.
    def rgb(match):
        value = ''.join(f'{int(match[i]):02x}' for i in (2, 3, 4))
        role = COLOR_ROLES.get(value)
        if not role:
            return match[0]
        color = colors[role][1:]
        values = ', '.join(str(int(color[i:i+2], 16)) for i in (0, 2, 4))
        return match[1] + '(' + values + (match[5] or '') + ')'
    text = RGB.sub(rgb, text)
    text = HYPR.sub(lambda m: m[1] + '(' + target(m[2]) + (m[3] or '') + ')', text)
    def ansi(match):
        value = ''.join(f'{int(match[i]):02x}' for i in (1, 2, 3))
        role = COLOR_ROLES.get(value)
        if not role:
            return match[0]
        color = colors[role][1:]
        return '38;2;' + ';'.join(str(int(color[i:i+2], 16)) for i in (0, 2, 4))
    return ANSI.sub(ansi, text)
