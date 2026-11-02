-- Hyprland 0.57 Lua configuration. Neovide supplies its own opacity (0.8).
local home = os.getenv("HOME")
local config = (os.getenv("XDG_CONFIG_HOME") or home .. "/.config") .. "/hypr"
local function helper(name)
    return string.format("%q", config .. "/bin/" .. name)
end

hl.monitor({ output = "", mode = "preferred", position = "auto", scale = "auto" })
-- Main display on the left; portrait display on the right, aligned at the top.
hl.monitor({ output = "DP-1", mode = "3840x2160@75", position = "0x0", scale = 1.25 })
hl.monitor({ output = "DP-2", mode = "3840x2160@75", position = "3072x0", scale = 1.25, transform = 1 })
hl.env("PATH", home .. "/.local/share/hypr-theme/bin:" .. home .. "/.local/bin:" .. (os.getenv("PATH") or "/usr/bin:/bin"))
hl.env("XCURSOR_THEME", "BreezeX-RosePine")
hl.env("XCURSOR_SIZE", "28")
hl.env("HYPRCURSOR_THEME", "rose-pine-hyprcursor")
hl.env("HYPRCURSOR_SIZE", "28")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_IM_MODULE", "fcitx")
hl.env("GTK_IM_MODULE", "fcitx")
hl.env("XMODIFIERS", "@im=fcitx")
hl.env("GTK_THEME", "Tokyonight-Dark")
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
hl.env("QT_PLUGIN_PATH", home .. "/.local/share/hypr-theme/qt-plugins")

hl.config({
    -- Smooth legacy X11 apps at fractional scales instead of enlarging pixel blocks.
    xwayland = { use_nearest_neighbor = false },
    general = {
        gaps_in = 6,
        gaps_out = 14,
        gaps_workspaces = 36,
        border_size = 2,
        resize_on_border = true,
        layout = "dwindle",
        col = {
            active_border = { colors = { "rgba(7aa2f7ff)", "rgba(bb9af7ff)", "rgba(7dcfffff)" }, angle = 35 },
            inactive_border = "rgba(41486899)",
        },
    },
    decoration = {
        rounding = 16,
        active_opacity = 1.0,
        inactive_opacity = 1.0,
        dim_inactive = true,
        dim_strength = 0.08,
        shadow = { enabled = true, range = 24, render_power = 3, color = 0x66080c16 },
        blur = { enabled = true, size = 6, passes = 3, vibrancy = 0.15 },
    },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    input = {
        kb_layout = "us",
        follow_mouse = 1,
        sensitivity = 0,
        touchpad = { natural_scroll = true },
    },
    misc = {
        disable_hyprland_logo = true,
        force_default_wallpaper = 0,
        animate_manual_resizes = true,
        animate_mouse_windowdragging = true,
    },
})

