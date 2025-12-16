-- ========================================
-- lazy.nvim bootstrap
-- ========================================
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

-- ========================================
-- 输入法切换模块
-- ========================================
local last_input_method = nil

-- 异步执行 system 命令，避免阻塞
local function run_async(cmd, args, callback)
	local handle
	handle = vim.loop.spawn(cmd, { args = args }, function(code, signal)
		if callback then
			callback(code, signal)
		end
		if handle then
			handle:close()
		end
	end)
end

-- 获取当前输入法（异步）
local function get_current_input_method(callback)
	local stdout = vim.loop.new_pipe(false)
	local handle
	handle = vim.loop.spawn("im-select", { stdio = { nil, stdout, nil } }, function()
		stdout:close()
		if handle then
			handle:close()
		end
	end)

	local chunks = {}
	stdout:read_start(function(err, data)
		assert(not err, err)
		if data then
			table.insert(chunks, data)
		else
			local result = table.concat(chunks):gsub("\n", "")
			if callback then
				callback(result)
			end
		end
	end)
end

-- 自动切换：进入 Insert 恢复原输入法
vim.api.nvim_create_autocmd("InsertEnter", {
	callback = function()
		if not last_input_method then
			get_current_input_method(function(method)
				last_input_method = method
			end)
		elseif last_input_method then
			run_async("im-select", { last_input_method })
		end
	end,
})

-- 自动切换：退出 Insert 统一切到英文
vim.api.nvim_create_autocmd("InsertLeave", {
	callback = function()
		run_async("im-select", { "com.apple.keylayout.ABC" })
	end,
})

-- 提供手动命令 :IMToggle
vim.api.nvim_create_user_command("IMToggle", function()
	get_current_input_method(function(method)
		if method == "com.apple.keylayout.ABC" and last_input_method then
			run_async("im-select", { last_input_method })
			vim.notify("切换到上次输入法: " .. last_input_method, vim.log.levels.INFO)
		else
			run_async("im-select", { "com.apple.keylayout.ABC" })
			vim.notify("切换到英文输入法", vim.log.levels.INFO)
		end
	end)
end, {})

-- ========================================
-- lazy.nvim 插件管理
-- ========================================
require("lazy").setup({
	{ import = "dengbo.plugins" },
	{ import = "dengbo.plugins.lsp" },
}, {
	checker = { enabled = true, notify = false },
	change_detection = { notify = false },
})

-- ========================================
-- 折叠设置
-- ========================================
vim.opt.foldmethod = "expr"
vim.opt.foldexpr = "nvim_treesitter#foldexpr()"
vim.opt.foldlevel = 99
vim.opt.foldtext = "v:lua.vim.treesitter.foldtext()"

-- ========================================
-- Neovide 配置
-- ========================================
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

if vim.g.neovide then
	vim.keymap.set("n", "<D-s>", ":w<CR>")
	vim.keymap.set("v", "<D-c>", '"+y')
	vim.keymap.set("n", "<D-v>", '"+P')
	vim.keymap.set("v", "<D-v>", '"+P')
	vim.keymap.set("c", "<D-v>", "<C-R>+")
	vim.keymap.set("i", "<D-v>", '<ESC>l"+Pli')
end

vim.api.nvim_set_keymap("", "<D-v>", "+p<CR>", { noremap = true, silent = true })
vim.api.nvim_set_keymap("!", "<D-v>", "<C-R>+", { noremap = true, silent = true })
vim.api.nvim_set_keymap("t", "<D-v>", "<C-R>+", { noremap = true, silent = true })
vim.api.nvim_set_keymap("v", "<D-v>", "<C-R>+", { noremap = true, silent = true })

vim.g.transparent_groups = vim.list_extend(vim.g.transparent_groups or {}, { "ExtraGroup" })

-- ========================================
-- 随机主题加载
-- ========================================
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
