-- set leader key to space
vim.g.mapleader = " "

local keymap = vim.keymap -- for conciseness

---------------------
-- General Keymaps -------------------
keymap.set("n", "n", "nzzzv", { desc = "跳转下一个搜索项并居中" })
keymap.set("n", "N", "Nzzzv", { desc = "跳转上一个搜索项并居中" })
keymap.set("n", "G", "Gzz", { desc = "跳转文件末尾并居中" })
keymap.set("n", "<C-d>", "<C-d>zz", { desc = "向下滚动并居中" })
keymap.set("n", "<C-u>", "<C-u>zz", { desc = "向上滚动并居中" })

-- General keymaps
keymap.set("i", "jk", "<ESC>") -- 通过 jk 退出插入模式
keymap.set("i", "ii", "<ESC>") -- 通过 ii 退出插入模式
keymap.set("n", "<leader>wq", ":wq<CR>", { desc = "保存并退出" })
keymap.set("n", "<leader>qq", ":q!<CR>", { desc = "强制退出不保存" })
keymap.set("n", "<leader>ww", ":w<CR>", { desc = "保存" })
keymap.set("n", "gx", ":!open <c-r><c-a><CR>") -- 打开光标下的链接

-- 清除搜索高亮
keymap.set("n", "<leader>nh", ":nohl<CR>", { desc = "清除搜索高亮" })

-- 增加/减少数字
keymap.set("n", "<leader>+", "<C-a>", { desc = "数字加一" })
keymap.set("n", "<leader>-", "<C-x>", { desc = "数字减一" })

-- 分屏管理
keymap.set("n", "<leader>sv", "<C-w>v", { desc = "垂直分屏" })
keymap.set("n", "<leader>sh", "<C-w>s", { desc = "水平分屏" })
keymap.set("n", "<leader>se", "<C-w>=", { desc = "使分屏大小相等" })
keymap.set("n", "<leader>sx", "<cmd>close<CR>", { desc = "关闭当前分屏" })
keymap.set("n", "<leader>sj", "<C-w>-", { desc = "减小分屏高度" })
keymap.set("n", "<leader>sk", "<C-w>+", { desc = "增加分屏高度" })
keymap.set("n", "<leader>sl", "<C-w>>5", { desc = "增加分屏宽度" })
keymap.set("n", "<leader>ss", "<C-w><5", { desc = "减小分屏宽度" })

-- 最大化窗口
keymap.set("n", "<leader>sm", ":MaximizerToggle<CR>", { desc = "切换最大化窗口" })

-- 标签页管理
keymap.set("n", "<leader>td", ":bp | bd #<CR>", { desc = "关闭当前缓冲区但保留标签页" })
keymap.set("n", "<leader>tl", ":Telescope buffers<CR>", { desc = "列出所有缓冲区" })
keymap.set("n", "<leader>to", "<cmd>tabnew<CR>", { desc = "打开新标签页" })
keymap.set("n", "<leader>tx", "<cmd>tabclose<CR>", { desc = "关闭当前标签页" })
keymap.set("n", "<leader>tf", "<cmd>tabnew %<CR>", { desc = "当前缓冲区新开标签页" })
keymap.set("n", "<leader>tp", ":BufferLineCyclePrev<CR>", { desc = "切换到上一个标签页(左上角)" })
keymap.set("n", "<leader>tn", ":BufferLineCycleNext<CR>", { desc = "切换到下一个标签页（左上角）" })
keymap.set("n", "<leader>t]", "gt", { desc = "切换到下一个标签页(右上角)" })
keymap.set("n", "<leader>t[", "gT", { desc = "切换到上一个标签页(右上角)" })
keymap.set("n", "<leader>th", ":BufferLineMovePrev<CR>", { desc = "缓冲区向左移动" })
keymap.set("n", "<leader>tr", ":BufferLineMoveNext<CR>", { desc = "缓冲区向右移动" })

