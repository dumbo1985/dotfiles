return {
	"folke/flash.nvim",
	event = "VeryLazy",
	opts = {
		modes = {
			char = {
				enabled = false, -- 禁用字符模式，使用 lightspeed
			},
		},
		-- 启用全窗口跳转
		search = {
			multi_window = true, -- 支持跨窗口搜索
		},
	},
	keys = {
		-- 禁用默认的 s/S 映射，避免冲突
		{ "s", mode = { "n", "x", "o" }, false },
		{ "S", mode = { "n", "x", "o" }, false },
		-- 使用 <leader>j 作为 Flash 跳转
		{
			"<leader>j",
			mode = { "n", "x", "o" },
			function()
				require("flash").jump({
					search = {
						mode = "search", -- 使用搜索模式
						max_length = false,
					},
					label = {
						after = { 0, 0 },
					},
					pattern = [[\<]], -- 匹配单词开头
					multi_window = true, -- 全窗口搜索
				})
			end,
			desc = "Flash 跳转（全窗口，无需输入字符）",
		},
		{
			"<leader>J",
			mode = { "n", "x", "o" },
			function()
				require("flash").jump({
					search = {
						mode = "search",
						max_length = false,
					},
					label = {
						after = { 0, 0 },
					},
					pattern = [[\<]],
					jump = {
						pos = "end",
					},
					multi_window = true,
				})
			end,
			desc = "Flash 跳转（向后，全窗口）",
		},
		{
			"<leader>jr",
			mode = "o",
			function()
				require("flash").remote()
			end,
			desc = "Flash 远程操作",
		},
		{
			"<leader>jR",
			mode = { "o", "x" },
			function()
				require("flash").treesitter()
			end,
			desc = "Flash Treesitter 搜索",
		},
		{
			"<c-s>",
			mode = { "c" },
			function()
				require("flash").toggle()
			end,
			desc = "切换 Flash 搜索",
		},
	},
}
