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
	checker = { enabled = true, notify = false },
	change_detection = { notify = false },
})

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
