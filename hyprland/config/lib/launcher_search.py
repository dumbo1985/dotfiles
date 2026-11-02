"""Bounded calculator, desktop application and filename search for the launcher."""
from __future__ import annotations

import ast
from dataclasses import dataclass
import math
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import threading
import time


@dataclass(frozen=True)
class Result:
    title: str
    subtitle: str
    kind: str
    target: str
    icon: str = ''


FUNCTIONS = {
    'sqrt': math.sqrt, 'abs': abs, 'round': round,
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log10, 'ln': math.log, 'exp': math.exp,
}
CONSTANTS = {'pi': math.pi, 'e': math.e}
EXCLUDED = ('node_modules', 'vendor', 'build', 'dist', 'target', '__pycache__',
            'venv', 'env', '.git', '.cache', '.local', '.npm', '.cargo', 'snap', 'squashfs-root')
EXCLUDED_PATHS = ('go/pkg/mod', 'go/pkg/sumdb')
_APP_TERMS: dict[str, str] = {}


def _bounded(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1e100:
        raise ValueError('数值超出计算范围')
    return value


def _number(node, depth=0):
    if depth > 12:
        raise ValueError('算式过于复杂')
    descend = lambda child: _number(child, depth + 1)
    if isinstance(node, ast.Constant):
        return _bounded(node.value)
    if isinstance(node, ast.Name) and node.id in CONSTANTS:
        return CONSTANTS[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = descend(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        first, second = descend(node.left), descend(node.right)
        if isinstance(node.op, ast.Add):
            value = first + second
        elif isinstance(node.op, ast.Sub):
            value = first - second
        elif isinstance(node.op, ast.Mult):
            value = first * second
        elif isinstance(node.op, ast.Div):
            value = first / second
        elif isinstance(node.op, ast.FloorDiv):
            value = first // second
        elif isinstance(node.op, ast.Mod):
            value = first % second
        elif isinstance(node.op, ast.Pow):
            if abs(second) > 1000 or (abs(first) > 1 and second * math.log10(abs(first)) > 100):
                raise ValueError('指数超出计算范围')
            value = first ** second
        else:
            raise ValueError('不支持这个运算')
        return _bounded(value)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS:
        if node.keywords or not 1 <= len(node.args) <= 2:
            raise ValueError('函数参数不正确')
        arguments = [descend(arg) for arg in node.args]
        if len(arguments) == 2 and node.func.id != 'round':
            raise ValueError('函数参数不正确')
        if node.func.id == 'round' and len(arguments) == 2:
            if type(arguments[1]) is not int or abs(arguments[1]) > 100:
                raise ValueError('小数位数超出范围')
        return _bounded(FUNCTIONS[node.func.id](*arguments))
    raise ValueError('只支持数字、数学运算和常用数学函数')


def _trailing_percentage(expression: str) -> str:
    """Bind a final percent sign to its atom, preserving ordinary precedence."""
    base = expression[:-1].rstrip()
    if base.endswith(')'):
        depth = 0
        start = None
        for index in range(len(base) - 1, -1, -1):
            depth += (base[index] == ')') - (base[index] == '(')
            if depth == 0:
                start = index
                break
        if start is None:
            raise SyntaxError('Unclosed parenthesis')
        function = re.search(r'[A-Za-z_][A-Za-z_0-9]*\s*$', base[:start])
        if function:
            start = function.start()
    else:
        atom = re.search(r'(?:\d[\d_]*(?:\.[\d_]*)?|\.[\d_]+)(?:[eE][+\-]?[\d_]+)?$|(?:pi|e)$', base)
        if atom is None:
            raise SyntaxError('Missing percentage operand')
        start = atom.start()
    return base[:start] + '(' + base[start:] + '/100)'


def calculate(query: str) -> Result | None:
    """Evaluate arithmetic without Python eval or access to user code/attributes."""
    text = query.strip()
    explicit = text.startswith('=')
    expression = text[1:].strip() if explicit else text
    expression = expression.replace('×', '*').replace('÷', '/').replace('−', '-').replace('^', '**')
    if not expression:
        return None
    if not explicit and not re.match(r'^(?:[\d.(+\-]|(?:sqrt|abs|round|sin|cos|tan|log|ln|exp)\s*\(|(?:pi|e)\b)', expression):
        return None
    # A filename such as "2026-report.pdf" should still be found normally.
    if not explicit and re.search(r'[A-Za-z_]', expression):
        names = re.findall(r'[A-Za-z_]+', expression)
        if any(name not in FUNCTIONS and name not in CONSTANTS and name not in ('E',) for name in names):
            return None
    try:
        if len(expression) > 256:
            raise ValueError('算式过长')
        if expression.endswith('%'):
            expression = _trailing_percentage(expression)
        tree = ast.parse(expression, mode='eval')
        if sum(1 for _ in ast.walk(tree)) > 100:
            raise ValueError('算式过于复杂')
        value = _number(tree.body)
        rendered = str(value) if type(value) is int else format(value, '.15g')
        if rendered == '-0':
            rendered = '0'
        return Result(rendered, text + '  ·  Enter 复制结果', 'calculator', rendered, 'accessories-calculator')
    except ZeroDivisionError:
        message = '除数不能为 0'
    except (SyntaxError, TypeError):
        # During normal typing, unfinished expressions should not flash errors.
        if not explicit:
            return None
        message = '算式尚未完成或格式不正确'
    except (ValueError, OverflowError, RecursionError) as error:
        message = str(error) if str(error) else '数值超出计算范围'
    return Result('无法计算', message, 'error', '', 'dialog-warning')


def load_applications() -> list[Result]:
    """Read visible XDG desktop entries; importing this module does not need GTK."""
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio

    applications = []
    _APP_TERMS.clear()
    for app in Gio.AppInfo.get_all():
        if not app.should_show() or not app.get_id():
            continue
        name = app.get_display_name() or app.get_name()
        description = app.get_description() or app.get_executable() or '应用程序'
        icon = app.get_icon()
        result = Result(name, description, 'application', app.get_id(), icon.to_string() if icon else 'application-x-executable')
        applications.append(result)
        keywords = app.get_keywords() if hasattr(app, 'get_keywords') else []
        generic = app.get_generic_name() if hasattr(app, 'get_generic_name') else ''
        _APP_TERMS[result.target] = ' '.join([name, description, app.get_id(), generic or '', *(keywords or [])]).casefold()
    return sorted(applications, key=lambda result: result.title.casefold())


def search_applications(query: str, apps: list[Result], limit=12) -> list[Result]:
    terms = query.casefold().split()
    if not terms:
        return apps[:limit]
    matches = [app for app in apps if all(term in _APP_TERMS.get(app.target, (app.title + ' ' + app.subtitle + ' ' + app.target).casefold()) for term in terms)]
    return sorted(matches, key=lambda app: (not app.title.casefold().startswith(query.casefold()), len(app.title), app.title.casefold()))[:limit]


def _file_result(path: Path, home: Path) -> Result | None:
    try:
        directory = path.is_dir()
        if not directory and not path.is_file():
            return None
        parent = str(path.parent)
        if parent == str(home) or parent.startswith(str(home) + '/'):
            parent = '~' + parent[len(str(home)):]
        return Result(path.name or str(path), parent, 'directory' if directory else 'file', str(path.absolute()), 'folder' if directory else 'text-x-generic')
    except OSError:
        return None


def _fd_paths(root: Path, fragment: str, cancel: threading.Event | None, limit: int,
              *, deadline=None, max_depth=None, min_depth=None, full_path=False):
    """Stream bounded NUL-delimited fd output, stopping and reaping on cancel."""
    executable = shutil.which('fdfind') or shutil.which('fd')
    deadline = deadline if deadline is not None else time.monotonic() + 3
    if time.monotonic() >= deadline or (cancel and cancel.is_set()):
        return
    if not executable:
        found = 0
        for parent, directories, files in os.walk(root):
            directories[:] = [name for name in directories if not name.startswith('.') and name not in EXCLUDED
                              and not any((Path(parent) / name).as_posix().endswith('/' + excluded) for excluded in EXCLUDED_PATHS)]
            names = directories + files
            entry_depth = len(Path(parent).relative_to(root).parts) + 1
            if max_depth is not None and entry_depth >= max_depth:
                directories[:] = []
            if time.monotonic() >= deadline or (cancel and cancel.is_set()):
                break
            if min_depth is not None and entry_depth < min_depth:
                continue
            for name in names:
                if time.monotonic() >= deadline or (cancel and cancel.is_set()):
                    return
                candidate = str(Path(parent) / name) if full_path else name
                if name.startswith('.') or fragment.casefold() not in candidate.casefold():
                    continue
                yield Path(parent) / name
                found += 1
                if found >= limit:
                    return
        return
    command = [executable, '--absolute-path', '--ignore-case', '--fixed-strings', '--print0',
               '--color', 'never', '--max-results', str(limit), '--threads', '2']
    if max_depth is not None:
        command += ['--max-depth', str(max_depth)]
    if min_depth is not None:
        command += ['--min-depth', str(min_depth)]
    if full_path:
        command += ['--full-path']
    for excluded in EXCLUDED + EXCLUDED_PATHS:
        command += ['--exclude', excluded]
    command += ['--', fragment, str(root)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    selector = selectors.DefaultSelector()
    try:
        selector.register(process.stdout, selectors.EVENT_READ)
        count, total, pending = 0, 0, b''
        while time.monotonic() < deadline and not (cancel and cancel.is_set()):
            if not selector.select(.05):
                if process.poll() is not None:
                    break
                continue
            data = os.read(process.stdout.fileno(), 8192)
            if not data:
                break
            total += len(data)
            if total > 512 * 1024:
                break
            pending += data
            parts = pending.split(b'\0')
            pending = parts.pop()
            for raw in parts:
                yield Path(os.fsdecode(raw))
                count += 1
                if count >= limit:
                    return
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


def search_files(query: str, cancel: threading.Event | None = None, limit=40, home: Path | None = None) -> list[Result]:
    """Find literal filenames/home-relative path fragments, or browse explicit paths."""
    if cancel and cancel.is_set():
        return []
    home = Path(home or Path.home()).absolute()
    text = query.strip()
    limit = max(1, min(int(limit), 80))
    if len(text) < 2 and text not in ('/', '~'):
        return []
    root, fragment = home, text
    try:
        if text.startswith(('/', '~/')) or text == '~':
            expanded = str(home) + text[1:] if text.startswith('~') else text
            path = Path(expanded)
            if path.exists() and not text.endswith('/'):
                item = _file_result(path, home)
                return [item] if item else []
            root, fragment = (path, '') if path.is_dir() else (path.parent, path.name)
            if not root.is_dir():
                return []
            # Explicit paths allow intentional access to dotfiles; browsing is shallow.
            matches = []
            deadline = time.monotonic() + 3
            for path in root.iterdir():
                if cancel and cancel.is_set():
                    return []
                if time.monotonic() >= deadline:
                    break
                if fragment.casefold() not in path.name.casefold():
                    continue
                if path.name.startswith('.') and not fragment.startswith('.'):
                    continue
                item = _file_result(path, home)
                if item:
                    matches.append(item)
                if len(matches) >= limit:
                    break
            return sorted(matches, key=lambda result: (result.kind != 'directory', result.title.casefold()))
        results = []
        deadline = time.monotonic() + 3
        # Collect nearby personal/project files before traversing deep source trees.
        for depth in ({'max_depth': 3}, {'min_depth': 4}):
            if cancel and cancel.is_set():
                return []
            if len(results) >= limit or time.monotonic() >= deadline:
                break
            paths = _fd_paths(root, fragment, cancel, limit - len(results), deadline=deadline,
                              full_path='/' in fragment, **depth)
            try:
                for path in paths:
                    if cancel and cancel.is_set():
                        return []
                    item = _file_result(path, home)
                    if item:
                        results.append(item)
            finally:
                paths.close()
        return sorted(results, key=lambda result: (result.title.casefold() != fragment.casefold(),
                      len(Path(result.target).relative_to(home).parts), result.kind != 'directory',
                      len(result.target), result.title.casefold()))
    except (OSError, ValueError):
        return []
