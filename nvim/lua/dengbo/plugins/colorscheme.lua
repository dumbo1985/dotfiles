-- plugins/theme-randomizer.lua
return {
	-- 默认主题：启动时加载，保证首屏稳定
	{
		"folke/tokyonight.nvim",
		lazy = false,
		priority = 1000,
	},
	-- 其它主题按需加载（:colorscheme xxx 时再加载）
	{
		"rebelot/kanagawa.nvim",
		lazy = true,
	},
	{
		"catppuccin/nvim",
		name = "catppuccin",
		lazy = true,
	},
	{
		"rose-pine/neovim",
		name = "rose-pine",
		lazy = true,
	},
	{
		"sainnhe/sonokai",
		lazy = true,
	},
	{
		"rmehri01/onenord.nvim",
		lazy = true,
	},
}
