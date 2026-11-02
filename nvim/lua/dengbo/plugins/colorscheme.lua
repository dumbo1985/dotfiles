-- Keep these plugins in sync with the random theme list in dengbo/lazy.lua.
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
	{
		"ellisonleao/gruvbox.nvim",
		lazy = true,
	},
	{
		"EdenEast/nightfox.nvim",
		lazy = true,
	},
	{
		"sainnhe/everforest",
		lazy = true,
	},
	{
		"shaunsingh/nord.nvim",
		lazy = true,
	},
	{
		"Mofiqul/dracula.nvim",
		lazy = true,
	},
	{
		"projekt0n/github-nvim-theme",
		lazy = true,
	},
	{
		"navarasu/onedark.nvim",
		lazy = true,
	},
	{
		"marko-cerovac/material.nvim",
		lazy = true,
	},
	{
		"AlexvZyl/nordic.nvim",
		lazy = true,
	},
	{
		"bluz71/vim-moonfly-colors",
		name = "moonfly",
		lazy = true,
	},
	{
		"bluz71/vim-nightfly-colors",
		name = "nightfly",
		lazy = true,
	},
	{
		"Shatur/neovim-ayu",
		lazy = true,
	},
	{
		"oxfist/night-owl.nvim",
		lazy = true,
		opts = {},
	},
	{
		"sainnhe/gruvbox-material",
		lazy = true,
	},
	{
		"sainnhe/edge",
		lazy = true,
	},
	{
		"Mofiqul/vscode.nvim",
		lazy = true,
	},
	{
		"Mofiqul/adwaita.nvim",
		lazy = true,
	},
	{
		"vague-theme/vague.nvim",
		lazy = true,
	},
	{
		"miikanissi/modus-themes.nvim",
		lazy = true,
	},
	{
		"tiagovla/tokyodark.nvim",
		lazy = true,
	},
	{
		"nyoom-engineering/oxocarbon.nvim",
		lazy = true,
		-- The repository already contains generated Lua; no LuaRocks build is needed.
		build = false,
	},
	{
		"comfysage/evergarden",
		lazy = true,
	},
	{
		"ramojus/mellifluous.nvim",
		lazy = true,
	},
	{
		"ribru17/bamboo.nvim",
		lazy = true,
	},
	{
		"savq/melange-nvim",
		lazy = true,
	},
	{
		"loctvl842/monokai-pro.nvim",
		lazy = true,
	},
	{
		"olivercederborg/poimandres.nvim",
		lazy = true,
	},
}
