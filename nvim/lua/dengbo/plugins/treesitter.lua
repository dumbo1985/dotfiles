return {
	"nvim-treesitter/nvim-treesitter",
	-- nvim-treesitter 的 main 分支是完全不兼容的重写版（v1）：
	--   要求 Neovim 0.12+ 与 tree-sitter-cli 0.26.1+，且明确不支持懒加载。
	--   master 分支已冻结，官方 README 写明 "Neovim 0.12 is not supported"，
	--   在 0.12 上会报 languagetree.lua 里 method 'range' 为 nil 的错。
	-- 不锁分支：跟随官方默认分支（当前为 main）。若哪天官方把默认分支切回 master，
	-- 这里就必须显式写 branch = "main"，否则会退回不兼容的旧版。
	lazy = false,
	build = ":TSUpdate",
	dependencies = {
		"windwp/nvim-ts-autotag",
	},
	config = function()
		require("nvim-treesitter").setup({
			install_dir = vim.fn.stdpath("data") .. "/site",
		})

		-- main 分支没有 ensure_installed，用 install() 异步补齐缺失的 parser
		-- （已安装时是 no-op，不会每次启动都重新编译）
		vim.schedule(function()
			require("nvim-treesitter").install({
				"json",
				"javascript",
				"typescript",
				"tsx",
				"yaml",
				"html",
				"css",
				"prisma",
				"markdown",
				"markdown_inline",
				"svelte",
				"graphql",
				"bash",
				"lua",
				"vim",
				"dockerfile",
				"gitignore",
				"query",
				"vimdoc",
				"c",
				"go",
				"cpp",
				"python",
			})
		end)

		-- 高亮：main 分支不再自带 highlight 模块，改由 Neovim 提供，需要显式 start
		vim.api.nvim_create_autocmd("FileType", {
			group = vim.api.nvim_create_augroup("dengbo_treesitter", { clear = true }),
			callback = function()
				pcall(vim.treesitter.start)
			end,
		})

		-- 缩进：main 分支提供的 indentexpr（官方标注为实验性）
		vim.api.nvim_create_autocmd("FileType", {
			group = "dengbo_treesitter",
			callback = function()
				vim.bo.indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
			end,
		})

		-- 自动补全 HTML/XML 标签：main 分支里不再走 nvim-treesitter.configs，独立 setup
		require("nvim-ts-autotag").setup({})

		-- main 分支移除了 incremental_selection 模块，这里用内置 API 复刻：
		-- <C-space> 从光标所在节点逐层扩展到父节点，visual 模式下 <BS> 缩回上一层
		local sel_stack = setmetatable({}, { __mode = "k" })

		local function select_node(node)
			local srow, scol, erow, ecol = vim.treesitter.get_node_range(node)
			vim.api.nvim_win_set_cursor(0, { srow + 1, scol })
			vim.cmd("normal! v")
			vim.api.nvim_win_set_cursor(0, { erow + 1, math.max(ecol - 1, 0) })
		end

		vim.keymap.set({ "n", "x" }, "<C-space>", function()
			local bufnr = vim.api.nvim_get_current_buf()
			local stack = sel_stack[bufnr]
			local node
			if vim.fn.mode() == "n" or not stack or #stack == 0 then
				local ok, cur = pcall(vim.treesitter.get_node)
				if not ok or not cur then
					return
				end
				stack = { cur }
				node = cur
			else
				local parent = stack[#stack]:parent()
				node = parent or stack[#stack]
				if parent then
					stack[#stack + 1] = parent
				end
			end
			sel_stack[bufnr] = stack
			select_node(node)
		end, { desc = "Treesitter 递增选区" })

		vim.keymap.set("x", "<bs>", function()
			local bufnr = vim.api.nvim_get_current_buf()
			local stack = sel_stack[bufnr]
			if stack and #stack > 1 then
				table.remove(stack)
				select_node(stack[#stack])
			else
				sel_stack[bufnr] = nil
				vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes("<Esc>", true, false, true), "x", false)
			end
		end, { desc = "Treesitter 递减选区" })
	end,
}
