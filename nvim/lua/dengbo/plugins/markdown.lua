return {
	{
		"MeanderingProgrammer/render-markdown.nvim",
		ft = { "markdown" },
		dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-tree/nvim-web-devicons" },
		opts = {
			checkbox = {
				checked = { icon = "󰱒 " },
				unchecked = { icon = "󰄱 " },
			},
			heading = { sign = false },
		},
		keys = {
			{ "<leader>mt", "<cmd>RenderMarkdown toggle<cr>", desc = "切换 Markdown 渲染" },
		},
	},
	{
		"iamcco/markdown-preview.nvim",
		ft = { "markdown" },
		-- The Node fallback used when the prebuilt binary is unavailable needs app dependencies.
		build = "cd app && npm install",
		init = function()
			vim.g.mkdp_filetypes = { "markdown" }
			vim.g.mkdp_auto_close = 0
		end,
		keys = {
			{ "<leader>mp", "<cmd>MarkdownPreviewToggle<cr>", desc = "切换 Markdown 浏览器预览" },
		},
	},
}
