#!/usr/bin/env python3
"""Build local palette adaptations of the installed Tokyonight GTK theme.

These variants retain Tokyo Night's widget layout and asset structure. They
apply the color schemes registered in the desktop palette catalog; they are
local adaptations rather than official GTK distributions of those schemes.
No network or root is needed.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

from PIL import Image

sys.dont_write_bytecode = True
CONFIG = Path(__file__).resolve().parent.parent / 'config'
sys.path.insert(0, str(CONFIG / 'lib'))
from theme_palette import COLOR_ROLES, palettes

DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
SOURCE = DATA / 'themes/Tokyonight-Dark'
UPSTREAM = 'https://github.com/Fausto-Korpsvart/Tokyo-Night-GTK-Theme'
SOURCE_COMMIT = '6c340e058e84c1975a038a8e5d1e384477225dc0'
GENERATOR_VERSION = 2

# The installed GTK base also contains upstream's original light/dark semantic
# accents and computed surface shades beyond the desktop component colors.
GTK_ROLES = COLOR_ROLES | {
    '323449': 'surface', '1f2231': 'surface', '4b4c5f': 'overlay',
    '545c7e': 'comment', '848cb5': 'muted', 'b6b8cd': 'fg',
    'c7c7d1': 'fg', 'd2d2da': 'fg', 'e1e2e7': 'fg', 'e9e9ed': 'fg',
    'f52a65': 'red', 'd20065': 'red', 'ff007c': 'red',
    '7847bd': 'purple', '2e7de9': 'blue',
    '27a1b9': 'blue', '006a83': 'blue',
    '118c74': 'cyan', '1abc9c': 'cyan', '387068': 'green',
    '007197': 'cyan', '8c6c3e': 'yellow', 'b15c00': 'orange',
}
# A selector such as #add-color-button is an identifier, not shorthand #add.
HEX = re.compile(r'(?i)#([0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3})(?![\w-])')
RGB = re.compile(r'(?i)\b(rgb|rgba)\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(\s*,\s*[.\d]+)?\s*\)')
TEXT_SUFFIXES = {'.css', '.svg', '.rc', '.xml', '.theme'}


def rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def mapper(palette):
    anchors = {rgb(source): rgb(palette['colors'][role]) for source, role in GTK_ROLES.items()}

    @lru_cache(maxsize=65536)
    def convert(color):
        if color in anchors:
            return anchors[color]
        # Derived highlight/shadow shades retain their offset from the closest
        # source anchor. Mapping is simultaneous, so target colors are never
        # interpreted again as source colors.
        anchor = min(anchors, key=lambda a: sum((a[i] - color[i]) ** 2 for i in range(3)))
        target = anchors[anchor]
        return tuple(max(0, min(255, target[i] + color[i] - anchor[i])) for i in range(3))

    return convert


def recolor_text(text, convert):
    def hexadecimal(match):
        value = match[1]
        if len(value) == 3:
            value = ''.join(char * 2 for char in value)
        converted = convert(rgb(value[:6]))
        return '#' + ''.join(f'{part:02x}' for part in converted) + value[6:]

    def numeric(match):
        converted = convert(tuple(int(match[i]) for i in (2, 3, 4)))
        return match[1] + '(' + ', '.join(map(str, converted)) + (match[5] or '') + ')'

    return RGB.sub(numeric, HEX.sub(hexadecimal, text))


def recolor_image(path, convert):
    with Image.open(path) as image:
        image = image.convert('RGBA')
        image.putdata([(*convert(pixel[:3]), pixel[3]) if pixel[3] else pixel
                       for pixel in image.getdata()])
        image.save(path, optimize=True)


def build(theme_id, palette):
    target_name = palette['gtk_theme']
    if not re.fullmatch(r'Hypr-[A-Za-z0-9-]+', target_name):
        raise ValueError(f'Invalid adaptation name: {target_name}')
    themes = SOURCE.parent
    destination = themes / target_name
    convert = mapper(palette)
    with tempfile.TemporaryDirectory(prefix='.hypr-gtk-', dir=themes) as temporary:
        staged = Path(temporary) / target_name
        shutil.copytree(SOURCE, staged, symlinks=True)
        for path in staged.rglob('*'):
            if path.is_symlink() or not path.is_file():
                continue
            if path.suffix.lower() == '.png':
                recolor_image(path, convert)
            elif path.suffix.lower() in TEXT_SUFFIXES or path.name in {'gtkrc', 'themerc'}:
                text = recolor_text(path.read_text(), convert)
                if path.name == 'index.theme':
                    text = text.replace('Tokyonight-Dark', target_name)
                    text = re.sub(r'^Comment=.*$',
                                  'Comment=Local palette adaptation of Tokyo Night GTK', text,
                                  flags=re.M)
                path.write_text(text)
        license_file = Path.home() / '.cache/hypr-theme/tokyo-gtk/LICENSE'
        if license_file.is_file():
            shutil.copy2(license_file, staged / 'LICENSE')
        (staged / 'README.generated.md').write_text(
            f"# {palette['name']} — local GTK palette adaptation\n\n"
            f"Generated by dotfiles/hyprland/tools/build-gtk-themes.py for `{theme_id}`.\n"
            'This is a color adaptation of Tokyo Night GTK, not the official GTK\n'
            'distribution of the named color scheme. Widget layouts, selectors,\n'
            'asset names and directory structure are retained from the base.\n'
            'CSS, SVG and PNG colors are adapted to the desktop palette.\n\n'
            f'Upstream: {UPSTREAM}\nBase commit: {SOURCE_COMMIT}\n'
            'License: GNU GPL v3 (same as upstream).\n'
            'The installed base includes compatibility fixes for GTK3 3.24 and GTK4 4.14.\n'
        )
        (staged / 'palette.json').write_text(json.dumps(palette, ensure_ascii=False, indent=2) + '\n')
        (staged / '.palette-generator-version').write_text(str(GENERATOR_VERSION) + '\n')
        if destination.exists():
            # Only replace variants previously produced by this generator.
            if not (destination / 'README.generated.md').is_file():
                raise FileExistsError(f'Refusing to replace an unrelated theme: {destination}')
            shutil.rmtree(destination)
        staged.rename(destination)
    print(destination)


def up_to_date(palette):
    """Reuse generated assets only when their complete palette still matches."""
    target_name = palette['gtk_theme']
    if not re.fullmatch(r'Hypr-[A-Za-z0-9-]+', target_name):
        raise ValueError(f'Invalid adaptation name: {target_name}')
    destination = SOURCE.parent / target_name
    required = ('README.generated.md', 'palette.json',
                '.palette-generator-version', 'gtk-3.0/gtk.css', 'gtk-4.0/gtk.css')
    if not all((destination / name).is_file() for name in required):
        return False
    try:
        return (json.loads((destination / 'palette.json').read_text()) == palette
                and (destination / '.palette-generator-version').read_text().strip()
                == str(GENERATOR_VERSION))
    except (OSError, ValueError):
        return False


def main():
    available = palettes()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', choices=list(available), action='append')
    parser.add_argument('--missing-only', action='store_true',
                        help='Build only missing, incomplete or changed palette adaptations')
    args = parser.parse_args()
    if not (SOURCE / 'gtk-3.0/gtk.css').is_file() or not (SOURCE / 'gtk-4.0/gtk.css').is_file():
        parser.error(f'The installed Tokyo Night GTK base is required at {SOURCE}')
    for name in args.name or available:
        if name == 'tokyo-night':
            continue
        if args.missing_only and up_to_date(available[name]):
            print(f'Unchanged: {name}')
            continue
        build(name, available[name])


if __name__ == '__main__':
    main()
