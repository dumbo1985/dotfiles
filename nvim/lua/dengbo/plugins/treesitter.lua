return {
	"nvim-treesitter/nvim-treesitter",
	-- main 分支为不兼容重写，无 nvim-treesitter.configs；本配置沿用旧版 API（与 nvim-ts-autotag、telescope-dap 等一致）
	branch = "master",
	event = { "BufReadPre", "BufNewFile" },
	build = ":TSUpdate",
	dependencies = {
		"windwp/nvim-ts-autotag",
	},
	opts = {
		auto_install = false,
		highlight = {
			enable = true,
		},
		indent = { enable = true },
		autotag = {
			enable = true,
		},
		ensure_installed = {
			"json",
			"javascript",
			"typescript",
			"tsx",
			"yaml",
			"html",
			"css",
			"prisma",
			"markdown",
			"markdown_inline",
			"svelte",
			"graphql",
			"bash",
			"lua",
			"vim",
			"dockerfile",
			"gitignore",
			"query",
			"vimdoc",
			"c",
			"go",
			"cpp",
			"python",
		},
		sync_install = false,
		incremental_selection = {
			enable = true,
			keymaps = {
				init_selection = "<C-space>",
				node_incremental = "<C-space>",
				scope_incremental = false,
				node_decremental = "<bs>",
			},
		},
	},
	config = function(_, opts)
		require("nvim-treesitter.configs").setup(opts)
	end,
}
