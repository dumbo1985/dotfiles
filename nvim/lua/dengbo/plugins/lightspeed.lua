return {
	{
		"ggandor/lightspeed.nvim",
		event = "VeryLazy",
		config = function()
			require("lightspeed").setup({
				-- 核心跳转行为
				jump_to_unique_chars = false, -- 必须输入两个字符才跳转（防止误跳）
				safe_labels = { "f", "d", "s", "j", "k", "l", "a", "n", "e", "i", "w", "o" }, -- 显示易按的标签
				labels = {}, -- 不显示其他标签（避免干扰）

				-- 搜索匹配优化
				ignore_case = true, -- 忽略大小写
				match_only_the_start_of_same_char_seqs = true, -- 优化连续相同字符匹配
				limit_ft_matches = 5, -- 限制可见匹配数（防止屏幕混乱）

				-- 多窗口支持
				multi_window = true, -- 支持跨窗口跳转

				-- 禁用灰色背景（旧版 grey_out_search_area 的替代方案）
				greywash = false, -- 直接禁用灰显功能
			})

			-- 手动设置高亮组（替代旧版 highlight_unique_chars）
			vim.api.nvim_set_hl(0, "LightspeedUniqueChar", { link = "LightspeedLabel" })

			-- 强化键位映射
			vim.keymap.set({ "n", "x", "o" }, "f", "<Plug>Lightspeed_s", {
				silent = true,
				noremap = true,
				desc = "Lightspeed forward search",
			})
			vim.keymap.set({ "n", "x", "o" }, "F", "<Plug>Lightspeed_S", {
				silent = true,
				noremap = true,
				desc = "Lightspeed backward search",
			})
		end,
	},
}
