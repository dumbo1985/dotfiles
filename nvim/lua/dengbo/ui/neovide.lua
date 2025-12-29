--- Neovide GUI 配置模块
--- 负责 Neovide 图形界面的所有配置
--- @module dengbo.ui.neovide

local M = {}

--- 检查是否在 Neovide 中运行
--- @return boolean
local function is_neovide()
	return vim.g.neovide ~= nil
end

--- 检查是否为 macOS
--- @return boolean
local function is_macos()
	return vim.fn.has("mac") == 1
end

--- 配置 Neovide GUI 选项
--- @return nil
local function setup_gui_options()
	if not is_neovide() then
		return
	end

	vim.o.guifont = "MesloLGS Nerd Font Mono:h12"
	vim.g.transparency = 0.8
	vim.g.neovide_transparency = 0.8
	vim.g.neovide_window_blurred = true
	vim.g.neovide_floating_blur_amount_x = 2.0
	vim.g.neovide_floating_blur_amount_y = 2.0
	vim.g.neovide_floating_shadow = true
	vim.g.neovide_floating_z_height = 10
	vim.g.neovide_light_angle_degrees = 45
	vim.g.neovide_light_radius = 5
	vim.g.neovide_show_border = true
	vim.g.neovide_scroll_animation_length = 0.3
	vim.g.neovide_scroll_animation_far_lines = 1
	vim.g.neovide_hide_mouse_when_typing = false
	vim.g.neovide_underline_stroke_scale = 1.0
	vim.g.neovide_theme = "auto"
	vim.g.neovide_unlink_border_highlights = true
	vim.g.neovide_refresh_rate = 60
	vim.g.neovide_fullscreen = false
	vim.g.neovide_confirm_quit = true
	vim.g.neovide_remember_window_size = true
	vim.g.neovide_profiler = false

	-- macOS 特定配置
	if is_macos() then
		vim.g.neovide_input_macos_alt_is_meta = false
	end

	vim.g.neovide_input_ime = true
end

--- 配置光标动画
--- @return nil
local function setup_cursor_animation()
	if not is_neovide() then
		return
	end

	vim.g.neovide_cursor_animation_length = 0.13
	vim.g.neovide_cursor_trail_size = 0.8
	vim.g.neovide_cursor_antialiasing = true
	vim.g.neovide_cursor_animate_in_insert_mode = true
	vim.g.neovide_cursor_animate_command_line = true
	vim.g.neovide_cursor_unfocused_outline_width = 0.125
	vim.g.neovide_cursor_vfx_mode = "railgun"
	vim.g.neovide_cursor_vfx_particle_curl = 1.0
	vim.g.neovide_cursor_vfx_particle_phase = 1.5
	vim.g.neovide_cursor_vfx_particle_speed = 10.0
	vim.g.neovide_cursor_vfx_particle_density = 7.0
	vim.g.neovide_cursor_vfx_particle_lifetime = 1.2
	vim.g.neovide_cursor_vfx_opacity = 200.0
end

--- 配置 Neovide 特定键位映射
--- @return nil
local function setup_keymaps()
	if not is_neovide() or not is_macos() then
		return
	end

	vim.keymap.set("n", "<D-s>", ":w<CR>", { desc = "Save" })
	vim.keymap.set("v", "<D-c>", '"+y', { desc = "Copy" })
	vim.keymap.set("n", "<D-v>", '"+P', { desc = "Paste normal mode" })
	vim.keymap.set("v", "<D-v>", '"+P', { desc = "Paste visual mode" })
	vim.keymap.set("c", "<D-v>", "<C-R>+", { desc = "Paste command mode" })
	vim.keymap.set("i", "<D-v>", '<ESC>l"+Pli', { desc = "Paste insert mode" })
end

--- 初始化 Neovide 配置
--- @return nil
function M.setup()
	setup_gui_options()
	setup_cursor_animation()
	setup_keymaps()
end

return M

