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
-- lazy.nvim 插件管理
-- ========================================
require("lazy").setup({
	{ import = "dengbo.plugins" },
	{ import = "dengbo.plugins.lsp" },
}, {
	defaults = {
		-- 未显式指定 lazy 的插件默认延迟加载；需立即加载的插件在各自 spec 里写 lazy = false
		lazy = true,
	},
	checker = { enabled = false, notify = false },
	change_detection = { notify = false },
	-- 安装/更新插件时若缺少 colorscheme，优先保证默认主题可用
	install = { colorscheme = { "tokyonight" } },
})

-- ========================================
-- 随机主题加载
-- ========================================
vim.schedule(function()
	local themes = {
		-- Explicit variants avoid counting aliases of the same palette twice.
		"tokyonight-night",
		"tokyonight-storm",
		"tokyonight-moon",
		"kanagawa-wave",
		"kanagawa-dragon",
		"catppuccin-mocha",
		"catppuccin-macchiato",
		"catppuccin-frappe",
		"rose-pine-main",
		"rose-pine-moon",
		"sonokai",
		"onenord",
		"gruvbox",
		"nightfox",
		"duskfox",
		"nordfox",
		"terafox",
		"carbonfox",
		"everforest",
		"nord",
		"dracula",
		"dracula-soft",
		"github_dark_default",
		"github_dark_dimmed",
		"github_dark_high_contrast",
		"onedark",
		"material-oceanic",
		"material-palenight",
		"material-deep-ocean",
		"material-darker",
		"nordic",
		"moonfly",
		"nightfly",
		"ayu-dark",
		"ayu-mirage",
		"night-owl",
		"gruvbox-material",
		"edge",
		"vscode",
		"adwaita",
		"vague",
		"modus_vivendi",
		"tokyodark",
		"oxocarbon",
		"evergarden",
		"mellifluous",
		"bamboo",
		"melange",
		"monokai-pro",
		"poimandres",
	}
	math.randomseed(vim.loop.hrtime())
	local chosen = themes[math.random(#themes)]
	if not pcall(vim.cmd.colorscheme, chosen) then
		vim.cmd.colorscheme("tokyonight")
	end
end)
