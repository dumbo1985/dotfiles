return {
	"folke/which-key.nvim",
	event = "VeryLazy",
	init = function()
		vim.o.timeout = true
		vim.o.timeoutlen = 500
	end,
	config = function()
		local whichkey = require("which-key")

		whichkey.setup({
			-- 其他配置选项
		})

		-- Normal mode keymaps
		vim.keymap.set("n", "<leader>b", function() end, { desc = "Breakpoint" })
		vim.keymap.set("n", "<leader>c", function() end, { desc = "Diff" })
		vim.keymap.set("n", "<leader>d", function() end, { desc = "Debug" })
		vim.keymap.set("n", "<leader>e", function() end, { desc = "File Explorer" })
		vim.keymap.set("n", "<leader>f", function() end, { desc = "Find" })
		vim.keymap.set("n", "<leader>g", function() end, { desc = "Blame" })
		vim.keymap.set("n", "<leader>h", function() end, { desc = "Hunk" })
		vim.keymap.set("n", "<leader>l", function() end, { desc = "LazyGit" })
		vim.keymap.set("n", "<leader>m", function() end, { desc = "Format" })
		vim.keymap.set("n", "<leader>n", function() end, { desc = "Highlights" })
		vim.keymap.set("n", "<leader>q", function() end, { desc = "Quickfix" })
		vim.keymap.set("n", "<leader>r", function() end, { desc = "Redo" })
		vim.keymap.set("n", "<leader>s", function() end, { desc = "Splite" })
		vim.keymap.set("n", "<leader>t", function() end, { desc = "Tab" })
		vim.keymap.set("n", "<leader>w", function() end, { desc = "Session" })
		vim.keymap.set("n", "<leader>x", function() end, { desc = "Trouble" })

		-- Visual mode keymaps
		vim.keymap.set("v", "<leader>de", "<cmd>lua require'dapui'.eval()<cr>", { desc = "Evaluate" })
	end,
}
