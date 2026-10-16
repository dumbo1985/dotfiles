-- ========================================
-- Neovide 图形界面配置
-- ----------------------------------------
-- ⚠️ 真正被加载的是这一份（core/init.lua 里 require("dengbo.core.neovide")）。
--    上层 ui/neovide.lua 是历史遗留、从未被 require，改配置别改错文件。
-- 全部可用选项：https://neovide.dev/configuration.html
-- 本机 Neovide 版本 0.16.2。
-- ========================================
if not vim.g.neovide then
	return
end

-- ---------------------------------------------------------------------------
-- 1. 字体与文字渲染
-- ---------------------------------------------------------------------------
-- guifont 格式：主字体,回退字体…:选项      （选项写在最后，对所有字体生效）
--   带空格的字体名可以用下划线写，Neovide 会还原成空格交给 fontconfig。
--   三个字体各司其职：等宽+图标 / 彩色 emoji / 中文。
--   调字号就改末尾的 h13。
vim.o.guifont = "MesloLGS_Nerd_Font_Mono,Noto_Color_Emoji,Noto_Sans_Mono_CJK_SC:h13"

-- 行间距（像素，可为负）。终端版 nvim 里无视觉效果，这是 Neovide 专属选项。
vim.opt.linespace = 3

-- 文字伽马/对比度微调，默认就是 0.0 / 0.5。
-- 想模仿 Alacritty 的字体渲染可以试 0.8 / 0.1。改了不会立刻生效（字体有缓存），
-- 重开窗口最稳。
vim.g.neovide_text_gamma = 0.0
vim.g.neovide_text_contrast = 0.5

-- 整体缩放（做演示/投屏时好用），1.0 = 原大小。可运行时改，见文末快捷键。
vim.g.neovide_scale_factor = 1.0

-- 【可选】想让文字更锐利（LCD 屏、且显示器是 RGB 排列）再打开下面两行：
--   vim.g.neovide_pixel_geometry = "RGBH"          -- 0.16 新增，默认 "Unknown"
--   并把上面的 guifont 改成 "...:h13:#e-subpixelantialias"
-- 半透明窗口下偶尔会有彩边，不喜欢就撤掉。

-- ---------------------------------------------------------------------------
-- 2. 窗口、留白与透明
-- ---------------------------------------------------------------------------
vim.g.neovide_opacity = 0.8 -- 整个窗口的不透明度，0~1，越小越透

-- 下面两个是 macOS 专有选项，在 Linux 上只是空设置（留着不影响，换平台即生效）
vim.g.neovide_window_blurred = true
vim.g.neovide_show_border = true

-- 文字块四周留白（像素），用背景色填充 —— 加了立刻不那么"顶格"
vim.g.neovide_padding_top = 14
vim.g.neovide_padding_bottom = 10
vim.g.neovide_padding_left = 16
vim.g.neovide_padding_right = 16

-- ---------------------------------------------------------------------------
-- 3. 浮动窗口（补全菜单 / LSP 悬浮框 / lazy 面板等）
-- ---------------------------------------------------------------------------
vim.g.neovide_floating_blur_amount_x = 2.0
vim.g.neovide_floating_blur_amount_y = 2.0
vim.g.neovide_floating_corner_radius = 0.3 -- 圆角，0~1（相对行高的比例），0 = 直角
vim.g.neovide_floating_shadow = true
vim.g.neovide_floating_z_height = 10 -- 阴影的"悬空高度"
vim.g.neovide_light_angle_degrees = 45 -- 投影光源角度
vim.g.neovide_light_radius = 5

-- ---------------------------------------------------------------------------
-- 4. 动画
-- ---------------------------------------------------------------------------
vim.g.neovide_position_animation_length = 0.15 -- :split 等窗口位置变化
vim.g.neovide_scroll_animation_length = 0.3
vim.g.neovide_scroll_animation_far_lines = 1

-- ---------------------------------------------------------------------------
-- 5. 光标与粒子特效
-- ---------------------------------------------------------------------------
vim.g.neovide_cursor_animation_length = 0.18 -- 越长拖影越明显
vim.g.neovide_cursor_short_animation_length = 0.08 -- 短距离移动用这个时长
vim.g.neovide_cursor_trail_size = 0.9
vim.g.neovide_cursor_antialiasing = true
vim.g.neovide_cursor_animate_in_insert_mode = true
vim.g.neovide_cursor_animate_command_line = true
vim.g.neovide_cursor_unfocused_outline_width = 0.125 -- 失焦时光标描边宽度

