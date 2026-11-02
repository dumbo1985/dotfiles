"""Query routing and discoverable commands for the desktop launcher."""
from __future__ import annotations

from dataclasses import dataclass
import ipaddress
from pathlib import Path
import re
import subprocess
from urllib.parse import quote_plus, urlsplit

from launcher_search import Result, calculate, search_applications, search_files

CONFIG = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Query:
    mode: str
    text: str


PREFIXES = {
    'w': 'windows', 'win': 'windows', '窗口': 'windows',
    'v': 'clipboard', 'clip': 'clipboard', '剪贴板': 'clipboard',
    'p': 'projects', 'project': 'projects', '项目': 'projects',
    't': 'tmux', 'tmux': 'tmux',
    's': 'snippets', 'snip': 'snippets', '片段': 'snippets',
    'dict': 'dictionary', '查词': 'dictionary', '词典': 'dictionary',
    'g': 'google', 'google': 'google', 'b': 'bing', 'bing': 'bing',
    'sys': 'system', '系统': 'system', '>': 'system',
}
HINTS = {
    'normal': 'w 窗口 · v 剪贴板 · p 项目 · t tmux · s 片段 · dict 查词 · ? 全部功能',
    'windows': 'w 名称或标题 · Enter 切换窗口',
    'clipboard': 'v 关键词 · 搜索剪贴板历史 · Enter 复制',
    'projects': 'p 项目名称 · Enter 用 Neovide 打开 · Ctrl+Enter 打开文件夹',
    'tmux': 't 会话名 · Enter 连接已有会话，没有时创建',
    'snippets': 's 名称 · Enter 复制常用文字 · 可编辑邮箱、地址和代码模板',
    'dictionary': 'dict 英文单词 · 音标、释义与例句 · Enter 复制选中内容',
    'google': 'g 搜索内容 · Enter 在浏览器中使用 Google 搜索',
    'bing': 'b 搜索内容 · Enter 在浏览器中使用 Bing 搜索',
    'system': '输入操作名称 · Enter 执行 · Esc 取消',
    'help': '选择功能后按 Enter，继续输入要查找的内容',
}

COMMANDS = [
    ('切换窗口', 'w neovide · 按名称或标题切换已打开窗口', 'w ', 'preferences-system-windows'),
    ('剪贴板历史', 'v 关键词 · 查找并复制之前复制过的内容', 'v ', 'edit-paste'),
    ('网页搜索', 'g Hyprland 快捷键 · Google；b 关键词 · Bing', 'g ', 'web-browser'),
    ('打开网址', '输入 github.com 或完整网址，Enter 打开', 'https://', 'web-browser'),
    ('查单词', 'dict hypothetical · 音标、中文释义和例句', 'dict ', 'accessories-dictionary'),
    ('单位换算', '10 km to mile · 32 f to c · 1 GB to MB', '10 km to mile', 'accessories-calculator'),
    ('打开项目', 'p dotfiles · 用 Neovide 打开项目目录', 'p ', 'folder-development'),
    ('tmux 会话', 't workspace · 连接会话，没有时再创建', 't ', 'utilities-terminal'),
    ('常用文字片段', 's 日期 · 复制邮箱、日期、地址或代码模板', 's ', 'edit-copy'),
    ('系统操作', '锁屏、截图、切换主题、网络、音量和电源菜单', 'sys ', 'preferences-system'),
    ('计算', '12*34 · (100+20)/3 · 2^10 · Enter 复制结果', '12*34', 'accessories-calculator'),
    ('查找文件', '输入文件名，或 ~/Documents/ 浏览目录', '~/Documents/', 'system-file-manager'),
    ('文件快速预览', '搜索文件后按 Alt+P；文件管理器中按空格', '~/Documents/', 'document-preview'),
    ('截图识字', 'Super+Shift+O 框选中英文；代码模式 Super+Ctrl+O', 'sys 识字', 'edit-select-all'),
    ('窗口布局记忆', '自动记住应用的屏幕和工作区，可手动保存或恢复', 'sys 布局', 'view-grid-symbolic'),
]

