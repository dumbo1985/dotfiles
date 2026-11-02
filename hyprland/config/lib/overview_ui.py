"""Wayland workspaces overview, isolated from Hyprland's plugin ABI.

The caller owns screenshot storage, compositor dispatch, and Gtk.main().
Set GI_TYPELIB_PATH before importing this module when using a private typelib.
"""
from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Callable

from theme_palette import selected_palette

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("PangoCairo", "1.0")
gi.require_foreign("cairo")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, GtkLayerShell, Pango, PangoCairo


class OverviewUI:
    OPEN_SECONDS = 0.22
    HOLD_SECONDS = 0.18
    CLOSE_SECONDS = 0.24
    COLOR_ROLES = {
        "background": "bg",
        "panel": "surface",
        "text": "fg",
        "muted": "muted",
        "blue": "blue",
        "purple": "purple",
        "line": "comment",
    }

    def __init__(self, select_callback: Callable[[int], None], close_callback: Callable[[], None]):
        self._load_colors()
        self.select_callback = select_callback
        self.close_callback = close_callback
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("工作区总览")
        self.window.set_decorated(False)
        self.window.set_app_paintable(True)
        visual = self.window.get_screen().get_rgba_visual()
        if visual:
            self.window.set_visual(visual)
        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_namespace(self.window, "workspace-overview")
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_exclusive_zone(self.window, -1)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
                     GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self.window, edge, True)
        self.canvas = Gtk.DrawingArea()
        self.canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.canvas.connect("draw", self._draw)
        self.canvas.connect("button-press-event", self._click)
        self.canvas.connect("motion-notify-event", self._motion)
        self.window.connect("key-press-event", self._key)
        self.window.connect("delete-event", self._delete)
        self.window.add(self.canvas)
        self._visible = False
        self._generation = 0
        self._source = 0
        self._items: list[dict] = []
        self._images: dict[int, GdkPixbuf.Pixbuf] = {}
        self._monitor: dict = {}
        self._current = 1
        self._selected = 1
        self._target: int | None = None
        self._hover: int | None = None
        self._phase = "opening"
        self._phase_start = 0.0
        self._progress = 0.0
        self._columns = 4
        self._boxes: dict[int, tuple[float, float, float, float]] = {}
        self._wallpaper: GdkPixbuf.Pixbuf | None = None
        self._card_cache = {}
        self._backdrop = None
        self._backdrop_key = None
        self._layout_key = None
        self._decoded_images = {}
        self._wallpaper_cache = {}

    def is_visible(self) -> bool:
        return self._visible

    def _load_colors(self):
        palette = selected_palette()["colors"]
        self.colors = {}
        for role, name in self.COLOR_ROLES.items():
            value = palette[name].lstrip("#")
            self.colors[role] = tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))

    def show(self, monitor: dict, items: list[dict], current: int, target: int | None = None):
        # Theme changes only rebuild the static surfaces on the next opening.
        self._load_colors()
        self._generation += 1
        self._cancel_tick()
        # Unmap before retargeting the layer surface to a different output.
        if self._visible:
            self.window.hide()
            self._visible = False
        self._monitor = dict(monitor)
        self._items = sorted((dict(item) for item in items), key=lambda item: int(item["id"]))
        self._current = int(current)
        ids = {int(item["id"]) for item in self._items}
        self._selected = self._current if self._current in ids else (min(ids) if ids else 1)
        self._target = int(target) if target is not None and int(target) in ids else None
        self._hover = None
        self._images = {}
        self._card_cache.clear()
        self._backdrop = None
        self._backdrop_key = None
        self._layout_key = None
        # Decode at preview size. Images never need to be read on every frame.
        for item in self._items:
            path = item.get("image")
            if path:
                try:
                    stamp = (str(path), Path(path).stat().st_mtime_ns)
                    image = self._decoded_images.get(stamp)
                    if image is None:
                        image = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), 1280, 1280, True)
                        self._decoded_images = {k: v for k, v in self._decoded_images.items() if k[0] != str(path)}
                        self._decoded_images[stamp] = image
                    self._images[int(item["id"])] = image
                except (GLib.Error, OSError):
                    pass
        portrait = int(monitor.get("transform", 0)) % 2 == 1
        path = Path(__file__).resolve().parent.parent / "wallpapers" / (
            "orbit-portrait.png" if portrait else "orbit-landscape.png")
        try:
            self._wallpaper = self._wallpaper_cache.get(str(path))
            if self._wallpaper is None:
                self._wallpaper = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), 1000, 1000, True)
                self._wallpaper_cache[str(path)] = self._wallpaper
        except (GLib.Error, OSError):
            self._wallpaper = None
        display = Gdk.Display.get_default()
        chosen = None
        for index in range(display.get_n_monitors()):
            candidate = display.get_monitor(index)
            geometry = candidate.get_geometry()
            if geometry.x == monitor.get("x", 0) and geometry.y == monitor.get("y", 0):
                chosen = candidate
                break
        if chosen is None:
            chosen = display.get_monitor(min(int(monitor.get("id", 0)), display.get_n_monitors() - 1))
        GtkLayerShell.set_monitor(self.window, chosen)
        # Build static layers before the first visible animation frame. Otherwise
        # PNG scaling and Pango shaping consume part of its 220 ms duration.
        geometry = chosen.get_geometry()
        self._layout(geometry.width, geometry.height)
        self._ensure_backdrop(geometry.width, geometry.height)
        self._phase = "opening"
        self._progress = 0.0
        self._phase_start = time.monotonic()
        self._visible = True
        self.window.show_all()
        self.window.present()
        self._source = self.canvas.add_tick_callback(self._frame_tick, self._generation)
        self.canvas.queue_draw()

    def hide(self):
        self._generation += 1
        self._visible = False
        self._cancel_tick()
        self.window.hide()
        self._images.clear()
        self._wallpaper = None
        self._boxes.clear()
        self._card_cache.clear()
        self._backdrop = None
        self._backdrop_key = None
        self._layout_key = None

    def _cancel_tick(self):
        if self._source:
            self.canvas.remove_tick_callback(self._source)
            self._source = 0

    def _frame_tick(self, _widget, _clock, generation):
        return self._tick(generation)

    def _tick(self, generation: int):
        if generation != self._generation or not self._visible:
            return GLib.SOURCE_REMOVE
        elapsed = time.monotonic() - self._phase_start
        duration = self.CLOSE_SECONDS if self._phase == "closing" else self.OPEN_SECONDS
        self._progress = min(1.0, elapsed / duration)
        if self._phase == "opening" and self._progress >= 1.0:
            self._phase = "holding"
            self._phase_start = time.monotonic()
            self._progress = 1.0
            if self._target is None:
                self._source = 0
                self.canvas.queue_draw()
                return GLib.SOURCE_REMOVE
        elif self._phase == "holding":
            self._progress = 1.0
            if self._target is not None and elapsed >= self.HOLD_SECONDS:
                self._selected = self._target
                self._phase = "closing"
                self._phase_start = time.monotonic()
                self._progress = 0.0
        elif self._phase == "closing" and self._progress >= 1.0:
            self._source = 0
            workspace = self._selected
            try:
                self.select_callback(workspace)
            finally:
                # A callback can open another generation; do not hide that one.
                if generation == self._generation:
                    self.hide()
            return GLib.SOURCE_REMOVE
        self.canvas.queue_draw()
        return GLib.SOURCE_CONTINUE

    @staticmethod
    def _ease(progress: float) -> float:
        return 1.0 - (1.0 - max(0.0, min(progress, 1.0))) ** 3

    @staticmethod
    def _rounded(cr, x, y, width, height, radius):
        radius = min(radius, width / 2, height / 2)
        cr.new_sub_path()
        for px, py, start in ((x + width - radius, y + radius, -math.pi / 2),
                              (x + width - radius, y + height - radius, 0),
                              (x + radius, y + height - radius, math.pi / 2),
                              (x + radius, y + radius, math.pi)):
            cr.arc(px, py, radius, start, start + math.pi / 2)
        cr.close_path()

    def _color(self, cr, name, alpha=1.0):
        cr.set_source_rgba(*self.colors[name], alpha)

    def _text(self, cr, text, x, y, width, size=14, color="text", bold=False):
        layout = PangoCairo.create_layout(cr)
        description = Pango.FontDescription()
        description.set_family("Noto Sans CJK SC")
        description.set_absolute_size(size * Pango.SCALE)
        description.set_weight(Pango.Weight.MEDIUM if bold else Pango.Weight.NORMAL)
        layout.set_font_description(description)
        layout.set_width(max(1, int(width * Pango.SCALE)))
        layout.set_ellipsize(Pango.EllipsizeMode.END)
        layout.set_single_paragraph_mode(True)
        # Never interpret application titles as markup.
        layout.set_text(str(text), -1)
        self._color(cr, color)
        cr.move_to(x, y)
        PangoCairo.show_layout(cr, layout)

    @staticmethod
    def _pixbuf(cr, image, rect, fill=False, alpha=1.0):
        x, y, width, height = rect
        if width <= 0 or height <= 0:
            return
        sx, sy = width / image.get_width(), height / image.get_height()
        scale = max(sx, sy) if fill else min(sx, sy)
        iw, ih = image.get_width() * scale, image.get_height() * scale
        cr.save()
        cr.rectangle(x, y, width, height)
        cr.clip()
        cr.translate(x + (width - iw) / 2, y + (height - ih) / 2)
        cr.scale(scale, scale)
        Gdk.cairo_set_source_pixbuf(cr, image, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_BILINEAR)
        cr.paint_with_alpha(alpha)
        cr.restore()

    def _layout(self, width, height):
        key = (width, height, len(self._items))
        if self._layout_key == key:
            return
        self._layout_key = key
        self._card_cache.clear()
        self._backdrop = None
        self._backdrop_key = None
        portrait = height > width * 1.1
        self._columns = 2 if portrait else (3 if width < 1050 else 4)
        rows = max(1, math.ceil(len(self._items) / self._columns))
        outer = max(22, min(64, width * .035))
        gap = max(14, min(24, width * .014))
        available_w = width - 2 * outer
        available_h = height - 150 - 2 * outer
        card_w = (available_w - gap * (self._columns - 1)) / self._columns
        card_h = min((available_h - gap * (rows - 1)) / rows, card_w * .66 + 36)
        total_h = card_h * rows + gap * (rows - 1)
        top = 105 + max(0, (available_h - total_h) / 2)
        self._boxes = {}
        for index, item in enumerate(self._items):
            self._boxes[int(item["id"])] = (outer + index % self._columns * (card_w + gap),
                                            top + index // self._columns * (card_h + gap), card_w, card_h)

    def _surface(self, width, height):
        scale = max(1, self.canvas.get_scale_factor())
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, math.ceil(width * scale), math.ceil(height * scale))
        surface.set_device_scale(scale, scale)
        return surface

    def _ensure_backdrop(self, width, height):
        # The expensive wallpaper/text/thumbnail work happens once per UI state.
        # Each animation frame composites this surface and one moving card.
        key = (width, height, self.canvas.get_scale_factor())
        if self._backdrop_key == key and self._backdrop is not None:
            return
        surface = self._surface(width, height)
        ctx = cairo.Context(surface)
        self._color(ctx, "background", 1.0)
        ctx.paint()
        if self._wallpaper:
            self._pixbuf(ctx, self._wallpaper, (0, 0, width, height), fill=True, alpha=.18)
        self._text(ctx, "工作区总览", 36, 27, width - 90, 26, bold=True)
        name = self._monitor.get("name", "")
        self._text(ctx, f"{name}  ·  数字选择 / 方向键移动 / Enter 确认 / Esc 返回", 38, 67, width - 76, 14, "muted")
        for item in self._items:
            box = self._boxes[int(item["id"])]
            self._paint_card(ctx, item, box, False)
        self._text(ctx, "缩略图为最近访问画面；尚未缓存的工作区显示窗口布局。", 38, height - 40, width - 76, 13, "muted")
        surface.flush()
        self._backdrop, self._backdrop_key = surface, key

    def _draw(self, _widget, cr):
        width, height = self.canvas.get_allocated_width(), self.canvas.get_allocated_height()
        if width < 1 or height < 1:
            return False
        self._layout(width, height)
        self._ensure_backdrop(width, height)
        cr.save()
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_surface(self._backdrop, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        for workspace, color in ((self._selected, "blue"), (self._hover, "purple")):
            if workspace in self._boxes:
                x, y, cw, ch = self._boxes[workspace]
                self._rounded(cr, x + 1, y + 1, cw - 2, ch - 2, 14)
                self._color(cr, color)
                cr.set_line_width(2.4 if color == "blue" else 1.5)
                cr.stroke()
        if self._phase in ("opening", "closing"):
            progress = self._ease(self._progress)
            active = self._selected if self._phase == "closing" else self._current
            item = next((i for i in self._items if int(i["id"]) == active), None)
            if item:
                small = self._boxes[active]
                full = (0.0, 0.0, float(width), float(height))
                start, finish = (small, full) if self._phase == "closing" else (full, small)
                box = tuple(a + (b - a) * progress for a, b in zip(start, finish))
                self._paint_card(cr, item, box, True)
        cr.restore()
        return False

    def _card_surface(self, item):
        workspace = int(item["id"])
        _, _, width, height = self._boxes[workspace]
        key = (workspace, round(width, 3), round(height, 3), self.canvas.get_scale_factor())
        cached = self._card_cache.get(key)
        if cached is not None:
            return cached
        surface = self._surface(width, height)
        ctx = cairo.Context(surface)
        # Clip BEFORE drawing: no per-card group may allocate an output-sized buffer.
        self._rounded(ctx, 0, 0, width, height, 14)
        ctx.clip()
        self._color(ctx, "panel")
        ctx.paint()
        content = (1, 1, max(1, width - 2), max(1, height - 40))
        if workspace in self._images:
            self._pixbuf(ctx, self._images[workspace], content)
        else:
            self._uncached(ctx, item, content)
        label = f"{workspace if workspace != 10 else '0 / 10'}  ·  {item.get('title') or '工作区 ' + str(workspace)}"
        self._text(ctx, label, 13, height - 32, width - 26, 13)
        self._rounded(ctx, 1, 1, width - 2, height - 2, 14)
        self._color(ctx, "line")
        ctx.set_line_width(1)
        ctx.stroke()
        surface.flush()
        # Bound alternate highlight states while preserving the 10 current cards.
        if len(self._card_cache) > max(30, len(self._items) * 3):
            self._card_cache.clear()
        self._card_cache[key] = surface
        return surface

    def _paint_card(self, cr, item, rect, animated):
        surface = self._card_surface(item)
        x, y, width, height = rect
        _, _, original_w, original_h = self._boxes[int(item["id"])]
        cr.save()
        cr.rectangle(x, y, width, height)
        cr.clip()
        cr.translate(x, y)
        cr.scale(width / original_w, height / original_h)
        cr.set_source_surface(surface, 0, 0)
        # Fast sampling only during motion; settled cards retain exact-size text.
        cr.get_source().set_filter(cairo.FILTER_FAST if animated else cairo.FILTER_NEAREST)
        cr.paint()
        cr.restore()

    def _uncached(self, cr, item, rect):
        x, y, width, height = rect
        if self._wallpaper:
            self._pixbuf(cr, self._wallpaper, rect, fill=True, alpha=.6)
        windows = item.get("windows") or []
        monitor = item.get("monitor") or self._monitor
        scale = float(monitor.get("scale", 1))
        mw, mh = float(monitor.get("width", 1920)), float(monitor.get("height", 1080))
        if int(monitor.get("transform", 0)) % 2:
            mw, mh = mh, mw
        mw, mh = max(mw / scale, 1), max(mh / scale, 1)
        ratio = min(width / mw, height / mh)
        left, top = x + (width - mw * ratio) / 2, y + (height - mh * ratio) / 2
        for window in windows:
            at, size = window.get("at", [0, 0]), window.get("size", [300, 200])
            wx = left + (float(at[0]) - float(monitor.get("x", 0))) * ratio
            wy = top + (float(at[1]) - float(monitor.get("y", 0))) * ratio
            ww, wh = max(8, float(size[0]) * ratio), max(8, float(size[1]) * ratio)
            self._rounded(cr, wx, wy, ww, wh, min(7, wh / 4))
            self._color(cr, "panel", .94)
            cr.fill_preserve()
            self._color(cr, "line")
            cr.set_line_width(1)
            cr.stroke()
            if ww > 70 and wh > 30:
                self._text(cr, window.get("title") or window.get("class") or "窗口", wx + 7, wy + 7, ww - 14, 11, "muted")
        self._text(cr, "预览未缓存" if windows else "空工作区", x + 12, y + height - 29, width - 24, 12, "muted")

    def _choose(self, workspace):
        if not self._visible or self._phase == "closing":
            return
        self._selected = int(workspace)
        self._target = self._selected
        self._phase = "closing"
        self._phase_start = time.monotonic()
        self._progress = 0.0
        if not self._source:
            self._source = self.canvas.add_tick_callback(self._frame_tick, self._generation)
        self.canvas.queue_draw()

    def _close(self):
        self.hide()
        self.close_callback()

    def _key(self, _window, event):
        if not self._visible:
            return False
        name = Gdk.keyval_name(event.keyval) or ""
        ids = [int(item["id"]) for item in self._items]
        if name == "Escape":
            self._close()
        elif name in tuple(str(i) for i in range(10)):
            target = 10 if name == "0" else int(name)
            if target in ids:
                self._choose(target)
        elif name.startswith("KP_") and name[3:].isdigit():
            target = 10 if name[3:] == "0" else int(name[3:])
            if target in ids:
                self._choose(target)
        elif name in ("Return", "KP_Enter", "space"):
            self._choose(self._selected)
        elif name in ("Left", "Right", "Up", "Down") and ids:
            if self._phase == "closing":
                return True
            index = ids.index(self._selected) if self._selected in ids else 0
            delta = {"Left": -1, "Right": 1, "Up": -self._columns, "Down": self._columns}[name]
            self._selected = ids[max(0, min(len(ids) - 1, index + delta))]
            self.canvas.queue_draw()
        return True

    def _hit(self, x, y):
        for workspace, (left, top, width, height) in self._boxes.items():
            if left <= x <= left + width and top <= y <= top + height:
                return workspace
        return None

    def _motion(self, _widget, event):
        if self._phase == "closing":
            return False
        hover = self._hit(event.x, event.y)
        if hover != self._hover:
            self._hover = hover
            self.canvas.queue_draw()
        return True

    def _click(self, _widget, event):
        if event.button == 1:
            workspace = self._hit(event.x, event.y)
            if workspace is not None:
                self._choose(workspace)
        elif event.button == 3:
            self._close()
        return True

    def _delete(self, *_args):
        self._close()
        return True