-- 粒子特效：可以给一个字符串，也可以给一个数组同时开多种。
-- 可选值：railgun 电磁炮 / torpedo 鱼雷 / pixiedust 星尘 /
--        sonicboom 音爆 / ripple 水波 / wireframe 线框
vim.g.neovide_cursor_vfx_mode = { "railgun", "pixiedust" }
vim.g.neovide_cursor_vfx_opacity = 200.0
vim.g.neovide_cursor_vfx_particle_lifetime = 1.2
vim.g.neovide_cursor_vfx_particle_density = 6.0 -- 双特效并行，密度比单开时略降
vim.g.neovide_cursor_vfx_particle_speed = 10.0
vim.g.neovide_cursor_vfx_particle_phase = 1.5
vim.g.neovide_cursor_vfx_particle_curl = 1.0

-- ---------------------------------------------------------------------------
-- 6. 进度条（0.16 新增，LSP 忙时在窗口顶部显示一条细进度线）
-- ---------------------------------------------------------------------------
vim.g.neovide_progress_bar_enabled = true
vim.g.neovide_progress_bar_height = 3.0
vim.g.neovide_progress_bar_animation_speed = 200.0
vim.g.neovide_progress_bar_hide_delay = 0.2

-- ---------------------------------------------------------------------------
-- 7. 状态与行为
-- ---------------------------------------------------------------------------
vim.g.neovide_refresh_rate = 60
vim.g.neovide_refresh_rate_idle = 5 -- 失焦时降到 5fps，省电
vim.g.neovide_no_idle = false -- true 会强制一直重绘，费 CPU
vim.g.neovide_hide_mouse_when_typing = true
vim.g.neovide_underline_stroke_scale = 1.0
vim.g.neovide_unlink_border_highlights = true
vim.g.neovide_theme = "dark" -- 仅 Windows / macOS / Wayland(带 CSD) 生效，X11 下无效果
vim.g.neovide_fullscreen = false -- 想启动即全屏就改成 true
vim.g.neovide_confirm_quit = true
vim.g.neovide_remember_window_size = true
vim.g.neovide_profiler = false
vim.g.neovide_input_macos_alt_is_meta = false
vim.g.neovide_input_ime = true

-- ---------------------------------------------------------------------------
-- 8. 键位
-- ---------------------------------------------------------------------------
-- 全屏切换。Neovide 0.16 没有内置全屏快捷键（F11 只会被原样转发给 Neovim）。
-- g:neovide_fullscreen 是「值发生变化才应用」的机制，必须用 not 取反。
vim.keymap.set({ "n", "i", "v", "t" }, "<F11>", function()
	vim.g.neovide_fullscreen = not vim.g.neovide_fullscreen
end, { silent = true, desc = "Neovide 切换全屏" })

-- 缩放（<C-=> / <C--> / <C-0>），演示时随手放大缩小
vim.keymap.set({ "n", "v" }, "<C-=>", function()
	vim.g.neovide_scale_factor = vim.g.neovide_scale_factor + 0.05
end, { silent = true, desc = "放大界面" })
vim.keymap.set({ "n", "v" }, "<C-->", function()
	vim.g.neovide_scale_factor = math.max(0.6, vim.g.neovide_scale_factor - 0.05)
end, { silent = true, desc = "缩小界面" })
vim.keymap.set({ "n", "v" }, "<C-0>", function()
	vim.g.neovide_scale_factor = 1.0
end, { silent = true, desc = "缩放复位" })

-- macOS 的 Cmd 键位（Linux 上不会触发，留着换平台即用）
vim.keymap.set("n", "<D-s>", ":w<CR>")
vim.keymap.set("v", "<D-c>", '"+y')
vim.keymap.set("n", "<D-v>", '"+P')
vim.keymap.set("v", "<D-v>", '"+P')
vim.keymap.set("c", "<D-v>", "<C-R>+")
vim.keymap.set("i", "<D-v>", '<ESC>l"+Pli')
vim.keymap.set("t", "<D-v>", "<C-R>+")
