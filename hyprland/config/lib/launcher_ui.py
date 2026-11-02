"""A session-scoped, on-demand Wayland launcher using the desktop palette."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import fcntl
import hashlib
import json
import logging
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading

from launcher_search import Result, load_applications
from launcher_features import (HINTS, background_results, initial_results, loading_message,
                               needs_background, parse_query, run_system_action)
from theme_palette import recolor, selected_palette

CONFIG = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
STATE = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'dotfiles-hyprland'
SESSION = hashlib.sha256(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE', 'default').encode()).hexdigest()[:12]
LOCK = Path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid()))) / ('hypr-launcher-' + SESSION + '.lock')

CSS = '''
#desktop-launcher { background: transparent; color: #c0caf5; font-family: "Noto Sans CJK SC", sans-serif; font-size: 15px; }
#launcher-backdrop { background: rgba(8, 12, 22, 0.18); }
#launcher-card { background: #1a1b26; border: 1px solid #414868; border-radius: 20px; padding: 20px; }
#desktop-launcher .heading { color: #bb9af7; font-size: 13px; font-weight: 600; }
#desktop-launcher .caption { color: #9aa5ce; font-size: 12px; }
#desktop-launcher entry { background: #24283b; background-image: none; color: #c0caf5; border: 1px solid #414868; border-radius: 12px; padding: 13px 15px; font-size: 22px; box-shadow: none; min-height: 32px; caret-color: #7aa2f7; }
#desktop-launcher entry:focus { border-color: #7aa2f7; }
#desktop-launcher entry selection { background: #414868; }
#desktop-launcher list, #desktop-launcher scrolledwindow, #desktop-launcher viewport { background: transparent; border: none; }
#desktop-launcher row { background: transparent; border: 1px solid transparent; border-radius: 10px; margin: 2px 0; padding: 9px 12px; }
#desktop-launcher row:hover { background: #24283b; }
#desktop-launcher row:selected { background: #303751; border-color: #7aa2f7; }
#desktop-launcher .result-title { color: #c0caf5; font-size: 17px; }
#desktop-launcher .result-detail { color: #9aa5ce; font-size: 12px; }
#desktop-launcher .calculation { color: #7dcfff; font-size: 27px; font-weight: 600; }
#desktop-launcher separator { background: #414868; min-height: 1px; }
#desktop-launcher scrollbar { background: transparent; }
#desktop-launcher scrollbar slider { background: #414868; min-width: 4px; border-radius: 3px; }
'''


def gtk_modules():
    os.environ['GDK_BACKEND'] = 'wayland'
    os.environ['GDK_SCALE'] = '1'
    # Same private typelib fallback as the existing desktop panel/overview.
    private = DATA / 'hypr-motion/gtk-layer/usr/lib/x86_64-linux-gnu/girepository-1.0'
    if private.is_dir():
        os.environ['GI_TYPELIB_PATH'] = str(private) + ':' + os.environ.get('GI_TYPELIB_PATH', '')
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import Gdk, Gio, GLib, Gtk, GtkLayerShell, Pango
    return Gtk, Gdk, Gio, GLib, GtkLayerShell, Pango


def close_existing(lock):
    try:
        lock.seek(0)
        pid = int(lock.read().strip())
        command = Path('/proc', str(pid), 'cmdline').read_bytes().split(b'\0')
        if any(Path(os.fsdecode(part)).name == 'launcher' for part in command if part):
            os.kill(pid, signal.SIGUSR1)
    except (OSError, ValueError):
        pass


class Launcher:
    def __init__(self, modules=None):
        self.Gtk, self.Gdk, self.Gio, self.GLib, self.Layer, self.Pango = modules or gtk_modules()
        Gtk, Gdk, Layer = self.Gtk, self.Gdk, self.Layer
        self.alive = True
        self.generation = 0
        self.timer = 0
        self.cancel = threading.Event()
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='launcher-search')
        self.dictionary_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='launcher-dictionary')
        self.future = None
        self.applications = load_applications()
        self.immediate = []
        self.results = []
        self.preedit = ''
        self.css_provider = Gtk.CssProvider()
        palette = selected_palette()
        css = recolor(CSS, palette)
        css += '\n#desktop-launcher entry selection { color: ' + palette['colors']['fg'] + '; }\n'
        self.css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider,
                                                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title('桌面搜索')
        self.window.set_name('desktop-launcher')
        self.window.set_decorated(False)
        self.window.set_app_paintable(True)
        visual = self.window.get_screen().get_rgba_visual()
        if visual:
            self.window.set_visual(visual)
        Layer.init_for_window(self.window)
        Layer.set_namespace(self.window, 'desktop-launcher')
        Layer.set_layer(self.window, Layer.Layer.OVERLAY)
        Layer.set_exclusive_zone(self.window, -1)
        Layer.set_keyboard_mode(self.window, Layer.KeyboardMode.EXCLUSIVE)
        for edge in (Layer.Edge.TOP, Layer.Edge.BOTTOM, Layer.Edge.LEFT, Layer.Edge.RIGHT):
            Layer.set_anchor(self.window, edge, True)
        monitor = self.focused_monitor()
        Layer.set_monitor(self.window, monitor)
        geometry = monitor.get_geometry()
        backdrop = Gtk.EventBox()
        backdrop.set_name('launcher-backdrop')
        backdrop.connect('button-press-event', self.outside_click)
        self.window.add(backdrop)
        alignment = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        backdrop.add(alignment)
        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.card.set_name('launcher-card')
        self.card.set_halign(Gtk.Align.CENTER)
        self.card.set_valign(Gtk.Align.START)
        self.card.set_size_request(min(780, geometry.width - 64), -1)
        self.card.set_margin_top(max(32, min(190, int(geometry.height * .13))))
        alignment.pack_start(self.card, False, False, 0)
        header = Gtk.Box(spacing=12)
        header.pack_start(self.label('桌面搜索', 'heading'), True, True, 0)
        header.pack_end(self.label('应用  ·  文件  ·  计算  ·  ? 更多功能', 'caption'), False, False, 0)
        self.card.pack_start(header, False, False, 0)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('搜索应用、文件，输入算式，或 ? 查看全部功能…')
        self.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'system-search-symbolic')
        self.entry.connect('changed', self.changed)
        self.entry.connect('preedit-changed', self.preedit_changed)
        self.entry.connect('activate', lambda *_: self.activate())
        self.card.pack_start(self.entry, False, False, 0)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.results_height = max(190, min(455, geometry.height - 380))
        self.scroll.set_size_request(-1, self.results_height)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_activate_on_single_click(True)
        self.listbox.connect('row-activated', lambda _, row: self.activate(row))
        self.listbox.connect('row-selected', self.selected)
        self.scroll.add(self.listbox)
        self.card.pack_start(self.scroll, True, True, 0)
        self.hint = self.label(HINTS['normal'], 'caption')
        self.hint.set_max_width_chars(90)
        self.card.pack_start(self.hint, False, False, 0)
        self.card.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)
        footer = Gtk.Box(spacing=16)
        self.status = self.label('输入名称查找应用和文件', 'caption')
        footer.pack_start(self.status, True, True, 0)
        footer.pack_end(self.label('↑↓ 选择   Enter 打开 / 复制   Esc 关闭', 'caption'), False, False, 0)
        self.card.pack_start(footer, False, False, 0)
        self.window.connect('key-press-event', self.key)
        self.window.connect('delete-event', lambda *_: self.close() or True)

    def label(self, text, style=None):
        label = self.Gtk.Label(label=text)
        label.set_xalign(0)
        label.set_ellipsize(self.Pango.EllipsizeMode.END)
        if style:
            label.get_style_context().add_class(style)
        return label

    def focused_monitor(self):
        display = self.Gdk.Display.get_default()
        try:
            result = subprocess.run(['hyprctl', '-j', 'monitors'], capture_output=True, text=True, timeout=1)
            metadata = next(m for m in json.loads(result.stdout) if m.get('focused'))
            for index in range(display.get_n_monitors()):
                monitor = display.get_monitor(index)
                geometry = monitor.get_geometry()
                if geometry.x == metadata['x'] and geometry.y == metadata['y']:
                    return monitor
        except (OSError, ValueError, StopIteration, subprocess.SubprocessError):
            pass
        return display.get_monitor(0)

    def show(self, text=''):
        self.window.show_all()
        self.window.present()
        self.entry.grab_focus()
        self.entry.set_text(text)
        if not text:
            self.changed(self.entry)
        self.entry.set_position(-1)

    def preedit_changed(self, _, text):
        self.preedit = text

    def outside_click(self, *_):
        x, y = self.window.get_pointer()
        origin = self.card.translate_coordinates(self.window, 0, 0)
        allocation = self.card.get_allocation()
        if origin and not (origin[0] <= x < origin[0] + allocation.width
                           and origin[1] <= y < origin[1] + allocation.height):
            self.close()
            return True
        return False

    def changed(self, *_):
        self.generation += 1
        self.cancel.set()
        self.cancel = threading.Event()
        if self.timer:
            self.GLib.source_remove(self.timer)
            self.timer = 0
        if self.future:
            self.future.cancel()
        query = parse_query(self.entry.get_text())
        self.hint.set_text(HINTS.get(query.mode, HINTS['normal']))
        self.immediate = initial_results(query, self.applications)
        self.render(self.immediate)
        if needs_background(query):
            self.status.set_text(loading_message(query))
            if query.mode == 'dictionary':
                self.render([Result('正在查词：' + query.text, '读取本地缓存或在线词典…', 'info', '', 'accessories-dictionary')])
            delay = 450 if query.mode == 'dictionary' else 120
            self.timer = self.GLib.timeout_add(delay, self.begin_search, query, self.generation, self.cancel)
        elif self.results:
            self.update_status()
        elif query.mode == 'normal' and query.text:
            self.status.set_text('文件名至少输入 2 个字符 · ? 查看全部功能')
        else:
            self.status.set_text('没有找到结果')

    def begin_search(self, query, generation, cancel):
        self.timer = 0
        pool = self.dictionary_pool if query.mode == 'dictionary' else self.pool
        future = pool.submit(background_results, query, cancel)
        self.future = future
        def finished(task):
            try:
                if task.cancelled():
                    return
                results = task.result()
            except Exception:
                logging.exception('Launcher search failed (%s)', query.mode)
                results = [Result('暂时无法读取结果', '请重试，或查看 launcher.log', 'error', '', 'dialog-warning')]
            if self.alive and not cancel.is_set():
                self.GLib.idle_add(self.show_results, generation, results)
        future.add_done_callback(finished)
        return False

    def show_results(self, generation, results):
        if self.alive and self.generation == generation:
            self.render(self.immediate + results)
            if not self.results:
                self.status.set_text('没有找到结果 · ? 查看全部功能')
            else:
                self.update_status()
        return False

    def render(self, results):
        previous = self.listbox.get_selected_row()
        target = getattr(previous, 'result', None)
        for row in self.listbox.get_children():
            row.destroy()
        self.results = results
        self.scroll.set_size_request(-1, min(self.results_height, max(100, len(results) * 82)))
        selected = None
        for result in results:
            row = self.Gtk.ListBoxRow()
            row.result = result
            row.set_can_focus(False)
            line = self.Gtk.Box(spacing=14)
            icon_name = result.icon or {
                'calculator': 'accessories-calculator', 'application': 'application-x-executable',
                'file': 'text-x-generic', 'directory': 'folder', 'error': 'dialog-warning-symbolic',
                'definition': 'accessories-dictionary', 'conversion': 'accessories-calculator',
                'window': 'preferences-system-windows', 'clipboard': 'edit-paste',
                'project': 'folder-development', 'tmux': 'utilities-terminal',
                'snippet': 'edit-copy', 'url': 'web-browser', 'fill': 'help-browser',
            }.get(result.kind, 'system-search-symbolic')
            try:
                icon = self.Gtk.Image.new_from_gicon(self.Gio.Icon.new_for_string(icon_name), self.Gtk.IconSize.DIALOG)
            except self.GLib.Error:
                icon = self.Gtk.Image.new_from_icon_name('application-x-executable', self.Gtk.IconSize.DIALOG)
            icon.set_pixel_size(32)
            line.pack_start(icon, False, False, 0)
            labels = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=3)
            title = self.label(result.title, 'calculation' if result.kind == 'calculator' else 'result-title')
            title.set_max_width_chars(55)
            if result.kind == 'definition':
                title.set_ellipsize(self.Pango.EllipsizeMode.NONE)
                title.set_line_wrap(True)
                title.set_line_wrap_mode(self.Pango.WrapMode.WORD_CHAR)
            labels.pack_start(title, False, False, 0)
            detail = self.label(result.subtitle, 'result-detail')
            detail.set_max_width_chars(75)
            if result.kind == 'definition':
                detail.set_ellipsize(self.Pango.EllipsizeMode.NONE)
                detail.set_line_wrap(True)
                detail.set_line_wrap_mode(self.Pango.WrapMode.WORD_CHAR)
            labels.pack_start(detail, False, False, 0)
            line.pack_start(labels, True, True, 0)
            row.add(line)
            if result.kind not in ('clipboard', 'snippet'):
                row.set_tooltip_text(result.title + '\n' + result.subtitle)
            self.listbox.add(row)
            if result == target:
                selected = row
        self.listbox.show_all()
        first = self.listbox.get_row_at_index(0)
        if first:
            self.listbox.select_row(selected or first)

    def selected(self, _, row):
        if row and self.alive:
            self.update_status(row)
            self.GLib.idle_add(self.ensure_visible, row)

    def update_status(self, row=None):
        row = row or self.listbox.get_selected_row()
        kind = row.result.kind if row else ''
        self.status.set_text({'calculator': '按 Enter 复制计算结果',
                              'file': 'Alt+P 预览 · Ctrl+Enter 所在文件夹',
                              'directory': 'Ctrl+Enter 打开上级文件夹',
                              'application': '按 Enter 启动应用',
                              'fill': '按 Enter 进入此功能',
                              'url': '按 Enter 在浏览器中打开',
                              'definition': '按 Enter 复制选中的释义或例句',
                              'conversion': '按 Enter 复制换算结果',
                              'window': '按 Enter 切换到此窗口',
                              'clipboard': '按 Enter 复制这条剪贴板记录',
                              'project': 'Enter 用 Neovide 打开 · Ctrl+Enter 文件夹',
                              'tmux': '按 Enter 连接会话，没有时创建',
                              'snippet': '按 Enter 复制文字片段',
                              'system': '按 Enter 执行所选操作',
                              'info': '请继续输入，或等待查询结果',
                              'error': '请修改输入或选择其他结果'}.get(kind, '↑↓ 选择后按 Enter'))

    def ensure_visible(self, row):
        if row.get_parent() is self.listbox:
            allocation = row.get_allocation()
            adjustment = self.scroll.get_vadjustment()
            bottom = allocation.y + allocation.height
            if allocation.y < adjustment.get_value():
                adjustment.set_value(allocation.y)
            elif bottom > adjustment.get_value() + adjustment.get_page_size():
                adjustment.set_value(bottom - adjustment.get_page_size())
        return False

    def key(self, _, event):
        Gdk = self.Gdk
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        if event.keyval == Gdk.KEY_space and event.state & Gdk.ModifierType.SUPER_MASK:
            self.close()
            return True
        if self.preedit:
            return False
        if event.keyval in (Gdk.KEY_p, Gdk.KEY_P) and event.state & Gdk.ModifierType.MOD1_MASK:
            self.preview_selected()
            return True
        if event.keyval in (Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Page_Up, Gdk.KEY_Page_Down):
            current = self.listbox.get_selected_row()
            index = current.get_index() if current else 0
            step = -1 if event.keyval in (Gdk.KEY_Up, Gdk.KEY_Page_Up) else 1
            if event.keyval in (Gdk.KEY_Page_Up, Gdk.KEY_Page_Down):
                step *= 6
            row = self.listbox.get_row_at_index(max(0, min(len(self.results) - 1, index + step)))
            if row:
                self.listbox.select_row(row)
            return True
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.activate(parent=bool(event.state & Gdk.ModifierType.CONTROL_MASK))
            return True
        return False

    def preview_selected(self):
        row = self.listbox.get_selected_row()
        if not row or row.result.kind not in ('file', 'directory', 'project'):
            self.status.set_text('先选中一个文件，再按 Alt+P 预览')
            return
        try:
            self.window.hide()
            subprocess.Popen([str(CONFIG / 'bin/file-preview'), row.result.target],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
            self.close()
        except OSError as error:
            self.window.show_all()
            self.entry.grab_focus()
            self.status.set_text('预览失败：' + str(error)[:80])

    def activate(self, row=None, parent=False):
        row = row or self.listbox.get_selected_row()
        if row is None or row.result.kind in ('error', 'info'):
            return
        result = row.result
        try:
            if result.kind == 'fill':
                self.entry.set_text(result.target)
                self.entry.grab_focus()
                self.entry.set_position(-1)
                return
            if result.kind in ('calculator', 'conversion', 'definition', 'snippet'):
                subprocess.run(['wl-copy'], input=result.target.encode(), check=True, timeout=2,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif result.kind == 'url':
                self.window.hide()
                self.Gio.AppInfo.launch_default_for_uri(result.target, None)
            elif result.kind in ('file', 'directory'):
                path = Path(result.target)
                if parent:
                    path = path.parent
                self.window.hide()
                self.Gio.AppInfo.launch_default_for_uri(path.as_uri(), None)
            elif result.kind == 'system':
                self.window.hide()
                run_system_action(result.target)
            elif result.kind in ('window', 'clipboard', 'project', 'tmux'):
                from launcher_context import activate_window, copy_clipboard, open_project, open_tmux
                self.window.hide()
                if result.kind == 'project' and parent:
                    self.Gio.AppInfo.launch_default_for_uri(Path(result.target).as_uri(), None)
                else:
                    handlers = {'window': activate_window, 'clipboard': copy_clipboard,
                                'project': open_project, 'tmux': open_tmux}
                    handlers[result.kind](result.target)
            else:
                app = self.Gio.DesktopAppInfo.new(result.target)
                if not app:
                    raise RuntimeError('应用入口已不存在')
                self.window.hide()
                app.launch([], self.Gdk.Display.get_default().get_app_launch_context())
            self.close()
        except (OSError, ValueError, RuntimeError, self.GLib.Error, subprocess.SubprocessError) as error:
            logging.exception('Cannot activate launcher result')
            self.window.show_all()
            self.entry.grab_focus()
            self.status.set_text('打开失败：' + str(error)[:80])

    def close(self):
        if not self.alive:
            return False
        self.alive = False
        self.cancel.set()
        if self.timer:
            self.GLib.source_remove(self.timer)
            self.timer = 0
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.dictionary_pool.shutdown(wait=False, cancel_futures=True)
        self.window.hide()
        if self.Gtk.main_level():
            self.Gtk.main_quit()
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', metavar='TEXT', help='print search results as JSON without opening a window')
    parser.add_argument('--text', default='', help='open with an initial query')
    parser.add_argument('--close', action='store_true', help='close an existing search window')
    args = parser.parse_args()
    if args.query is not None:
        query = parse_query(args.query)
        results = initial_results(query, load_applications())
        if needs_background(query):
            results += background_results(query)
        print(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2))
        return 0
    os.umask(0o077)
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            close_existing(lock)
            return 0
        if args.close:
            return 0
        STATE.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=str(STATE / 'launcher.log'), level=logging.WARNING,
                            format='%(asctime)s %(levelname)s %(message)s')
        try:
            launcher = Launcher()
            for sig in (signal.SIGUSR1, signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, lambda *_: launcher.GLib.idle_add(launcher.close))
            lock.seek(0)
            lock.truncate()
            lock.write(str(os.getpid()))
            lock.flush()
            launcher.show(args.text)
            launcher.Gtk.main()
        except Exception as error:
            logging.exception('Cannot start desktop launcher')
            print('启动搜索失败：' + str(error), file=sys.stderr)
            return 1
    return 0
