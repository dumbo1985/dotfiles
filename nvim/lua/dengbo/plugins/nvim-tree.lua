return {
	"nvim-tree/nvim-tree.lua",
	dependencies = "nvim-tree/nvim-web-devicons",
	config = function()
		local nvimtree = require("nvim-tree")

		-- recommended settings from nvim-tree documentation
		vim.g.loaded_netrw = 1
		vim.g.loaded_netrwPlugin = 1

		nvimtree.setup({
			sort_by = "case_sensitive",
			on_attach = on_attach,

			view = {
				width = 40,
				relativenumber = true,
				side = "left",
				signcolumn = "yes",
			},

			-- project plugin 需要这样设置
			update_cwd = true,
			update_focused_file = {
				enable = true,
				update_cwd = true,
			},

			-- change folder arrow icons
			renderer = {
				group_empty = true,
				indent_markers = {
					enable = true,
				},
				icons = {
					glyphs = {
						folder = {
							arrow_closed = "", -- arrow when folder is closed
							arrow_open = "", -- arrow when folder is open
						},
					},
				},
			},
			-- disable window_picker for
			-- explorer to work well with
			-- window splits
			actions = {
				open_file = {
					window_picker = {
						enable = false,
					},
				},
			},
			filters = {
				custom = { ".DS_Store" },
			},
			git = {
				ignore = false,
			},

			system_open = {
				cmd = "open",
			},
		})
	end,
}