# Existing helpers retain their own interaction/confirmation behavior.
SYSTEM_ACTIONS = {
    'lock': ('锁屏', 'lock 锁定 屏幕', '立即锁定当前会话', 'system-lock-screen', ['power-menu', '--lock']),
    'screenshot': ('截图', 'screenshot 截屏 拍屏', '打开截图和标注菜单', 'applets-screenshooter', ['screenshot', 'menu']),
    'theme': ('切换主题', 'theme 配色 外观 桌面主题', '选择桌面主题和登录随机配色', 'preferences-desktop-theme', ['theme-picker']),
    'cursor': ('鼠标设置', 'cursor 鼠标 指针 光标', '更换鼠标外观和运动效果', 'preferences-desktop-mouse', ['cursor-picker']),
    'notifications': ('通知中心', 'notifications 通知 勿扰', '打开通知与快捷设置', 'preferences-system', ['control-center']),
    'panel': ('日历与系统面板', 'calendar 日历 系统面板 音乐', '查看日历、媒体和系统状态', 'x-office-calendar', ['desktop-panel']),
    'network': ('网络设置', 'network wifi 网络 无线', '打开网络连接设置', 'network-wireless', ['control-center', 'net']),
    'bluetooth': ('蓝牙设置', 'bluetooth 蓝牙', '打开蓝牙设备管理', 'bluetooth', ['control-center', 'bt']),
    'volume': ('音量设置', 'audio volume 音量 声音', '打开音频设备和音量控制', 'audio-volume-high', ['control-center', 'audio']),
    'power': ('电源菜单', 'power 关机 重启 注销 睡眠', '打开电源菜单后选择操作', 'system-shutdown', ['power-menu']),
    'ocr': ('截图识字', 'ocr 识字 识别 提取文字', '框选中英文并复制为文字', 'edit-select-all', ['screen-ocr']),
    'ocr-code': ('截图识字：代码模式', 'ocr code 代码识别 提取代码', '保留换行和空格，框选后复制', 'text-x-script', ['screen-ocr', '--code']),
    'layout-save': ('保存窗口布局', 'layout 布局 保存记忆', '记住当前应用的显示器和工作区', 'document-save', ['window-layout', '--save']),
    'layout-restore': ('恢复窗口布局', 'layout 布局 恢复记忆', '将已打开窗口恢复到记住的屏幕和工作区', 'view-restore', ['window-layout', '--restore']),
}


def parse_query(raw: str) -> Query:
    stripped = raw.strip()
    if stripped.casefold() in ('?', 'help', '帮助'):
        return Query('help', '')
    # Only complete tokens reserve a mode; names such as github.com/git stay ordinary.
    parts = stripped.split(maxsplit=1)
    if parts and parts[0].casefold() in PREFIXES:
        return Query(PREFIXES[parts[0].casefold()], parts[1] if len(parts) > 1 else '')
    if stripped.startswith('>'):
        return Query('system', stripped[1:].strip())
    return Query('normal', stripped)


def help_results() -> list[Result]:
    return [Result(title, detail, 'fill', target, icon) for title, detail, target, icon in COMMANDS]


def system_results(text: str, *, all_actions=False) -> list[Result]:
    terms = text.casefold().split()
    if not terms and not all_actions:
        return []
    results = []
    for key, (title, keywords, detail, icon, _) in SYSTEM_ACTIONS.items():
        searchable = (title + ' ' + keywords).casefold()
        if not terms or all(term in searchable for term in terms):
            results.append(Result(title, detail + ' · Enter 执行', 'system', key, icon))
    return results


