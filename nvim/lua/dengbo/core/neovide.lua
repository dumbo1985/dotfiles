-- ========================================
-- Neovide 配置
-- ========================================
if not vim.g.neovide then
	return
end

vim.o.guifont = "MesloLGS Nerd Font Mono:h12"
vim.g.transparency = 0.6
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
vim.g.neovide_theme = "dark"
vim.g.neovide_unlink_border_highlights = true
vim.g.neovide_refresh_rate = 60
vim.g.neovide_fullscreen = false
vim.g.neovide_confirm_quit = true
vim.g.neovide_remember_window_size = true
vim.g.neovide_profiler = false
vim.g.neovide_input_macos_alt_is_meta = false
vim.g.neovide_input_ime = true
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

-- Neovide 特定的键位映射
vim.keymap.set("n", "<D-s>", ":w<CR>")
vim.keymap.set("v", "<D-c>", '"+y')
vim.keymap.set("n", "<D-v>", '"+P')
vim.keymap.set("v", "<D-v>", '"+P')
vim.keymap.set("c", "<D-v>", "<C-R>+")
vim.keymap.set("i", "<D-v>", '<ESC>l"+Pli')
vim.keymap.set("t", "<D-v>", "<C-R>+")