-- Diff操作
keymap.set("n", "<leader>cc", ":diffput<CR>", { desc = "把改动放到另一个缓冲区" })
keymap.set("n", "<leader>cj", ":diffget 1<CR>", { desc = "从左边取改动" })
keymap.set("n", "<leader>ck", ":diffget 3<CR>", { desc = "从右边取改动" })
keymap.set("n", "<leader>cn", "]c", { desc = "跳转到下一个差异块" })
keymap.set("n", "<leader>cp", "[c", { desc = "跳转到上一个差异块" })

-- NvimTree 文件树
keymap.set("n", "<leader>ee", "<cmd>NvimTreeToggle<CR>", { desc = "切换文件资源管理器" })
keymap.set("n", "<leader>ec", "<cmd>NvimTreeCollapse<CR>", { desc = "收起文件资源管理器" })
keymap.set("n", "<leader>er", "<cmd>NvimTreeRefresh<CR>", { desc = "刷新文件资源管理器" })
keymap.set("n", "<leader>eo", ":NvimTreeFocus<CR>", { desc = "聚焦文件资源管理器" })
keymap.set("n", "<leader>ef", ":NvimTreeFindFile<CR>", { desc = "在文件资源管理器中定位文件" })

-- Telescope 模糊搜索
keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "查找文件" })
keymap.set("n", "<leader>fr", "<cmd>Telescope oldfiles<cr>", { desc = "查找最近打开的文件" })
keymap.set("n", "<leader>fs", "<cmd>Telescope live_grep<cr>", { desc = "全局搜索字符串" })
keymap.set("n", "<leader>fc", "<cmd>Telescope grep_string<cr>", { desc = "搜索光标下的字符串" })
keymap.set("n", "<leader>ft", "<cmd>TodoTelescope<cr>", { desc = "查找 TODO" })

-- Quickfix
keymap.set("n", "<leader>qo", ":copen<CR>", { desc = "打开 quickfix 列表" })
keymap.set("n", "<leader>qf", ":cfirst<CR>", { desc = "跳转到第一个 quickfix 项" })
keymap.set("n", "<leader>qn", ":cnext<CR>", { desc = "跳转到下一个 quickfix 项" })
keymap.set("n", "<leader>qp", ":cprev<CR>", { desc = "跳转到上一个 quickfix 项" })
keymap.set("n", "<leader>ql", ":clast<CR>", { desc = "跳转到最后一个 quickfix 项" })
keymap.set("n", "<leader>qc", ":cclose<CR>", { desc = "关闭 quickfix 列表" })

-- Git blame
keymap.set("n", "<leader>gb", ":GitBlameToggle<CR>", { desc = "切换 Git 责任人显示" })

-- LSP
keymap.set("n", "<leader>gg", "<cmd>lua vim.lsp.buf.hover()<CR>", { desc = "悬停提示" })
keymap.set("n", "gd", "<cmd>lua vim.lsp.buf.definition()<CR>", { desc = "跳转到定义" })
keymap.set("n", "gD", "<cmd>lua vim.lsp.buf.declaration()<CR>", { desc = "跳转到声明" })
keymap.set("n", "gi", "<cmd>lua vim.lsp.buf.implementation()<CR>", { desc = "跳转到实现" })
keymap.set("n", "gt", "<cmd>lua vim.lsp.buf.type_definition()<CR>", { desc = "跳转到类型定义" })
keymap.set("n", "gr", "<cmd>lua vim.lsp.buf.references()<CR>", { desc = "查找引用" })
keymap.set("n", "gs", "<cmd>lua vim.lsp.buf.signature_help()<CR>", { desc = "函数签名提示" })
keymap.set("n", "rr", "<cmd>lua vim.lsp.buf.rename()<CR>", { desc = "重命名" })
keymap.set("n", "gf", "<cmd>lua vim.lsp.buf.format({async = true})<CR>", { desc = "格式化文件" })
keymap.set("v", "gf", "<cmd>lua vim.lsp.buf.format({async = true})<CR>", { desc = "格式化选中内容" })
keymap.set("n", "ga", "<cmd>lua vim.lsp.buf.code_action()<CR>", { desc = "代码操作" })
keymap.set("n", "gl", "<cmd>lua vim.diagnostic.open_float()<CR>", { desc = "显示诊断信息" })
keymap.set("n", "gp", "<cmd>lua vim.diagnostic.goto_prev()<CR>", { desc = "跳转到上一个诊断" })
keymap.set("n", "gn", "<cmd>lua vim.diagnostic.goto_next()<CR>", { desc = "跳转到下一个诊断" })
keymap.set("n", "tr", "<cmd>lua vim.lsp.buf.document_symbol()<CR>", { desc = "文档符号列表" })
keymap.set("i", "<C-Space>", "<cmd>lua vim.lsp.buf.completion()<CR>", { desc = "补全" })

