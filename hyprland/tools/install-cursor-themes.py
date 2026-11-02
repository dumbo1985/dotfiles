#!/usr/bin/env python3
"""Install pinned upstream cursor themes for this user, without selecting them.

Bibata, Catppuccin and Nordzy use upstream release binaries. Capitaine and
Volantes are rendered from upstream SVG source with librsvg, retaining their
hotspots, animations and aliases. This installer never runs upstream shell
scripts, modifies system paths, or changes the active cursor.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

HOME = Path.home()
ICONS = Path(os.environ.get('XDG_DATA_HOME', str(HOME / '.local/share'))) / 'icons'
CACHE = Path(os.environ.get('XDG_CACHE_HOME', str(HOME / '.cache'))) / 'hypr-cursors'
BIBATA = 'https://github.com/ful1e5/Bibata_Cursor/releases/download/v2.0.7/'
CATPPUCCIN = 'https://github.com/catppuccin/cursors/releases/download/v2.0.0/'
NORDZY = 'https://github.com/guillaumeboehm/Nordzy-cursors/releases/download/v2.4.0/'
RESOURCES = {
    'Bibata-Modern-Classic.tar.xz': (BIBATA + 'Bibata-Modern-Classic.tar.xz', '7d3495864e5bbef02f5e77de760b2905903b63c71495a78ef6306d19a3b556d8'),
    'Bibata-Modern-Ice.tar.xz': (BIBATA + 'Bibata-Modern-Ice.tar.xz', 'a68cae60c4dc706350e194ebc91c5fe48bc7bc9d59e119555834a2a7ee5078ef'),
    'Bibata-Modern-Amber.tar.xz': (BIBATA + 'Bibata-Modern-Amber.tar.xz', '58b7ac00ed3cb45acb6b917cb9807a553873f1cca5c91348c4abaebe638e5884'),
    'capitaine-r4.tar.gz': ('https://codeload.github.com/keeferrourke/capitaine-cursors/tar.gz/refs/tags/r4', '41f66e9f4d41729dc5e9185aab3bc4a719fdcca939e6f3f590b6b811b28dedd2'),
    'catppuccin-mocha-mauve-cursors.zip': (CATPPUCCIN + 'catppuccin-mocha-mauve-cursors.zip', '971e113a49de65529b3b706ce8529c1c80f22b2828b9c2f4732b3363fb69fcbb'),
    'catppuccin-mocha-lavender-cursors.zip': (CATPPUCCIN + 'catppuccin-mocha-lavender-cursors.zip', '9e8c67efd4c8ff75f09196fa8579ca366c5a4ea204f541edd7b49ab0cb44d9cf'),
    'Nordzy-cursors.tar.gz': (NORDZY + 'Nordzy-cursors.tar.gz', '3451c1221d58562a5eb647c45f3f7b5e2bbfe0aacf10d9cbc899bc36e5239e5a'),
    'Nordzy-cursors-white.tar.gz': (NORDZY + 'Nordzy-cursors-white.tar.gz', '5873641192f7c89692f1335c525969879307482c0f70283142f3fa65cfa74ff6'),
    'Nordzy-hyprcursors.tar.gz': (NORDZY + 'Nordzy-hyprcursors.tar.gz', 'd13767cd6d4757ddc3722e407d7a5f3422a4e4cce231495b7cf4d1be3e7a8b35'),
    'Nordzy-hyprcursors-white.tar.gz': (NORDZY + 'Nordzy-hyprcursors-white.tar.gz', '81d82bd012c1b76a48e1026f1fdb5a66bc9374fb1c6cad64530d3d1b6b14711e'),
    'volantes-b13a4bb.tar.gz': ('https://codeload.github.com/varlesh/volantes-cursors/tar.gz/b13a4bbf6bd1d7e85fadf7f2ecc44acc198f8d01', '24a8b82fb99011032669c8721e11ddb05350b57baff7f2b3751853b6868acce1'),
}


def download(name):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    url, expected = RESOURCES[name]
    if not path.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'dotfiles-cursor-installer'})
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read()
        path.write_bytes(data)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(f'Archive checksum mismatch: {path}')
    return path


def unpack(name, destination):
    path = download(name)
    if name.endswith('.zip'):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                target = destination / member.filename
                if not target.resolve().is_relative_to(destination.resolve()):
                    raise RuntimeError('Unsafe zip path')
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                data = archive.read(member)
                if stat.S_ISLNK(member.external_attr >> 16):
                    link = data.decode()
                    if not (target.parent / link).resolve().is_relative_to(destination.resolve()):
                        raise RuntimeError('Unsafe zip symlink')
                    target.symlink_to(link)
                else:
                    target.write_bytes(data)
    else:
        with tarfile.open(path) as archive:
            archive.extractall(destination, filter='data')
    return next(path for path in destination.iterdir() if path.is_dir())


def valid_cursor(theme):
    path = theme / 'cursors/left_ptr'
    return path.is_file() and path.read_bytes()[:4] == b'Xcur'


def validate(theme):
    if not valid_cursor(theme):
        raise RuntimeError(f'Missing or invalid Xcursor pointer: {theme}')
    metadata = configparser.ConfigParser(interpolation=None, strict=False)
    metadata.read(theme / 'index.theme')
    if not metadata.get('Icon Theme', 'Name', fallback='').strip():
        raise RuntimeError(f'Missing cursor theme name: {theme}')
    for cursor in ('text', 'hand2', 'wait', 'crosshair'):
        path = theme / 'cursors' / cursor
        if not path.is_file() or path.read_bytes()[:4] != b'Xcur':
            raise RuntimeError(f'Missing or invalid {cursor} cursor: {theme}')
    return metadata.get('Icon Theme', 'Name').strip()


def commit(staged, name, resource):
    destination = ICONS / name
    if destination.exists():
        print('Already installed:', name)
        return
    (staged / 'SOURCE.json').write_text(json.dumps({
        'archive': resource, 'url': RESOURCES[resource][0],
        'sha256': RESOURCES[resource][1],
        'built_locally': name.startswith(('capitaine-', 'volantes_')),
    }, indent=2) + '\n')
    staged.rename(destination)
    print('Installed:', name)


def install_binary(name):
    with tempfile.TemporaryDirectory(prefix='.cursor-install-', dir=ICONS) as directory:
        staged = unpack(name, Path(directory))
        if (staged / 'manifest.hl').exists():
            if not (list(staged.rglob('left_ptr.hlc')) or list(staged.rglob('default.hlc'))):
                raise RuntimeError(f'Missing native Hyprcursor pointer: {staged}')
        if (staged / 'cursors').is_dir():
            validate(staged)
        commit(staged, staged.name, name)


def render_svg(svg, png, size):
    import cairo
    import gi
    # The desktop suite keeps gi-cairo in a user-local package extraction.
    for root in (HOME / '.local/share/hypr-theme/root', HOME / '.local/share/hypr-motion/gtk-cairo'):
        extension = root / 'usr/lib/python3/dist-packages/gi'
        if extension.is_dir() and str(extension) not in gi.__path__:
            gi.__path__.append(str(extension))
    gi.require_foreign('cairo')
    gi.require_version('Rsvg', '2.0')
    from gi.repository import Rsvg
    handle = Rsvg.Handle.new_from_file(str(svg))
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    context = cairo.Context(surface)
    area = Rsvg.Rectangle()
    area.x, area.y, area.width, area.height = 0, 0, size, size
    handle.render_document(context, area)
    surface.write_to_png(str(png))


def aliases(directory, alias_file):
    for line in alias_file.read_text().splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        alias, source = parts
        target = directory / alias
        if not target.exists() and not target.is_symlink():
            target.symlink_to(source)


def build_capitaine():
    resource = 'capitaine-r4.tar.gz'
    with tempfile.TemporaryDirectory(prefix='.capitaine-build-', dir=ICONS) as directory:
        build = Path(directory)
        source = unpack(resource, build)
        for variant, name in [('dark', 'capitaine-cursors'), ('light', 'capitaine-cursors-light')]:
            if valid_cursor(ICONS / name):
                print('Already installed:', name)
                continue
            staged = build / name
            cursors = staged / 'cursors'
            cursors.mkdir(parents=True)
            raster = build / ('png-' + variant)
            raster.mkdir()
            for spec in sorted((source / 'src/config').rglob('*.spec')):
                values = [int(value) for value in spec.read_text().split()]
                xhot, yhot = values[:2]
                frames, delay = values[2:] if len(values) == 4 else (1, 0)
                rows = []
                for size in (24, 28, 32, 36, 48, 64, 96):
                    for frame in range(frames):
                        stem = spec.stem + (f'-{frame:02d}' if frames > 1 else '')
                        png = raster / f'{stem}_{size}.png'
                        render_svg(source / 'src/svg' / variant / (stem + '.svg'), png, size)
                        rows.append(f'{size} {int(xhot * size / 24)} {int(yhot * size / 24)} {png} {delay}')
                config = raster / (spec.stem + '.in')
                config.write_text('\n'.join(rows) + '\n')
                subprocess.run(['xcursorgen', str(config), str(cursors / spec.stem)], check=True)
            aliases(cursors, source / 'src/cursor-aliases')
            label = 'Capitaine Cursors' + (' - White' if variant == 'light' else '')
            (staged / 'index.theme').write_text('[Icon Theme]\nName=' + label + '\nComment=Upstream SVGs rendered locally with librsvg\n')
            shutil.copy2(source / 'COPYING', staged / 'COPYING')
            validate(staged)
            commit(staged, name, resource)


def build_volantes():
    resource = 'volantes-b13a4bb.tar.gz'
    with tempfile.TemporaryDirectory(prefix='.volantes-build-', dir=ICONS) as directory:
        build = Path(directory)
        source = unpack(resource, build)
        for name in ('volantes_cursors', 'volantes_light_cursors'):
            if valid_cursor(ICONS / name):
                print('Already installed:', name)
                continue
            staged = build / name
            cursors = staged / 'cursors'
            cursors.mkdir(parents=True)
            raster = build / ('png-' + name)
            raster.mkdir()
            for config in sorted((source / 'src/config').glob('*.cursor')):
                for row in config.read_text().splitlines():
                    fields = row.split()
                    if len(fields) < 4:
                        continue
                    png = raster / fields[3]
                    if not png.exists():
                        stem, size = png.stem.rsplit('_', 1)
                        render_svg(source / 'src' / name / (stem + '.svg'), png, int(size))
                subprocess.run(['xcursorgen', '-p', str(raster), str(config), str(cursors / config.stem)], check=True)
            aliases(cursors, source / 'src/cursorList')
            for filename in ('index.theme', 'cursor.theme'):
                shutil.copy2(source / 'src' / name / filename, staged / filename)
            for filename in ('LICENSE', 'AUTHORS'):
                shutil.copy2(source / filename, staged / filename)
            validate(staged)
            commit(staged, name, resource)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=['binary', 'capitaine', 'volantes'])
    args = parser.parse_args()
    ICONS.mkdir(parents=True, exist_ok=True)
    if args.only in (None, 'binary'):
        for name in RESOURCES:
            if name not in ('capitaine-r4.tar.gz', 'volantes-b13a4bb.tar.gz'):
                install_binary(name)
    if args.only in (None, 'capitaine'):
        build_capitaine()
    if args.only in (None, 'volantes'):
        build_volantes()
    # Ubuntu's libXcursor omits the XDG icon directory from its default path.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'config/lib'))
    from cursor_config import ensure_legacy_search_path
    ensure_legacy_search_path()


if __name__ == '__main__':
    main()
