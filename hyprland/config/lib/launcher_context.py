"""Local windows, clipboard, projects, snippets and tmux launcher providers."""
from __future__ import annotations

from collections import deque
from datetime import datetime
import json
import os
from pathlib import Path
import re
import selectors
import shlex
import shutil
import subprocess
import threading
import time

from launcher_search import Result


CONFIG = Path(__file__).resolve().parent.parent
SNIPPETS_FILE = CONFIG / 'launcher-snippets.json'
PROJECTS_FILE = CONFIG / 'launcher-projects.json'
ADDRESS = re.compile(r'0x[0-9a-fA-F]+\Z')
TMUX_NAME = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_-]{0,63}\Z')
PROJECT_MARKERS = ('.git', 'pyproject.toml', 'package.json', 'Cargo.toml', 'go.mod',
                   'CMakeLists.txt', 'Makefile', 'pom.xml', 'build.gradle', 'setup.py')
PROJECT_EXCLUDED = {'node_modules', 'vendor', 'build', 'dist', 'target', '__pycache__',
                    'venv', 'env', 'squashfs-root', 'worktree-backups', 'worktree-archives'}


def _program(name: str) -> str | None:
    """Find private desktop-suite wrappers even outside the session PATH."""
    executable = shutil.which(name)
    if executable:
        return executable
    data = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    for path in (data / 'hypr-theme/bin' / name, Path.home() / '.local/bin' / name):
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def _command_bytes(arguments, cancel=None, timeout=1.5, cap=512 * 1024):
    """Read small command output with cancellation; always reap subprocesses."""
    if cancel and cancel.is_set():
        return b''
    try:
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return b''
    selector = selectors.DefaultSelector()
    chunks, total = [], 0
    deadline = time.monotonic() + timeout
    try:
        selector.register(process.stdout, selectors.EVENT_READ)
        while time.monotonic() < deadline and not (cancel and cancel.is_set()):
            if not selector.select(.05):
                if process.poll() is not None:
                    break
                continue
            data = os.read(process.stdout.fileno(), min(8192, cap - total + 1))
            if not data:
                break
            total += len(data)
            if total > cap:
                return b''
            chunks.append(data)
        if time.monotonic() >= deadline or (cancel and cancel.is_set()):
            return b''
        return b''.join(chunks)
    finally:
        selector.close()
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=.2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdout.close()


def _text(arguments, cancel=None, **kwargs):
    return _command_bytes(arguments, cancel, **kwargs).decode('utf-8', 'replace')


def _clean(text, limit=160):
    return ' '.join(re.sub(r'[\x00-\x1f\x7f]', ' ', str(text or '')).split())[:limit]


def _matches(query, *values):
    haystack = ' '.join(str(value or '') for value in values).casefold()
    return all(token in haystack for token in query.casefold().split())


def search_windows(query='', cancel=None, limit=30):
    """Search mapped Hyprland clients; raw addresses are validated before use."""
    if cancel and cancel.is_set():
        return []
    try:
        clients = json.loads(_text(['hyprctl', 'clients', '-j'], cancel))
        if not isinstance(clients, list):
            return []
    except (ValueError, TypeError):
        return []
    clients = [client for client in clients if isinstance(client, dict)]
    def history(client):
        value = client.get('focusHistoryID', 9999)
        value = value if isinstance(value, (int, float)) else 9999
        return value < 0, value
    clients.sort(key=history)
    results = []
    for client in clients:
        address = client.get('address', '')
        if not isinstance(address, str) or not ADDRESS.fullmatch(address):
            continue
        if not client.get('mapped', True) or client.get('hidden', False):
            continue
        app = _clean(client.get('class') or client.get('initialClass') or '应用', 50)
        title = _clean(client.get('title') or client.get('initialTitle') or app)
        workspace = client.get('workspace') or {}
        workspace = workspace if isinstance(workspace, dict) else {}
        name = workspace.get('name') or workspace.get('id', '?')
        if not _matches(query, app, title, name):
            continue
        results.append(Result(title, f'{app}  ·  工作区 {_clean(name, 25)}  ·  Enter 切换',
                              'window', address, 'preferences-system-windows'))
        if len(results) >= limit:
            break
    return results