-- 文件类型特定操作
keymap.set("n", "<leader>go", function()
	if vim.bo.filetype == "python" then
		vim.api.nvim_command("PyrightOrganizeImports")
	end
end, { desc = "整理导入 (Python)" })

keymap.set("n", "<leader>tc", function()
	if vim.bo.filetype == "python" then
		require("dap-python").test_class()
	end
end, { desc = "测试当前类 (Python)" })

keymap.set("n", "<leader>tm", function()
	if vim.bo.filetype == "python" then
		require("dap-python").test_method()
	end
end, { desc = "测试当前方法 (Python)" })

-- 调试相关
keymap.set("n", "<leader>db", "<cmd>lua require'dap'.toggle_breakpoint()<cr>", { desc = "切换断点" })
keymap.set(
	"n",
	"<leader>bc",
	"<cmd>lua require'dap'.set_breakpoint(vim.fn.input('断点条件: '))<cr>",
	{ desc = "设置条件断点" }
)
keymap.set(
	"n",
	"<leader>bl",
	"<cmd>lua require'dap'.set_breakpoint(nil, nil, vim.fn.input('日志点信息: '))<cr>",
	{ desc = "设置日志点" }
)
keymap.set("n", "<leader>br", "<cmd>lua require'dap'.clear_breakpoints()<cr>", { desc = "清除所有断点" })
keymap.set("n", "<leader>ba", "<cmd>Telescope dap list_breakpoints<cr>", { desc = "列出所有断点" })
keymap.set("n", "<leader>dc", "<cmd>lua require'dap'.continue()<cr>", { desc = "继续运行" })
keymap.set("n", "<leader>dj", "<cmd>lua require'dap'.step_over()<cr>", { desc = "单步跳过" })
keymap.set("n", "<leader>dk", "<cmd>lua require'dap'.step_into()<cr>", { desc = "单步进入" })
keymap.set("n", "<leader>do", "<cmd>lua require'dap'.step_out()<cr>", { desc = "跳出函数" })
keymap.set("n", "<leader>dd", function()
	require("dap").disconnect()
	require("dapui").close()
end, { desc = "断开调试" })
keymap.set("n", "<leader>dt", function()
	require("dap").terminate()
	require("dapui").close()
end, { desc = "结束调试" })
keymap.set("n", "<leader>dp", "<cmd>lua require'dap'.repl.toggle()<cr>", { desc = "切换 REPL" })
keymap.set("n", "<leader>dl", "<cmd>lua require'dap'.run_last()<cr>", { desc = "运行上一次调试" })
keymap.set("n", "<leader>di", function()
	require("dap.ui.widgets").hover()
end, { desc = "调试悬停变量" })
keymap.set("n", "<leader>d?", function()
	local widgets = require("dap.ui.widgets")
	widgets.centered_float(widgets.scopes)
end, { desc = "浮动显示变量作用域" })
keymap.set("n", "<leader>df", "<cmd>Telescope dap frames<cr>", { desc = "查看调用栈" })
keymap.set("n", "<leader>dh", "<cmd>Telescope dap commands<cr>", { desc = "查看调试命令" })
keymap.set("n", "<leader>de", function()
	require("telescope.builtin").diagnostics({ default_text = ":E:" })
end, { desc = "查找调试错误信息" })

---------------------
-- ✨ 头文件和 CPP 文件跳转 ✨
---------------------
keymap.set("n", "<leader>ch", function()
	vim.cmd("ClangdSwitchSourceHeader")
end, { desc = "切换源文件/头文件" })
