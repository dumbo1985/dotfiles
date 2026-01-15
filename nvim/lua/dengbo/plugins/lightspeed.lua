return {
	{
		"ggandor/lightspeed.nvim",
		event = "VeryLazy",
		config = function()
			require("lightspeed").setup({
				jump_to_unique_chars = false,
				safe_labels = { "f", "d", "s", "j", "k", "l", "a", "n", "e", "i", "w", "o" },
				labels = {},
				ignore_case = true,
				match_only_the_start_of_same_char_seqs = true,
				limit_ft_matches = 5,
				multi_window = true,
				greywash = false,
			})

			vim.cmd([[
        highlight! link LightspeedUniqueChar LightspeedLabel
      ]])

			-- 修改快捷键为 f 和 F
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