def activate_window(address):
    if not isinstance(address, str) or not ADDRESS.fullmatch(address):
        raise ValueError('窗口地址无效')
    expression = 'hl.dispatch(hl.dsp.focus({window=' + json.dumps('address:' + address) + '}))'
    subprocess.run(['hyprctl', 'eval', expression], check=True, timeout=2,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def search_clipboard(query='', cancel=None, limit=30):
    """Return cliphist rows without decoding or printing private clipboard text."""
    if cancel and cancel.is_set():
        return []
    executable = _program('cliphist')
    if not executable:
        return [Result('剪贴板历史暂不可用', '请检查桌面剪贴板服务', 'error', '', 'edit-paste')]
    rows = _text([executable, 'list'], cancel).splitlines()
    results = []
    for line in rows:
        identifier, separator, preview = line.partition('\t')
        if not separator or not identifier.isdecimal() or not _matches(query, preview):
            continue
        binary = preview.startswith('[[') and 'binary' in preview.casefold()
        results.append(Result(_clean(preview, 140) or '空白文本',
                              ('图片或文件' if binary else '文本') + '  ·  Enter 复制到剪贴板',
                              'clipboard', line, 'image-x-generic' if binary else 'edit-paste'))
        if len(results) >= limit:
            break
    return results


def _clipboard_type(line):
    preview = line.partition('\t')[2].casefold()
    if not preview.startswith('[[') or 'binary' not in preview:
        return None
    for token, mimetype in (('png', 'image/png'), ('jpeg', 'image/jpeg'), ('jpg', 'image/jpeg'),
                            ('gif', 'image/gif'), ('webp', 'image/webp'), ('bmp', 'image/bmp')):
        if re.search(r'\b' + token + r'\b', preview):
            return mimetype
    return None


def copy_clipboard(line):
    if not isinstance(line, str) or len(line) > 65536:
        raise ValueError('剪贴板记录无效')
    identifier, separator, _ = line.partition('\t')
    if not separator or not identifier.isdecimal() or '\n' in line or '\r' in line:
        raise ValueError('剪贴板记录无效')
    cliphist, copy = _program('cliphist'), _program('wl-copy')
    if not cliphist or not copy:
        raise RuntimeError('缺少剪贴板程序')
    decoder = subprocess.Popen([cliphist, 'decode'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
    copier = None
    try:
        arguments = [copy]
        mimetype = _clipboard_type(line)
        if mimetype:
            arguments += ['--type', mimetype]
        copier = subprocess.Popen(arguments, stdin=decoder.stdout, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
        decoder.stdout.close()
        decoder.stdin.write((line + '\n').encode())
        decoder.stdin.close()
        decoder.wait(timeout=3)
        copier.wait(timeout=3)
        if decoder.returncode or copier.returncode:
            raise RuntimeError('无法恢复这条剪贴板记录')
    finally:
        for process in (decoder, copier):
            if process is not None and process.poll() is None:
                process.kill()
                process.wait()
        if decoder.stdin and not decoder.stdin.closed:
            decoder.stdin.close()
        if decoder.stdout and not decoder.stdout.closed:
            decoder.stdout.close()


def _project_roots(home):
    defaults = ['~/dotfiles', '~/Documents/workspace', '~/Documents/dengprojects',
                '~/Documents/learning', '~/Projects']
    try:
        config = json.loads(PROJECTS_FILE.read_text())
        raw = config.get('roots', defaults) if isinstance(config, dict) else defaults
        roots = raw if isinstance(raw, list) else defaults
    except (OSError, ValueError):
        roots = defaults
    paths = []
    for value in roots[:30]:
        if not isinstance(value, str):
            continue
        if value == '~' or value.startswith('~/'):
            value = str(home) + value[1:]
        path = Path(value)
        path = path if path.is_absolute() else home / path
        if path.is_dir() and path not in paths:
            paths.append(path)
    return paths


def load_projects(cancel=None, home=None):
    """Discover project roots by breadth first traversal with time/node/depth caps."""
    home = Path(home or Path.home())
    pending = deque((path, 0) for path in _project_roots(home))
    visited, results = set(), []
    deadline = time.monotonic() + 1.5
    while pending and len(visited) < 1800 and len(results) < 200 and time.monotonic() < deadline:
        if cancel and cancel.is_set():
            return []
        path, depth = pending.popleft()
        if path in visited:
            continue
        visited.add(path)
        try:
            project = any((path / marker).exists() for marker in PROJECT_MARKERS)
            if project:
                label = str(path)
                if label.startswith(str(home) + '/'):
                    label = '~' + label[len(str(home)):]
                results.append(Result(path.name, label + '  ·  Enter 用 Neovide 打开',
                                      'project', str(path.absolute()), 'folder-development'))
                # A project's dependencies/examples are not separate top-level projects.
                continue
            if depth >= 3:
                continue
            children = []
            with os.scandir(path) as entries:
                for entry in entries:
                    if time.monotonic() >= deadline or (cancel and cancel.is_set()):
                        break
                    if entry.name.startswith('.') or entry.name in PROJECT_EXCLUDED:
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        children.append(Path(entry.path))
                    if len(children) >= 300:
                        break
            pending.extend((child, depth + 1) for child in sorted(children))
        except OSError:
            continue
    return sorted(results, key=lambda result: (result.title.casefold(), result.target))


def search_projects(query='', cancel=None, limit=30, projects=None):
    if cancel and cancel.is_set():
        return []
    projects = projects if projects is not None else load_projects(cancel)
    return [result for result in projects if _matches(query, result.title, result.target)][:limit]


def open_project(path):
    project = Path(path)
    if not project.is_absolute() or not project.is_dir():
        raise ValueError('项目目录不存在')
    neovide = _program('neovide')
    if not neovide:
        raise RuntimeError('未找到 Neovide')
    subprocess.Popen([neovide, '--', '.'], cwd=str(project), stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def load_snippets():
    try:
        snippets = json.loads(SNIPPETS_FILE.read_text())
        return snippets if isinstance(snippets, list) else []
    except (OSError, ValueError):
        return []


def search_snippets(query='', cancel=None, limit=30):
    if cancel and cancel.is_set():
        return []
    now = datetime.now()
    replacements = {'date': now.strftime('%Y-%m-%d'), 'time': now.strftime('%H:%M:%S'),
                    'datetime': now.strftime('%Y-%m-%d %H:%M:%S'), 'year': now.strftime('%Y')}
    results = []
    for snippet in load_snippets():
        if not isinstance(snippet, dict):
            continue
        name, content = snippet.get('name'), snippet.get('content')
        if not isinstance(name, str) or not isinstance(content, str):
            continue
        description = str(snippet.get('description') or '')
        keywords = snippet.get('keywords', [])
        keywords = ' '.join(str(value) for value in keywords) if isinstance(keywords, list) else str(keywords)
        if not _matches(query, name, description, keywords):
            continue
        if not content:
            if name == '邮箱':
                email = _text(['git', 'config', '--get', 'user.email'], cancel, cap=4096).strip()
                if re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                    content = email
            if not content:
                results.append(Result(name + '：填写内容', '编辑 launcher-snippets.json 后即可复制',
                                      'file', str(SNIPPETS_FILE), 'document-edit'))
                continue
        for token, value in replacements.items():
            content = content.replace('{{' + token + '}}', value)
        results.append(Result(name, description + '  ·  Enter 复制片段', 'snippet', content, 'insert-text'))
        if len(results) >= limit:
            break
    return results


def search_tmux(query='', cancel=None, limit=30):
    if cancel and cancel.is_set():
        return []
    executable = _program('tmux')
    if not executable:
        return [Result('未安装 tmux', '当前无法打开 tmux 工作区', 'error', '', 'utilities-terminal')]
    output = _text([executable, 'list-sessions', '-F', '#{session_name}\t#{session_windows}\t#{session_attached}'], cancel)
    if cancel and cancel.is_set():
        return []
    results, names = [], set()
    for line in output.splitlines():
        name, separator, detail = line.partition('\t')
        if not separator or not name or any(character in name for character in '\r\n\0'):
            continue
        names.add(name)
        if not _matches(query, name):
            continue
        windows, _, attached = detail.partition('\t')
        results.append(Result(name, f'{_clean(windows)} 个窗口  ·  ' + ('已有客户端连接' if attached != '0' else '未连接') + '  ·  Enter 接入',
                              'tmux', name, 'utilities-terminal'))
    name = query.strip()
    if TMUX_NAME.fullmatch(name) and name not in names:
        results.insert(0, Result('新建 tmux：' + name, '若会话已存在则直接接入  ·  Enter 打开',
                                 'tmux', name, 'utilities-terminal'))
    return results[:limit]


def _terminal_command(arguments):
    configured = os.environ.get('DOTFILES_LAUNCHER_TERMINAL', '').strip()
    if configured:
        prefix = shlex.split(configured)
        if not prefix:
            raise ValueError('终端配置为空')
        return prefix + arguments
    wezterm = _program('wezterm')
    if wezterm:
        return [wezterm, 'start', '--'] + arguments
    kitty = _program('kitty')
    if kitty:
        return [kitty, '--'] + arguments
    flatpak = _program('flatpak')
    if flatpak:
        return [flatpak, 'run', 'org.wezfurlong.wezterm', 'start', '--',
                '/usr/bin/flatpak-spawn', '--host'] + arguments
    raise RuntimeError('未找到可用终端')


def open_tmux(session):
    if not isinstance(session, str) or not session or len(session) > 128 or any(char in session for char in '\0\r\n'):
        raise ValueError('tmux 会话名称无效')
    executable = _program('tmux')
    if not executable:
        raise RuntimeError('未找到 tmux')
    environment = os.environ.copy()
    environment.pop('TMUX', None)
    environment.pop('TMUX_PANE', None)
    subprocess.Popen(_terminal_command([executable, 'new-session', '-A', '-s', session]),
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, env=environment)