hl.curve("smooth", { type = "bezier", points = { { 0.22, 1 }, { 0.36, 1 } } })
hl.curve("motion", { type = "bezier", points = { { 0.16, 1 }, { 0.3, 1 } } })
hl.curve("workspaceGlide", { type = "bezier", points = { { 0.22, 0.8 }, { 0.2, 1 } } })
hl.curve("gentle", { type = "bezier", points = { { 0.25, 0.1 }, { 0.25, 1 } } })
hl.curve("orbit", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.animation({ leaf = "global", enabled = true, speed = 4, bezier = "smooth" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 3.4, bezier = "motion", style = "popin 92%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2, bezier = "gentle", style = "popin 96%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 3.2, bezier = "motion" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 4.5, bezier = "workspaceGlide", style = "slidevert" })
hl.animation({ leaf = "fade", enabled = true, speed = 2, bezier = "gentle" })
hl.animation({ leaf = "fadeDim", enabled = true, speed = 2.2, bezier = "gentle" })
hl.animation({ leaf = "border", enabled = true, speed = 2.5, bezier = "gentle" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 100, bezier = "orbit", style = "loop" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 2.5, bezier = "motion", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.8, bezier = "gentle", style = "fade" })
hl.layer_rule({ name = "launcher-motion", match = { namespace = "wofi" }, animation = "popin 96%" })
hl.layer_rule({ name = "desktop-search-motion", match = { namespace = "desktop-launcher" }, animation = "fade" })
hl.layer_rule({ name = "notification-motion", match = { namespace = "notifications" }, animation = "slide top" })
hl.layer_rule({ name = "workspace-overview-motion", match = { namespace = "workspace-overview" }, no_anim = true })
hl.layer_rule({ name = "bar-glass", match = { namespace = "waybar" }, blur = true, ignore_alpha = 0.15 })
hl.layer_rule({ name = "control-glass", match = { namespace = "swaync-control-center" }, blur = true, ignore_alpha = 0.15, animation = "slide right" })
hl.layer_rule({ name = "toast-motion", match = { namespace = "swaync-notification-window" }, animation = "slide right" })
hl.layer_rule({ name = "desktop-panel-motion", match = { namespace = "desktop-panel" }, blur = true, ignore_alpha = 0.15, animation = "slide right" })
hl.layer_rule({ name = "desktop-osd-motion", match = { namespace = "desktop-osd" }, animation = "popin 94%" })
hl.layer_rule({ name = "power-motion", match = { namespace = "logout_dialog" }, blur = true, ignore_alpha = 0.15, animation = "fade" })
hl.window_rule({ name = "music-spectrum", match = { class = "hypr-music-visualizer" }, float = true, center = true, size = "900 380" })
hl.window_rule({ name = "file-preview", match = { class = "org.gnome.NautilusPreviewer" }, float = true, center = true, size = "1050 740" })

-- The optional plugin is loaded by the session helper after checking its ABI.
if hl.plugin.dynamic_cursors then
    hl.config({ plugin = { dynamic_cursors = {
        enabled = true,
        mode = "stretch",
        threshold = 2,
        stretch = { limit = 6500, activation = "quadratic", window = 70 },
        shake = { enabled = true, threshold = 7, base = 2, speed = 1.5, limit = 3, timeout = 900, effects = false },
        hyprcursor = { enabled = true, nearest = 0, resolution = 96 },
    } } })
    hl.plugin.dynamic_cursors.shape_rule({ shape = "text", mode = "none" })
    hl.plugin.dynamic_cursors.shape_rule({ shape = "crosshair", mode = "none" })
end

hl.on("hyprland.start", function()
    hl.exec_cmd(helper("session-start"))
end)

hl.bind("SUPER + Return", hl.dsp.exec_cmd(helper("terminal")))
hl.bind("SUPER + space", hl.dsp.exec_cmd(helper("launcher")))
hl.bind("SUPER + SHIFT + space", hl.dsp.exec_cmd("wofi --show drun --conf " .. string.format("%q", config .. "/wofi.conf")
    .. " --style " .. string.format("%q", config .. "/wofi.css")))
hl.bind("SUPER + O", hl.dsp.exec_cmd(helper("workspace-switch") .. " --overview"))
hl.bind("SUPER + C", hl.dsp.exec_cmd(helper("control-center")))
hl.bind("SUPER + D", hl.dsp.exec_cmd(helper("desktop-panel")))
hl.bind("SUPER + W", hl.dsp.exec_cmd(helper("window-switcher")))
hl.bind("SUPER + Tab", hl.dsp.exec_cmd(helper("window-cycle")))
hl.bind("SUPER + SHIFT + Tab", hl.dsp.exec_cmd(helper("window-cycle") .. " --reverse"))
hl.bind("SUPER + grave", hl.dsp.exec_cmd(helper("window-cycle") .. " --same-app"))
hl.bind("SUPER + SHIFT + grave", hl.dsp.exec_cmd(helper("window-cycle") .. " --same-app --reverse"))
hl.bind("SUPER + SHIFT + O", hl.dsp.exec_cmd(helper("screen-ocr")))
hl.bind("SUPER + CTRL + O", hl.dsp.exec_cmd(helper("screen-ocr") .. " --code"))
hl.bind("SUPER + M", hl.dsp.exec_cmd(helper("music-visualizer")))
hl.bind("SUPER + SHIFT + V", hl.dsp.exec_cmd(helper("clipboard")))
hl.bind("SUPER + period", hl.dsp.exec_cmd(helper("emoji")))
hl.bind("SUPER + SHIFT + P", hl.dsp.exec_cmd(helper("power-menu")))
hl.bind("SUPER + SHIFT + B", hl.dsp.exec_cmd(helper("wallpaper") .. " next"))
hl.bind("SUPER + SHIFT + T", hl.dsp.exec_cmd(helper("theme-picker")))
hl.bind("SUPER + SHIFT + C", hl.dsp.exec_cmd(helper("cursor-picker")))
hl.bind("SUPER + N", hl.dsp.exec_cmd(home .. "/.local/bin/neovide"))
hl.bind("SUPER + E", hl.dsp.exec_cmd("nautilus --new-window"))
hl.bind("SUPER + B", hl.dsp.exec_cmd("xdg-open https://www.google.com"))
hl.bind("SUPER + Q", hl.dsp.window.close())
hl.bind("SUPER + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind("SUPER + F", hl.dsp.window.fullscreen_state({ action = "toggle", internal = 2, client = 2 }))
hl.bind("SUPER + SHIFT + F", hl.dsp.window.fullscreen_state({ action = "toggle", internal = 1, client = 1 }))
hl.bind("SUPER + L", hl.dsp.exec_cmd("loginctl lock-session"))
hl.bind("SUPER + SHIFT + E", hl.dsp.exit())
hl.bind("Print", hl.dsp.exec_cmd(helper("screenshot")))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd(helper("screenshot") .. " full"))
hl.bind("SUPER + Print", hl.dsp.exec_cmd(helper("screenshot") .. " edit"))

for _, direction in ipairs({ "left", "right", "up", "down" }) do
    hl.bind("SUPER + " .. direction, hl.dsp.focus({ direction = direction }))
end
for i = 1, 10 do
    local key = i % 10
    hl.bind("SUPER + " .. key, hl.dsp.exec_cmd(helper("workspace-switch") .. " " .. i))
    hl.bind("SUPER + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd(helper("osd") .. " volume up"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd(helper("osd") .. " volume down"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd(helper("osd") .. " volume mute"), { locked = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd(helper("osd") .. " brightness up"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(helper("osd") .. " brightness down"), { locked = true, repeating = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

-- Palette overrides are generated independently of display, input and key rules.
local current_theme = config .. "/themes/current.lua"
local theme_file = io.open(current_theme, "r")
if theme_file then
    theme_file:close()
    pcall(dofile, current_theme)
end

-- Cursor choices are independent of the desktop palette and survive reloads.
local current_cursor = config .. "/cursors/current.lua"
local cursor_file = io.open(current_cursor, "r")
if cursor_file then
    cursor_file:close()
    dofile(current_cursor)
end
