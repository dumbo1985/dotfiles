return {
	"akinsho/bufferline.nvim",
	dependencies = { "nvim-tree/nvim-web-devicons" },
	version = "*",

	config = function()
		local bufferline = require("bufferline")

		bufferline.setup({
			options = {
				-- Make sure nvim-tree can show in the left
				offsets = {
					{
						filetype = "NvimTree",
						text = "【自歌自舞自开怀 无拘无束无碍】",
						highlight = "Directory",
						text_align = "left",
						separator = true,
					},
				},

				close_command = "bdelete! %d", -- 点击关闭按钮关闭
				right_mouse_command = "bdelete! %d", -- 右键点击关闭
				indicator = {
					icon = "▎", -- 分割线
					style = "underline",
				},

				buffer_close_icon = "󰅖",
				modified_icon = "●",
				close_icon = "",
			},
		})
	end,
}
