"""Quick Look for Nautilus and the launcher, using the NautilusPreviewer2 API.

Nautilus 46 calls ShowFile(ssb), reads Visible and receives SelectionEvent(u).
The service previews local files only; it never executes source files.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import logging
import mimetypes
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import unquote, urlsplit

CONFIG = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
STATE = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'dotfiles-hyprland'
BUS_NAME = 'org.gnome.NautilusPreviewer'
BUS_PATH = '/org/gnome/NautilusPreviewer'
INTERFACE = 'org.gnome.NautilusPreviewer2'
MAX_TEXT = 1024 * 1024
TEXT_SUFFIXES = {'.py', '.pyi', '.lua', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.c', '.cc',
                 '.cpp', '.h', '.hpp', '.rs', '.go', '.java', '.kt', '.swift', '.sh', '.bash', '.zsh',
                 '.fish', '.conf', '.ini', '.toml', '.yaml', '.yml', '.json', '.xml', '.html', '.css',
                 '.scss', '.sql', '.md', '.rst', '.txt', '.csv', '.log', '.tex', '.desktop', '.service'}

INTROSPECTION = '''<node>
 <interface name="org.gnome.NautilusPreviewer2">
  <method name="ShowFile"><arg type="s" direction="in" name="uri"/>
   <arg type="s" direction="in" name="window_handle"/>
   <arg type="b" direction="in" name="close_if_already_visible"/></method>
  <method name="Close"/>
  <property name="Visible" type="b" access="read"/>
  <signal name="SelectionEvent"><arg type="u" name="direction"/></signal>
 </interface>
 <interface name="org.gnome.NautilusPreviewer">
  <method name="ShowFile"><arg type="s" direction="in" name="uri"/>
   <arg type="i" direction="in" name="xid"/>
   <arg type="b" direction="in" name="close_if_already_visible"/></method>
  <method name="Close"/>
 </interface>
</node>'''


@dataclass(frozen=True)
class FileInfo:
    path: Path
    kind: str
    mime: str
    size: int


def local_path(value: str) -> Path:
    if value.startswith('file:'):
        parsed = urlsplit(value)
        if parsed.scheme != 'file' or parsed.netloc not in ('', 'localhost'):
            raise ValueError('仅支持本机文件预览')
        path = Path(unquote(parsed.path))
    elif '://' in value:
        raise ValueError('远程文件请先下载到本机再预览')
    else:
        path = Path(value).expanduser().absolute()
    if not path.is_absolute() or '\0' in str(path):
        raise ValueError('文件路径无效')
    return path


def inspect_file(value: str | Path) -> FileInfo:
    path = local_path(str(value))
    info = path.stat()
    if path.is_dir():
        return FileInfo(path, 'directory', 'inode/directory', info.st_size)
    if not path.is_file():
        raise ValueError('这个位置不是普通文件')
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    if mime.startswith('image/'):
        kind = 'image'
    elif mime == 'application/pdf' or path.suffix.casefold() == '.pdf':
        kind = 'pdf'
    elif mime.startswith(('video/', 'audio/')):
        kind = 'media'
    elif mime.startswith('text/') or path.suffix.casefold() in TEXT_SUFFIXES or path.name in (
            'Makefile', 'Dockerfile', 'CMakeLists.txt', 'LICENSE', 'README', '.gitignore', '.bashrc'):
        kind = 'text'
    else:
        # Extensionless scripts and small UTF-8 documents should remain readable.
        with path.open('rb') as stream:
            sample = stream.read(4096)
        try:
            sample.decode('utf-8')
            kind = 'text' if sample and b'\0' not in sample else 'metadata'
        except UnicodeDecodeError:
            kind = 'metadata'
    return FileInfo(path, kind, mime, info.st_size)


def read_text(path: Path, limit=MAX_TEXT) -> tuple[str, bool]:
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    truncated = len(data) > limit
    data = data[:limit]
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16', 'replace'), truncated
    if b'\0' in data:
        raise ValueError('这是二进制文件，无法作为文字预览')
    for encoding in ('utf-8-sig', 'gb18030'):
        try:
            return data.decode(encoding), truncated
        except UnicodeError:
            continue
    return data.decode('utf-8', 'replace'), truncated


def directory_summary(path: Path):
    entries = []
    with os.scandir(path) as scan:
        for index, entry in enumerate(scan):
            if index >= 300:
                break
            if not entry.name.startswith('.'):
                entries.append(('📁 ' if entry.is_dir(follow_symlinks=False) else '    ') + entry.name)
    names = sorted(entries, key=str.casefold)
    return '\n'.join(names[:18]) + ('\n…' if len(names) > 18 else '') or '这个文件夹中没有可显示的文件'


def system_program(name):
    # Do not depend on Codex's temporary PATH overrides for desktop features.
    system = Path('/usr/bin') / name
    return str(system) if system.is_file() else shutil.which(name)


def pdf_pages(path):
    program = system_program('pdfinfo')
    if not program:
        return 1
    result = subprocess.run([program, str(path)], capture_output=True, text=True, timeout=4)
    match = re.search(r'^Pages:\s+(\d+)', result.stdout, re.M)
    return max(1, int(match[1])) if match else 1


def render_pdf(path: Path, page: int, destination: Path, cancel=None):
    program = system_program('pdftoppm')
    if not program:
        raise RuntimeError('缺少 PDF 预览工具 pdftoppm')
    process = subprocess.Popen([program, '-f', str(max(1, int(page))), '-singlefile', '-scale-to', '1600',
                                '-png', str(path), str(destination)], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 12
        while process.poll() is None:
            if (cancel and cancel.is_set()) or time.monotonic() >= deadline:
                raise RuntimeError('PDF 预览已取消或超时')
            time.sleep(.03)
        output = destination.with_suffix('.png')
        if process.returncode or not output.is_file():
            raise RuntimeError('PDF 无法预览，可能已加密或损坏')
        return output
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=.3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def install_activation():
    directory = DATA / 'dbus-1/services'
    directory.mkdir(parents=True, exist_ok=True)
    executable = str(CONFIG / 'bin/file-preview').replace('\\', '\\\\').replace('"', '\\"')
    content = '[D-BUS Service]\nName=' + BUS_NAME + '\nExec=/usr/bin/python3 "' + executable + '" --daemon\n'
    path = directory / (BUS_NAME + '.service')
    if path.exists():
        existing = path.read_text()
        if existing != content and 'bin/file-preview" --daemon' not in existing:
            # Respect a preview service the user installed independently (Sushi).
            return path
    if not path.exists() or path.read_text() != content:
        path.write_text(content)
    return path


def gtk_modules():
    os.environ['GDK_BACKEND'] = 'wayland'
    os.environ['GDK_SCALE'] = '1'
    plugins = DATA / 'hypr-preview/root/usr/lib/x86_64-linux-gnu/gstreamer-1.0'
    if plugins.is_dir():
        os.environ['GST_PLUGIN_PATH'] = str(plugins) + ':' + os.environ.get('GST_PLUGIN_PATH', '')
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gdk', '4.0')
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango
    return Gtk, Gdk, GdkPixbuf, Gio, GLib, Pango


def service_type(modules):
    Gtk, Gdk, GdkPixbuf, Gio, GLib, Pango = modules

    class PreviewService(Gtk.Application):
        def __init__(self):
            super().__init__(application_id=BUS_NAME, flags=Gio.ApplicationFlags.IS_SERVICE)
            self.window = None
            self.connection = None
            self.visible = False
            self.current = None
            self.kind = 'metadata'
            self.media = None
            self.generation = 0
            self.page = 1
            self.pages = 1
            self.page_cancel = threading.Event()
            self.cancel = threading.Event()
            self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='file-preview')
            self.storage = tempfile.TemporaryDirectory(prefix='hypr-file-preview-',
                dir=os.environ.get('XDG_RUNTIME_DIR') or None)

        def do_startup(self):
            Gtk.Application.do_startup(self)
            self.hold()

        def do_dbus_register(self, connection, object_path):
            if not Gtk.Application.do_dbus_register(self, connection, object_path):
                return False
            self.connection = connection
            node = Gio.DBusNodeInfo.new_for_xml(INTROSPECTION)
            self.registrations = [connection.register_object(BUS_PATH, interface, self.method,
                                  self.property_value, None) for interface in node.interfaces]
            return True

        def do_dbus_unregister(self, connection, object_path):
            for identifier in getattr(self, 'registrations', []):
                connection.unregister_object(identifier)
            Gtk.Application.do_dbus_unregister(self, connection, object_path)

        def property_value(self, connection, sender, path, interface, name):
            return GLib.Variant('b', self.visible) if name == 'Visible' else None

        def method(self, connection, sender, path, interface, method, parameters, invocation):
            try:
                if method == 'Close':
                    self.hide()
                elif method == 'ShowFile':
                    uri, handle, toggle = parameters.unpack()
                    self.show_file(uri, toggle)
                invocation.return_value(None)
            except Exception as error:
                invocation.return_dbus_error('org.gnome.NautilusPreviewer.Error', str(error))

        def set_visible_state(self, value):
            if self.visible == value:
                return
            self.visible = value
            if self.connection:
                self.connection.emit_signal(None, BUS_PATH, 'org.freedesktop.DBus.Properties',
                    'PropertiesChanged', GLib.Variant('(sa{sv}as)',
                    (INTERFACE, {'Visible': GLib.Variant('b', value)}, [])))

        def build(self):
            from theme_palette import recolor
            css = '''window.file-preview { background: #1a1b26; color: #c0caf5; }
                .preview-title { font-size: 18px; font-weight: 600; }
                .preview-status { color: #9aa5ce; font-size: 12px; }
                .preview-content { background: #16161e; border-radius: 12px; }
                .preview-content textview, .preview-content textview text { background: #16161e; color: #c0caf5; }
                button { color: #c0caf5; background: #24283b; border: 1px solid #414868; border-radius: 8px; padding: 7px 12px; }
                button:hover { background: #303751; }'''
            provider = Gtk.CssProvider()
            provider.load_from_data(recolor(css).encode())
            Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider,
                                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.window = Gtk.ApplicationWindow(application=self)
            self.window.set_title('文件预览')
            self.window.add_css_class('file-preview')
            self.window.set_default_size(1000, 740)
            self.window.connect('close-request', lambda *_: self.hide() or True)
            controller = Gtk.EventControllerKey()
            controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
            controller.connect('key-pressed', self.key)
            self.window.add_controller(controller)
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            for edge in ('top', 'bottom', 'start', 'end'):
                getattr(container, 'set_margin_' + edge)(16)
            self.window.set_child(container)
            header = Gtk.Box(spacing=12)
            self.heading = Gtk.Label(xalign=0, hexpand=True)
            self.heading.add_css_class('preview-title')
            self.heading.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            header.append(self.heading)
            opener = Gtk.Button(label='打开文件 ↵')
            opener.connect('clicked', lambda *_: self.open_default())
            header.append(opener)
            closer = Gtk.Button.new_from_icon_name('window-close-symbolic')
            closer.connect('clicked', lambda *_: self.hide())
            header.append(closer)
            container.append(header)
            self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True)
            self.content.add_css_class('preview-content')
            container.append(self.content)
            self.status = Gtk.Label(xalign=0)
            self.status.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            self.status.add_css_class('preview-status')
            container.append(self.status)

        def clear(self):
            if self.media:
                self.media.pause()
                self.media = None
            child = self.content.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self.content.remove(child)
                child = next_child

        def message(self, text):
            self.clear()
            label = Gtk.Label(label=text, wrap=True, vexpand=True, hexpand=True)
            self.content.append(label)

        def show_file(self, uri, toggle=False):
            path = local_path(uri)
            if toggle and self.visible and self.current == path:
                self.hide()
                return
            if self.window is None:
                self.build()
            self.cancel.set()
            self.page_cancel.set()
            self.cancel = threading.Event()
            self.page_cancel = threading.Event()
            self.generation += 1
            generation, cancel = self.generation, self.cancel
            self.current = path
            self.kind = 'metadata'
            # Generation-specific output cannot collide with a previous render.
            request_dir = Path(self.storage.name) / str(generation)
            request_dir.mkdir()
            self.request_dir = request_dir
            self.page = self.pages = 1
            self.heading.set_text(path.name or str(path))
            self.heading.set_tooltip_text(str(path))
            self.window.set_title('文件预览 · ' + (path.name or str(path)))
            self.status.set_text('正在读取文件…  ·  Space / Esc 关闭  ·  Enter 打开')
            self.message('正在载入预览…')
            self.set_visible_state(True)
            self.window.present()
            def prepare():
                info = inspect_file(path)
                extra = read_text(path) if info.kind == 'text' else None
                if info.kind == 'pdf':
                    extra = (pdf_pages(path), render_pdf(path, 1, request_dir / '1', cancel))
                if info.kind == 'image':
                    extra = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), 1800, 1300, True)
                if info.kind == 'directory':
                    extra = directory_summary(path)
                return info, extra
            self.submit(prepare, self.loaded, generation, cancel)

        def submit(self, work, callback, generation, cancel):
            future = self.pool.submit(work)
            def finished(task):
                try:
                    payload, error = task.result(), None
                except Exception as exception:
                    payload, error = None, str(exception)
                if not cancel.is_set():
                    GLib.idle_add(callback, generation, payload, error)
            future.add_done_callback(finished)

        def loaded(self, generation, payload, error):
            if generation != self.generation or not self.visible:
                return False
            if error:
                self.message('无法预览：' + error)
                self.status.set_text('Enter 用默认程序打开  ·  Space / Esc 关闭')
                return False
            info, extra = payload
            self.kind = info.kind
            self.clear()
            self.status.set_text(f'{info.mime}  ·  {info.size:,} 字节  ·  Space / Esc 关闭  ·  Enter 打开')
            if info.kind == 'image':
                picture = Gtk.Picture.new_for_paintable(Gdk.Texture.new_for_pixbuf(extra))
                picture.set_can_shrink(True)
                picture.set_content_fit(Gtk.ContentFit.CONTAIN)
                picture.set_vexpand(True)
                self.content.append(picture)
            elif info.kind == 'pdf':
                self.pages, image = extra
                self.pdf_picture = Gtk.Picture.new_for_filename(str(image))
                self.pdf_picture.set_can_shrink(True)
                self.pdf_picture.set_content_fit(Gtk.ContentFit.CONTAIN)
                self.pdf_picture.set_vexpand(True)
                self.content.append(self.pdf_picture)
                self.pdf_status()
            elif info.kind == 'text':
                text, truncated = extra
                viewer = Gtk.TextView(editable=False, cursor_visible=False, monospace=True)
                viewer.set_wrap_mode(Gtk.WrapMode.NONE)
                viewer.set_left_margin(16)
                viewer.set_right_margin(16)
                viewer.set_top_margin(12)
                viewer.set_bottom_margin(12)
                viewer.get_buffer().set_text(text)
                scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
                scroll.set_child(viewer)
                self.content.append(scroll)
                if truncated:
                    self.status.set_text('仅预览前 1 MiB，完整内容请按 Enter 打开  ·  Space / Esc 关闭')
            elif info.kind == 'media':
                self.media = Gtk.MediaFile.new_for_filename(str(info.path))
                self.media.connect('notify::error', self.media_error, generation)
                video = Gtk.Video(media_stream=self.media, vexpand=True, hexpand=True)
                self.content.append(video)
                self.media.play()
            else:
                self.message(extra if info.kind == 'directory' else '此文件暂无内嵌预览\n按 Enter 用默认程序打开')
            # Old requests have been cancelled; keep only this file's page cache.
            self.pool.submit(self.cleanup_old, self.request_dir)
            return False

        def cleanup_old(self, keep):
            # A cancelled renderer notices within 30ms; delay cleanup off the UI.
            time.sleep(.4)
            root = Path(self.storage.name)
            if root.is_dir():
                for directory in root.iterdir():
                    if directory.is_dir() and directory.name.isdecimal() and int(directory.name) < int(keep.name):
                        shutil.rmtree(directory, ignore_errors=True)

        def media_error(self, media, _, generation):
            error = media.get_error()
            if error and generation == self.generation:
                self.message('无法播放：' + error.message + '\n按 Enter 用默认播放器打开')

        def pdf_status(self):
            self.status.set_text(f'PDF  第 {self.page} / {self.pages} 页  ·  ← → 翻页  ·  Space / Esc 关闭  ·  Enter 打开')

        def turn_page(self, step):
            page = max(1, min(self.pages, self.page + step))
            if page == self.page:
                return
            self.page = page
            self.page_cancel.set()
            self.page_cancel = threading.Event()
            self.pdf_status()
            self.status.set_text(self.status.get_text() + '  ·  正在渲染…')
            generation, cancel = self.generation, self.page_cancel
            path = self.current
            request_dir = self.request_dir
            def ready(token, image, error):
                if token == self.generation and self.visible and self.page == page:
                    if error:
                        self.status.set_text('翻页失败：' + error)
                    else:
                        self.pdf_picture.set_filename(str(image))
                        self.pdf_status()
                return False
            def render():
                output = request_dir / f'{page}.png'
                if output.is_file():
                    return output
                # Even revisiting a page while its old task stops cannot share output.
                destination = request_dir / f'{page}-{time.monotonic_ns()}'
                rendered = render_pdf(path, page, destination, cancel)
                if cancel.is_set():
                    rendered.unlink(missing_ok=True)
                    raise RuntimeError('翻页已取消')
                rendered.replace(output)
                return output
            self.submit(render,
                        ready, generation, cancel)

        def key(self, controller, keyval, keycode, state):
            if keyval in (Gdk.KEY_Escape, Gdk.KEY_space):
                self.hide()
                return True
            if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                self.open_default()
                return True
            if self.kind == 'pdf' and keyval in (Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Page_Up, Gdk.KEY_Page_Down):
                self.turn_page(-1 if keyval in (Gdk.KEY_Left, Gdk.KEY_Page_Up) else 1)
                return True
            if self.kind != 'text' and keyval in (Gdk.KEY_Up, Gdk.KEY_Down):
                direction = 2 if keyval == Gdk.KEY_Up else 3
                self.connection.emit_signal(None, BUS_PATH, INTERFACE, 'SelectionEvent', GLib.Variant('(u)', (direction,)))
                return True
            return False

        def open_default(self):
            if self.current:
                try:
                    Gio.AppInfo.launch_default_for_uri(self.current.as_uri(), None)
                    self.hide()
                except GLib.Error as error:
                    self.status.set_text('打开失败：' + error.message)

        def hide(self):
            self.cancel.set()
            self.page_cancel.set()
            self.generation += 1
            self.pool.submit(self.cleanup_old, Path(self.storage.name) / str(self.generation))
            if self.media:
                self.media.pause()
                self.media = None
            if self.window:
                self.window.hide()
            self.set_visible_state(False)
            return False

        def stop(self):
            self.hide()
            self.pool.shutdown(wait=False, cancel_futures=True)
            self.quit()
            return False

    return PreviewService


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', help='local path or file:// URI')
    parser.add_argument('--daemon', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--start', action='store_true', help='register and start the Nautilus preview service')
    parser.add_argument('--close', action='store_true', help='close the visible preview')
    parser.add_argument('--inspect', action='store_true', help='print file metadata without opening a window')
    args = parser.parse_args(argv)
    if args.inspect:
        if not args.path:
            parser.error('--inspect requires a path')
        info = inspect_file(args.path)
        print(json.dumps({'path': str(info.path), 'kind': info.kind, 'mime': info.mime, 'size': info.size}, ensure_ascii=False))
        return 0
    os.umask(0o077)
    if args.daemon:
        STATE.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=str(STATE / 'file-preview.log'), level=logging.WARNING)
        modules = gtk_modules()
        app = service_type(modules)()
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: modules[4].idle_add(app.stop))
        return app.run([sys.argv[0]])
    if not args.path and not args.start and not args.close:
        parser.print_help()
        return 0
    install_activation()
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio, GLib
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        if args.close:
            bus.call_sync(BUS_NAME, BUS_PATH, INTERFACE, 'Close', None, None,
                          Gio.DBusCallFlags.NO_AUTO_START, 2000, None)
        elif args.path:
            uri = local_path(args.path).as_uri()
            bus.call_sync(BUS_NAME, BUS_PATH, INTERFACE, 'ShowFile', GLib.Variant('(ssb)', (uri, '', False)),
                          None, Gio.DBusCallFlags.NONE, 5000, None)
        else:
            bus.call_sync('org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus',
                          'StartServiceByName', GLib.Variant('(su)', (BUS_NAME, 0)), None,
                          Gio.DBusCallFlags.NONE, 5000, None)
    except (GLib.Error, OSError, ValueError) as error:
        print('文件预览未完成：' + str(error), file=sys.stderr)
        return 1
    return 0
