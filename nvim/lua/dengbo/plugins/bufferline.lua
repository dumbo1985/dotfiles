return {
	"akinsho/bufferline.nvim",
	dependencies = { "nvim-tree/nvim-web-devicons" },
	version = "*",
	opts = {
		options = {
			numbers = "ordinal", --use ordinal

			indicator = {
				icon = "▎", -- this should be omitted if indicator style is not 'icon'
				style = "icon",
			},

			diagnostics = "nvim-lsp", -- Use nvim-lsp
			-- Make sure nvim-tree can show in the left
			offsets = {
				{
					filetype = "NvimTree",
					text = "【自歌自舞自开怀 无拘无束无碍】",
					highlight = "Directory",
					text_align = "left",
				},
			},

			mode = "tabs",
			separator_style = "slant",
		},
	},
}
