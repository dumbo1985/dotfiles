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
		config = function(_, opts)
			require("render-markdown").setup(opts)

			--------------------------------------------------------------------
			-- 任务项勾选切换：- [ ] <-> - [x]，同时支持 1. [ ] 这类有序列表
			--------------------------------------------------------------------
			local function toggle_lines(srow, erow)
				local bufnr = vim.api.nvim_get_current_buf()
				local lines = vim.api.nvim_buf_get_lines(bufnr, srow - 1, erow, false)
				local changed = 0
				for i, line in ipairs(lines) do
					local prefix, state = line:match("^(%s*[-*+]%s+)%[(.)%]")
					if not prefix then
						prefix, state = line:match("^(%s*%d+%.%s+)%[(.)%]")
					end
					if prefix then
						local next_state = (state == "x" or state == "X") and " " or "x"
						lines[i] = prefix .. "[" .. next_state .. "]" .. line:sub(#prefix + 4)
						changed = changed + 1
					end
				end
				if changed == 0 then
					vim.notify("光标下或选区内没有任务项", vim.log.levels.WARN)
					return
				end
				vim.api.nvim_buf_set_lines(bufnr, srow - 1, erow, false, lines)
			end

			vim.api.nvim_create_user_command("TodoToggle", function(args)
				toggle_lines(args.line1, args.line2)
			end, { range = true, desc = "切换 Markdown 任务项勾选状态" })

			vim.keymap.set("n", "<leader>mc", "<cmd>TodoToggle<cr>", { desc = "勾选/取消当前任务项" })
			vim.keymap.set("v", "<leader>mc", ":<C-u>TodoToggle<cr>", { desc = "勾选/取消选中的任务项" })

			--------------------------------------------------------------------
			-- 插入模式硬换行：Alt+Enter = 行尾两个空格 + 换行
			--------------------------------------------------------------------
			local function hard_break()
				local bufnr = vim.api.nvim_get_current_buf()
				local cursor = vim.api.nvim_win_get_cursor(0)
				local row, col = cursor[1], cursor[2]
				local line = vim.api.nvim_buf_get_lines(bufnr, row - 1, row, false)[1]
				vim.api.nvim_buf_set_lines(bufnr, row - 1, row, false, { line:sub(1, col) .. "  " })
				vim.api.nvim_buf_set_lines(bufnr, row, row, false, { line:sub(col + 1) })
				vim.api.nvim_win_set_cursor(0, { row + 1, 0 })
			end

			local function bind_hard_break(bufnr)
				vim.keymap.set("i", "<M-CR>", hard_break, {
					buffer = bufnr,
					desc = "Markdown 硬换行（行尾两个空格 + 换行）",
				})
			end

			vim.api.nvim_create_autocmd("FileType", {
				pattern = "markdown",
				callback = function(args)
					bind_hard_break(args.buf)
				end,
			})
			if vim.bo.filetype == "markdown" then
				bind_hard_break(0)
			end
		end,
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
