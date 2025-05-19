local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
	vim.fn.system({
		"git",
		"clone",
		"--filter=blob:none",
		"https://github.com/folke/lazy.nvim.git",
		"--branch=stable", -- latest stable release
		lazypath,
	})
end
vim.opt.rtp:prepend(lazypath)

local last_input_method = nil

vim.api.nvim_create_autocmd("InsertLeave", {
	callback = function()
		-- 记录当前输入法
		last_input_method = vim.fn.system("im-select"):gsub("\n", "")
		-- 切换为英文
		vim.fn.system("im-select com.apple.keylayout.ABC")
	end,
})

vim.api.nvim_create_autocmd("InsertEnter", {
	callback = function()
		-- 恢复之前的输入法（如果记录了）
		if last_input_method then
			vim.fn.system("im-select " .. last_input_method)
		end
	end,
})

require("lazy").setup({ { import = "dengbo.plugins" }, { import = "dengbo.plugins.lsp" } }, {
	checker = {
		enabled = true,
		notify = false,
	},
	change_detection = {
		notify = false,
	},
})

-- 启用缩进折叠（或切换为 marker/syntax 等）
vim.opt.foldmethod = "expr" -- 使用 treesitter 的 expr 折叠
vim.opt.foldexpr = "nvim_treesitter#foldexpr()"
vim.opt.foldlevel = 99 -- 默认不折叠
vim.opt.foldtext = "v:lua.vim.treesitter.foldtext()" -- 美化折叠显示

----- Neovide GUI -----
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

if vim.g.neovide then
	vim.keymap.set("n", "<D-s>", ":w<CR>") -- Save
	vim.keymap.set("v", "<D-c>", '"+y') -- Copy
	vim.keymap.set("n", "<D-v>", '"+P') -- Paste normal mode
	vim.keymap.set("v", "<D-v>", '"+P') -- Paste visual mode
	vim.keymap.set("c", "<D-v>", "<C-R>+") -- Paste command mode
	vim.keymap.set("i", "<D-v>", '<ESC>l"+Pli') -- Paste insert mode
end

-- Allow clipboard copy paste in neovim
vim.api.nvim_set_keymap("", "<D-v>", "+p<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("!", "<D-v>", "<C-R>+", { noremap = true, silent = true })
vim.api.nvim_set_keymap("t", "<D-v>", "<C-R>+", { noremap = true, silent = true })
vim.api.nvim_set_keymap("v", "<D-v>", "<C-R>+", { noremap = true, silent = true })

vim.g.transparent_groups = vim.list_extend(vim.g.transparent_groups or {}, { "ExtraGroup" })

-- plugins/colorscheme.lua 末尾添加以下代码
vim.schedule(function()
	local themes = {
		{
			name = "tokyonight",
			setup = function()
				require("tokyonight").setup({ style = "night" })
			end,
		},
		{
			name = "kanagawa",
			setup = function()
				require("kanagawa").setup({ background = { dark = "wave" } })
			end,
		},
		{
			name = "catppuccin",
			setup = function()
				require("catppuccin").setup({ flavour = "mocha" })
			end,
		},
		{
			name = "rose-pine",
			setup = function()
				require("rose-pine").setup({ variant = "main" })
			end,
		},
		{
			name = "sonokai",
			setup = function()
				vim.g.sonokai_style = "default"
			end,
		},
		{ name = "onenord", setup = function() end },
	}

	math.randomseed(os.time())
	local theme = themes[math.random(#themes)]
	theme.setup()
	vim.cmd("colorscheme " .. theme.name)
	vim.notify("🎨 Loaded random theme: " .. theme.name)
end)