def website(text: str) -> str | None:
    """Recognize HTTP(S) sites without treating ordinary source filenames as URLs."""
    if not text or any(char.isspace() or ord(char) < 32 for char in text):
        return None
    explicit = text.startswith(('http://', 'https://'))
    if '://' in text and not explicit:
        return None
    candidate = text if explicit else 'https://' + text
    try:
        parsed = urlsplit(candidate)
        host = parsed.hostname
        if parsed.scheme not in ('http', 'https') or not host or parsed.username or parsed.password:
            return None
        if parsed.port is not None and not 0 < parsed.port < 65536:
            return None
        if explicit:
            return candidate
        if host == 'localhost':
            return ('http://' + text) if not explicit else candidate
        try:
            ipaddress.ip_address(host)
            return 'http://' + text
        except ValueError:
            pass
        if not re.fullmatch(r'(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}', host):
            return None
        extension = host.rsplit('.', 1)[1].casefold()
        if extension in {'md', 'txt', 'py', 'pyi', 'lua', 'cpp', 'hpp', 'cc', 'rs', 'go', 'json', 'yaml',
                         'yml', 'toml', 'conf', 'pdf', 'docx', 'xlsx', 'pptx', 'png', 'jpg', 'svg', 'zip',
                         'sh', 'log', 'ini', 'js', 'jsx', 'ts', 'tsx', 'html', 'htm', 'css', 'scss',
                         'sass', 'vue', 'svelte', 'java', 'class', 'kt', 'swift', 'sql', 'xml', 'lock'}:
            return None
        return candidate
    except ValueError:
        return None


def search_url(text: str, engine='google') -> str:
    base = 'https://www.bing.com/search?q=' if engine == 'bing' else 'https://www.google.com/search?q='
    return base + quote_plus(text)


def initial_results(query: Query, applications: list[Result]) -> list[Result]:
    if query.mode == 'help':
        return help_results()
    if query.mode == 'system':
        return system_results(query.text, all_actions=True)
    if query.mode in ('google', 'bing'):
        if not query.text:
            return [Result('输入要搜索的内容', HINTS[query.mode], 'info', '', 'system-search')]
        return [Result('搜索：' + query.text, query.mode.capitalize() + ' · Enter 打开浏览器', 'url',
                       search_url(query.text, query.mode), 'web-browser')]
    if query.mode == 'dictionary' and not query.text:
        return [Result('输入一个英文单词', '例如 dict hypothetical · 显示音标、释义和例句', 'info', '', 'accessories-dictionary')]
    if query.mode != 'normal':
        return []
    if not query.text:
        return [Result('全部功能与用法', HINTS['normal'], 'fill', '?', 'help-browser')] + applications[:9]
    from launcher_knowledge import conversion
    converted = conversion(query.text)
    calculated = calculate(query.text) if converted is None else None
    pinned = [result for result in (converted, calculated) if result]
    address = website(query.text)
    if address:
        pinned.append(Result('打开：' + query.text, 'Enter 在默认浏览器中打开', 'url', address, 'web-browser'))
    return pinned + system_results(query.text) + search_applications(query.text, applications)


def needs_background(query: Query) -> bool:
    if query.mode in ('windows', 'clipboard', 'projects', 'tmux', 'snippets'):
        return True
    if query.mode == 'dictionary':
        return bool(query.text)
    return query.mode == 'normal' and (len(query.text) >= 2 or query.text in ('/', '~'))


def background_results(query: Query, cancel=None) -> list[Result]:
    if cancel and cancel.is_set():
        return []
    if query.mode == 'normal':
        return search_files(query.text, cancel)
    if query.mode == 'dictionary':
        from launcher_knowledge import lookup_word
        return lookup_word(query.text, cancel)
    from launcher_context import search_clipboard, search_projects, search_snippets, search_tmux, search_windows
    handlers = {'windows': search_windows, 'clipboard': search_clipboard, 'projects': search_projects,
                'tmux': search_tmux, 'snippets': search_snippets}
    handler = handlers.get(query.mode)
    results = handler(query.text, cancel) if handler else []
    if query.mode == 'snippets':
        results.append(Result('编辑常用文字片段', '设置邮箱、地址和代码模板 · Enter 编辑配置', 'file',
                              str(CONFIG / 'launcher-snippets.json'), 'document-edit'))
    return results


def loading_message(query: Query) -> str:
    return {'windows': '正在查找窗口…', 'clipboard': '正在搜索剪贴板…', 'projects': '正在查找项目…',
            'tmux': '正在读取 tmux 会话…', 'snippets': '正在读取常用片段…',
            'dictionary': '正在查词…'}.get(query.mode, '正在查找文件…')


def run_system_action(key: str):
    if key not in SYSTEM_ACTIONS:
        raise ValueError('未知的系统操作')
    arguments = SYSTEM_ACTIONS[key][4]
    subprocess.Popen([str(CONFIG / 'bin' / arguments[0]), *arguments[1:]],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
