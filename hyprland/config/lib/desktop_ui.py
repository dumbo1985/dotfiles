"""Session-local GTK companion panel and volume/brightness OSD."""
from __future__ import annotations

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time

from theme_palette import recolor, selected_palette, selection_text
from weather_status import get_weather, panel_summary

sys.dont_write_bytecode = True
CONFIG = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
SESSION = hashlib.sha256(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE', 'default').encode()).hexdigest()[:12]
RUNTIME = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')) / ('hypr-desktop-' + SESSION)
SOCKET = RUNTIME / 'control.sock'
os.environ['PATH'] = str(DATA / 'hypr-theme/bin') + ':' + os.environ.get('PATH', '/usr/bin:/bin')


def run(arguments, timeout=2):
    return subprocess.run(arguments, capture_output=True, text=True, timeout=timeout)


def output(arguments, timeout=2):
    try:
        result = run(arguments, timeout)
        return result.stdout.strip() if result.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def launch(arguments):
    subprocess.Popen([str(a) for a in arguments], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def focused_monitor():
    try:
        monitors = json.loads(output(['hyprctl', 'monitors', '-j']))
        return next((m for m in monitors if m.get('focused')), monitors[0])
    except (ValueError, IndexError):
        return None


def send(payload):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(.5)
        connection.connect(str(SOCKET))
        connection.sendall(json.dumps(payload).encode() + b'\n')
        if connection.recv(32) != b'ok\n':
            raise RuntimeError('Desktop service rejected command')


def start_service():
    RUNTIME.mkdir(parents=True, mode=0o700, exist_ok=True)
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'dotfiles-hyprland'
    state.mkdir(parents=True, exist_ok=True)
    command = shlex.join(['/usr/bin/python3', '-u', str(CONFIG / 'bin/desktop-panel'), '--daemon'])
    command += ' >' + shlex.quote(str(state / 'desktop-panel.log')) + ' 2>&1'
    result = run(['hyprctl', 'eval', 'hl.exec_cmd(' + json.dumps(command) + ')'])
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    for _ in range(35):
        time.sleep(.05)
        try:
            send({'action': 'ping'})
            return
        except (OSError, RuntimeError):
            pass
    raise RuntimeError('Desktop panel did not start; check desktop-panel.log')


def main(kind='panel'):
    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon', action='store_true')
    parser.add_argument('--start', action='store_true')
    parser.add_argument('--close', action='store_true')
    parser.add_argument('--restart', action='store_true')
    parser.add_argument('--quit', action='store_true')
    parser.add_argument('category', nargs='?', choices=['volume', 'brightness'])
    parser.add_argument('operation', nargs='?', choices=['up', 'down', 'mute', 'show'], default='show')
    args = parser.parse_args()
    if args.daemon:
        daemon()
        return
    if args.restart:
        try:
            send({'action': 'quit'})
            for _ in range(35):
                time.sleep(.05)
                if not SOCKET.exists():
                    break
        except (OSError, RuntimeError):
            pass
    if kind == 'osd':
        if not args.category:
            parser.error('usage: osd volume|brightness up|down|mute|show')
        if args.category == 'brightness' and args.operation == 'mute':
            parser.error('brightness supports up, down and show')
        payload = {'action': 'osd', 'category': args.category, 'operation': args.operation}
    else:
        payload = {'action': 'quit' if args.quit else ('close' if args.close else ('ping' if args.start or args.restart else 'panel'))}
    try:
        send(payload)
    except (OSError, RuntimeError):
        if args.quit or args.close:
            return
        start_service()
        send(payload)


CSS = '''
#desktop-panel { background: transparent; color: #c0caf5; font-family: "Noto Sans CJK SC", sans-serif; font-size: 14px; }
#desktop-panel .panel { background: #161925; border: 1px solid #414868; border-radius: 20px; padding: 22px; }
#desktop-panel .heading { color: #c0caf5; font-size: 26px; font-weight: 600; }
#desktop-panel .caption { color: #9aa5ce; font-size: 12px; }
#desktop-panel .section { background: #202437; border: 1px solid #303751; border-radius: 13px; padding: 13px; }
#desktop-panel button { background: #282e45; background-image: none; color: #c0caf5; border: 1px solid #414868; border-radius: 10px; padding: 9px 12px; box-shadow: none; text-shadow: none; }
#desktop-panel button:hover { background: #343c5b; border-color: #7aa2f7; }
#desktop-panel button:focus { border-color: #bb9af7; }
#desktop-panel .accent { color: #7dcfff; }
#desktop-panel calendar { background: transparent; border: none; color: #c0caf5; padding: 6px; }
#desktop-panel calendar:selected { background: #7aa2f7; color: #16161e; border-radius: 5px; }
#desktop-panel calendar.header { background: transparent; color: #bb9af7; }
#desktop-panel calendar.highlight { color: #7dcfff; }
#desktop-panel separator { background: #303751; min-height: 1px; }
#desktop-panel scale trough, #desktop-osd progressbar trough { background: #303751; border: none; border-radius: 8px; min-height: 7px; }
#desktop-panel scale highlight, #desktop-osd progressbar progress { background: #7aa2f7; border: none; border-radius: 8px; min-height: 7px; }
#desktop-panel scale slider { background: #bb9af7; border: none; min-width: 14px; min-height: 14px; }
#desktop-osd { background: transparent; color: #c0caf5; font-family: "Noto Sans CJK SC", sans-serif; font-size: 14px; }
#desktop-osd .osd { background: #161925; border: 1px solid #7aa2f7; border-radius: 18px; padding: 16px 22px; }
#desktop-osd .osd-title { color: #bb9af7; font-size: 16px; }
'''


def daemon():
    os.umask(0o077)
    RUNTIME.mkdir(parents=True, mode=0o700, exist_ok=True)
    lock = open(RUNTIME / 'daemon.lock', 'w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    os.environ['GDK_BACKEND'] = 'wayland'
    os.environ['GDK_SCALE'] = '1'
    os.environ['GI_TYPELIB_PATH'] = str(DATA / 'hypr-motion/gtk-layer/usr/lib/x86_64-linux-gnu/girepository-1.0') + ':' + os.environ.get('GI_TYPELIB_PATH', '')
    import gi
    gi.__path__.append(str(DATA / 'hypr-motion/gtk-cairo/usr/lib/python3/dist-packages/gi'))
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import Gdk, GLib, Gtk, GtkLayerShell, Pango
    service = DesktopService(Gtk, Gdk, GLib, GtkLayerShell, Pango)
    signal.signal(signal.SIGTERM, lambda *_: GLib.idle_add(service.quit))
    signal.signal(signal.SIGINT, lambda *_: GLib.idle_add(service.quit))
    service.run()


class DesktopService:
    def __init__(self, Gtk, Gdk, GLib, Layer, Pango):
        self.Gtk, self.Gdk, self.GLib, self.Layer, self.Pango = Gtk, Gdk, GLib, Layer, Pango
        self.alive = True
        self.worker = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.commands = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.polling = False
        self.generation = 0
        self.osd_generation = 0
        self.osd_timer = None
        self.previous_cpu = None
        self.refreshing_slider = False
        self.slider_timer = None
        self.weather = ''
        self.weather_pending = False
        self.weather_timestamp = 0
        self.theme_css = ''
        self.css_provider = Gtk.CssProvider()
        self.refresh_theme()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.panel = self.window('desktop-panel', Layer.KeyboardMode.EXCLUSIVE)
        Layer.set_anchor(self.panel, Layer.Edge.TOP, True)
        Layer.set_anchor(self.panel, Layer.Edge.RIGHT, True)
        Layer.set_margin(self.panel, Layer.Edge.TOP, 64)
        Layer.set_margin(self.panel, Layer.Edge.RIGHT, 18)
        self.panel.set_size_request(420, -1)
        self.panel.connect('key-press-event', self.key)
        self.panel.connect('delete-event', lambda *_: self.hide_panel() or True)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        outer.get_style_context().add_class('panel')
        self.panel.add(outer)
        row = Gtk.Box(spacing=12)
        self.clock = self.label('', 'heading')
        row.pack_start(self.clock, True, True, 0)
        close = self.button('×', self.hide_panel)
        close.set_tooltip_text('关闭面板 · Esc')
        row.pack_end(close, False, False, 0)
        outer.pack_start(row, False, False, 0)
        self.date = self.label('', 'caption')
        outer.pack_start(self.date, False, False, 0)
        self.calendar = Gtk.Calendar()
        self.calendar.set_display_options(Gtk.CalendarDisplayOptions.SHOW_HEADING | Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES)
        outer.pack_start(self.calendar, False, False, 0)
        self.weather_label = self.label('', 'caption')
        self.weather_label.set_no_show_all(True)
        outer.pack_start(self.weather_label, False, False, 0)
        stats = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        stats.get_style_context().add_class('section')
        stats.pack_start(self.label('系统状态', 'accent'), False, False, 0)
        self.stats = self.label('正在读取…')
        stats.pack_start(self.stats, False, False, 0)
        self.temps = self.label('', 'caption')
        stats.pack_start(self.temps, False, False, 0)
        outer.pack_start(stats, False, False, 0)
        media = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        media.get_style_context().add_class('section')
        self.media_title = self.label('没有正在播放的媒体')
        media.pack_start(self.media_title, False, False, 0)
        self.media_artist = self.label('', 'caption')
        media.pack_start(self.media_artist, False, False, 0)
        controls = Gtk.Box(spacing=8)
        for title, action in [('上一首', 'previous'), ('播放 / 暂停', 'play-pause'), ('下一首', 'next')]:
            controls.pack_start(self.button(title, lambda action=action: self.command(['playerctl', action])), True, True, 0)
        media.pack_start(controls, False, False, 0)
        self.media_controls = controls
        outer.pack_start(media, False, False, 0)
        audio = Gtk.Box(spacing=10)
        self.volume_label = self.label('音量')
        audio.pack_start(self.volume_label, False, False, 0)
        self.volume = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume.set_draw_value(False)
        self.volume.set_hexpand(True)
        self.volume.connect('value-changed', self.slider_changed)
        audio.pack_start(self.volume, True, True, 0)
        audio.pack_start(self.button('静音', lambda: self.osd_request('volume', 'mute')), False, False, 0)
        outer.pack_start(audio, False, False, 0)
        self.network = self.button('网络设置', lambda: self.command(['nm-connection-editor'], hide=True))
        outer.pack_start(self.network, False, False, 0)
        quick = Gtk.Box(spacing=8)
        quick.pack_start(self.button('蓝牙', self.bluetooth), True, True, 0)
        quick.pack_start(self.button('通知', lambda: self.command([CONFIG / 'bin/control-center'], hide=True)), True, True, 0)
        quick.pack_start(self.button('截图', lambda: self.command([CONFIG / 'bin/screenshot'], hide=True)), True, True, 0)
        outer.pack_start(quick, False, False, 0)
        scene = Gtk.Box(spacing=8)
        for label, mode in [('日间', 'day'), ('夜间', 'night'), ('专注', 'focus')]:
            scene.pack_start(self.button(label, lambda mode=mode: self.command([CONFIG / 'bin/theme-mode', mode])), True, True, 0)
        outer.pack_start(scene, False, False, 0)
        outer.pack_start(self.button('切换桌面主题', lambda: self.command([CONFIG / 'bin/theme-picker'], hide=True)), False, False, 0)
        self.osd = self.window('desktop-osd', Layer.KeyboardMode.NONE)
        Layer.set_anchor(self.osd, Layer.Edge.BOTTOM, True)
        Layer.set_margin(self.osd, Layer.Edge.BOTTOM, 110)
        self.osd.set_size_request(350, -1)
        osd_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=11)
        osd_box.get_style_context().add_class('osd')
        self.osd.add(osd_box)
        line = Gtk.Box(spacing=12)
        self.osd_title = self.label('', 'osd-title')
        self.osd_value = self.label('')
        line.pack_start(self.osd_title, True, True, 0)
        line.pack_end(self.osd_value, False, False, 0)
        osd_box.pack_start(line, False, False, 0)
        self.progress = Gtk.ProgressBar()
        osd_box.pack_start(self.progress, False, False, 0)
        SOCKET.unlink(missing_ok=True)
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(str(SOCKET))
        self.socket.listen(8)
        self.GLib.timeout_add_seconds(2, self.periodic)

    def refresh_theme(self):
        palette = selected_palette()
        themed_css = recolor(CSS, palette)
        themed_css += '\n#desktop-panel calendar:selected { color: ' + selection_text(palette) + '; }\n'
        if themed_css != self.theme_css:
            self.css_provider.load_from_data(themed_css.encode())
            self.theme_css = themed_css

    def window(self, name, keyboard):
        window = self.Gtk.Window(type=self.Gtk.WindowType.TOPLEVEL)
        window.set_name(name)
        window.set_decorated(False)
        window.set_app_paintable(True)
        visual = window.get_screen().get_rgba_visual()
        if visual:
            window.set_visual(visual)
        self.Layer.init_for_window(window)
        self.Layer.set_namespace(window, name)
        self.Layer.set_layer(window, self.Layer.Layer.OVERLAY)
        self.Layer.set_exclusive_zone(window, -1)
        self.Layer.set_keyboard_mode(window, keyboard)
        return window

    def label(self, text, css_class=None):
        label = self.Gtk.Label(label=text)
        label.set_xalign(0)
        label.set_ellipsize(self.Pango.EllipsizeMode.END)
        label.set_max_width_chars(42)
        if css_class:
            label.get_style_context().add_class(css_class)
        return label

    def button(self, text, callback):
        button = self.Gtk.Button(label=text)
        button.connect('clicked', lambda *_: callback())
        return button

    def monitor(self, window):
        metadata = focused_monitor()
        if not metadata:
            return
        display = self.Gdk.Display.get_default()
        for i in range(display.get_n_monitors()):
            monitor = display.get_monitor(i)
            geometry = monitor.get_geometry()
            if geometry.x == metadata['x'] and geometry.y == metadata['y']:
                target = metadata.get('name', str(i))
                if getattr(window, '_desktop_monitor', None) != target:
                    if window.get_mapped():
                        window.hide()
                    self.Layer.set_monitor(window, monitor)
                    window._desktop_monitor = target
                return

    def run(self):
        threading.Thread(target=self.listen, daemon=True).start()
        self.Gtk.main()
        self.alive = False
        self.socket.close()
        SOCKET.unlink(missing_ok=True)
        self.worker.shutdown(wait=False, cancel_futures=True)
        self.commands.shutdown(wait=False, cancel_futures=True)

    def listen(self):
        while self.alive:
            try:
                connection, _ = self.socket.accept()
                with connection:
                    connection.settimeout(.6)
                    raw = b''
                    while b'\n' not in raw:
                        chunk = connection.recv(2048)
                        if not chunk or len(raw) + len(chunk) > 4096:
                            raise ValueError('Invalid desktop command')
                        raw += chunk
                    payload = json.loads(raw.split(b'\n')[0])
                    self.GLib.idle_add(self.handle, payload)
                    connection.sendall(b'ok\n')
            except Exception:
                if self.alive:
                    logging.exception('Desktop command failed')

    def handle(self, payload):
        try:
            action = payload.get('action')
            if action == 'quit':
                self.quit()
            elif action == 'close':
                self.hide_panel()
            elif action == 'panel':
                if self.panel.get_visible():
                    self.hide_panel()
                else:
                    self.refresh_theme()
                    if shutil.which('swaync-client'):
                        launch(['swaync-client', '--close-panel'])
                    self.monitor(self.panel)
                    self.panel.show_all()
                    self.panel.present()
                    self.update_clock()
                    self.periodic()
                    self.fetch_weather()
            elif action == 'osd':
                self.osd_request(payload.get('category'), payload.get('operation', 'show'))
        except Exception:
            logging.exception('Desktop action failed')
        return False

    def key(self, _, event):
        if self.Gdk.keyval_name(event.keyval) == 'Escape':
            self.hide_panel()
            return True
        return False

    def hide_panel(self):
        self.panel.hide()
        self.generation += 1
        return False

    def command(self, arguments, hide=False):
        def spawn():
            try:
                launch(arguments)
            except OSError:
                logging.exception('Could not launch %s', arguments)
            return False
        if hide:
            self.hide_panel()
            self.GLib.timeout_add(160, spawn)
        else:
            spawn()

    def bluetooth(self):
        if shutil.which('blueman-manager'):
            self.command(['blueman-manager'], hide=True)
        elif shutil.which('gnome-control-center'):
            self.command(['env', 'XDG_CURRENT_DESKTOP=GNOME', 'gnome-control-center', 'bluetooth'], hide=True)

    def update_clock(self):
        import datetime
        now = datetime.datetime.now()
        self.clock.set_text(now.strftime('%H:%M'))
        weekdays = '一二三四五六日'
        self.date.set_text(f'{now.year}年{now.month}月{now.day}日 · 星期{weekdays[now.weekday()]}')

    def periodic(self):
        if not self.alive:
            return False
        if not self.panel.get_visible() or self.polling:
            return True
        self.update_clock()
        self.polling = True
        generation = self.generation
        def collect():
            try:
                data = self.collect_stats()
                self.GLib.idle_add(self.apply_stats, data, generation)
            except Exception:
                logging.exception('Panel status update failed')
                self.GLib.idle_add(self.clear_polling)
        self.worker.submit(collect)
        return True

    def clear_polling(self):
        self.polling = False
        return False

    def collect_stats(self):
        cpu = [int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]]
        total, idle = sum(cpu), cpu[3] + cpu[4]
        usage = None
        if self.previous_cpu:
            dt, di = total - self.previous_cpu[0], idle - self.previous_cpu[1]
            if dt > 0:
                usage = max(0, min(100, (1 - di / dt) * 100))
        self.previous_cpu = (total, idle)
        memory = {}
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, value = line.split(':', 1)
            memory[key] = int(value.split()[0])
        used = (memory['MemTotal'] - memory['MemAvailable']) / 1024 / 1024
        total_gb = memory['MemTotal'] / 1024 / 1024
        temperatures = []
        for hwmon in sorted(Path('/sys/class/hwmon').glob('hwmon*')):
            try:
                name = (hwmon / 'name').read_text().strip()
                if name not in ['k10temp', 'coretemp', 'amdgpu', 'nvidia']:
                    continue
                values = [int(p.read_text()) / 1000 for p in hwmon.glob('temp*_input')]
                if values:
                    temperatures.append(f'{name} {max(values):.0f}°C')
            except OSError:
                pass
        if shutil.which('nvidia-smi'):
            gpu = output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], 1)
            if gpu.isdigit():
                temperatures.append(f'GPU {gpu}°C')
        metadata = output(['playerctl', 'metadata', '--format', '{{title}}\n{{artist}}'])
        volume = output(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'])
        network = output(['nmcli', '-t', '-f', 'TYPE,STATE,CONNECTION', 'device'])
        connections = [line.split(':', 2)[-1] for line in network.splitlines() if ':connected:' in line and line.startswith(('wifi:', 'ethernet:'))]
        return {'cpu': usage, 'used': used, 'memory': total_gb, 'temps': '  ·  '.join(temperatures), 'media': metadata,
                'volume': volume, 'network': ' / '.join(connections)}

    def apply_stats(self, data, generation):
        self.polling = False
        if not self.alive or generation != self.generation:
            return False
        cpu = '…' if data['cpu'] is None else f"{data['cpu']:.0f}%"
        self.stats.set_text(f"CPU {cpu}     内存 {data['used']:.1f} / {data['memory']:.1f} GiB")
        self.temps.set_text(data['temps'])
        media = data['media'].splitlines()
        self.media_title.set_text(media[0] if media else '没有正在播放的媒体')
        self.media_artist.set_text(media[1] if len(media) > 1 else '')
        self.media_controls.set_sensitive(bool(media))
        self.network.set_label(data['network'] or '网络设置')
        match = re.search(r'Volume:\s*([\d.]+)', data['volume'])
        if match:
            value = min(100, round(float(match[1]) * 100))
            self.refreshing_slider = True
            self.volume.set_value(value)
            self.volume_label.set_text('静音' if 'MUTED' in data['volume'] else f'音量 {value}%')
            self.refreshing_slider = False
        return False

    def slider_changed(self, slider):
        if self.refreshing_slider:
            return
        value = round(slider.get_value())
        if self.slider_timer:
            self.GLib.source_remove(self.slider_timer)
        def apply():
            self.slider_timer = None
            # Coalesce motion events and preserve order with key-driven changes.
            self.commands.submit(run, ['wpctl', 'set-volume', '-l', '1', '@DEFAULT_AUDIO_SINK@', f'{value}%'])
            return False
        self.slider_timer = self.GLib.timeout_add(45, apply)
        self.volume_label.set_text(f'音量 {value}%')

    def fetch_weather(self):
        if self.weather_pending:
            return
        self.weather_pending = True
        def collect():
            try:
                self.GLib.idle_add(self.apply_weather, panel_summary(get_weather()))
            except Exception:
                self.GLib.idle_add(self.apply_weather, '天气暂不可用')
        self.worker.submit(collect)

    def apply_weather(self, value):
        self.weather_pending = False
        self.weather_timestamp = time.time()
        self.weather = value
        self.weather_label.set_text(value)
        self.weather_label.set_visible(bool(value))
        return False

    def osd_request(self, category, operation):
        self.osd_generation += 1
        generation = self.osd_generation
        def change():
            try:
                if category == 'volume':
                    commands = {'up': ['wpctl', 'set-volume', '-l', '1', '@DEFAULT_AUDIO_SINK@', '5%+'],
                                'down': ['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%-'],
                                'mute': ['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle']}
                    if operation in commands:
                        result = run(commands[operation])
                        if result.returncode:
                            raise RuntimeError(result.stderr)
                    text = output(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'])
                    match = re.search(r'Volume:\s*([\d.]+)', text)
                    if not match:
                        raise RuntimeError('没有可用音频输出')
                    value = max(0, min(100, round(float(match[1]) * 100)))
                    muted = 'MUTED' in text
                    payload = ('静音' if muted else '音量', value, '静音' if muted else f'{value}%')
                elif category == 'brightness':
                    if not list(Path('/sys/class/backlight').iterdir()):
                        payload = ('亮度', None, '显示器没有可用背光接口')
                    else:
                        if operation in ('up', 'down'):
                            result = run(['brightnessctl', 'set', '5%+' if operation == 'up' else '5%-'])
                            if result.returncode:
                                raise RuntimeError(result.stderr)
                        current = output(['brightnessctl', 'get'])
                        maximum = output(['brightnessctl', 'max'])
                        if not current.isdigit() or not maximum.isdigit() or int(maximum) == 0:
                            raise RuntimeError('无法读取亮度')
                        value = round(int(current) / int(maximum) * 100)
                        payload = ('亮度', value, f'{value}%')
                else:
                    raise ValueError('Unknown OSD category')
                self.GLib.idle_add(self.show_osd, payload, generation)
            except Exception as error:
                self.GLib.idle_add(self.show_osd, ('无法调整', None, str(error)[:48]), generation)
        self.commands.submit(change)

    def show_osd(self, payload, generation):
        if generation != self.osd_generation or not self.alive:
            return False
        if self.osd_timer:
            self.GLib.source_remove(self.osd_timer)
        self.refresh_theme()
        title, value, text = payload
        self.osd_title.set_text(title)
        self.osd_value.set_text(text)
        self.progress.set_fraction((value or 0) / 100)
        self.progress.set_visible(value is not None)
        self.monitor(self.osd)
        self.osd.show_all()
        self.progress.set_visible(value is not None)
        def hide():
            if generation == self.osd_generation:
                self.osd.hide()
                self.osd_timer = None
            return False
        self.osd_timer = self.GLib.timeout_add(700, hide)
        return False

    def quit(self):
        self.alive = False
        self.generation += 1
        if self.osd_timer:
            self.GLib.source_remove(self.osd_timer)
            self.osd_timer = None
        if self.slider_timer:
            self.GLib.source_remove(self.slider_timer)
            self.slider_timer = None
        self.panel.hide()
        self.osd.hide()
        self.Gtk.main_quit()
        return False
