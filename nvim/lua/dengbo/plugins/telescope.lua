return {
	"nvim-telescope/telescope.nvim",
	-- 0.1.x 分支早已停止维护，它的预览器调用 nvim-treesitter 旧 API
	-- （parsers.ft_to_lang / configs.is_enabled），与 nvim-treesitter main 分支
	-- 及 Neovim 0.12 不兼容（live_grep 预览报 attempt to call field 'ft_to_lang'）。
	-- 官方默认分支 master 才是长期维护分支。
	-- 不锁分支：跟随官方默认分支（当前为 master）。0.1.x 是 2023 年冻结的历史分支，不要锁回它。
	cmd = "Telescope",
	dependencies = {
		"nvim-lua/plenary.nvim",
		-- telescope-dap 的预览会用到 treesitter；须在首次 :Telescope 前已加载
		"nvim-treesitter/nvim-treesitter",
		{ "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
		"nvim-tree/nvim-web-devicons",
		"folke/todo-comments.nvim",
		"nvim-telescope/telescope-dap.nvim",
	},
	config = function()
		local telescope = require("telescope")
		local actions = require("telescope.actions")

		telescope.setup({
			defaults = {
				path_display = { "smart" },
				mappings = {
					i = {
						["<C-k>"] = actions.move_selection_previous, -- move to prev result
						["<C-j>"] = actions.move_selection_next, -- move to next result
						["<C-q>"] = actions.send_selected_to_qflist + actions.open_qflist,
					},
				},
			},
		})

		telescope.load_extension("fzf")
		pcall(telescope.load_extension, "dap")
	end,
}
