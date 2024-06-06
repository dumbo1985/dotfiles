-- set leader key to space
vim.g.mapleader = " "

local keymap = vim.keymap -- for conciseness

---------------------
-- General Keymaps -------------------

-- General keymaps
keymap.set("i", "jk", "<ESC>") -- exit insert mode with jk
keymap.set("i", "ii", "<ESC>") -- exit insert mode with ii
keymap.set("n", "<leader>wq", ":wq<CR>", { desc = "save and quit" }) -- save and quit
keymap.set("n", "<leader>qq", ":q!<CR>", { desc = "quit without saving" }) -- quit without saving
keymap.set("n", "<leader>ww", ":w<CR>", { desc = "save" }) -- save
keymap.set("n", "gx", ":!open <c-r><c-a><CR>") -- open URL under cursor

-- clear search highlights
keymap.set("n", "<leader>nh", ":nohl<CR>", { desc = "Clear search highlights" })

-- delete single character without copying into register
-- keymap.set("n", "x", '"_x')

-- increment/decrement numbers
keymap.set("n", "<leader>+", "<C-a>", { desc = "Increment number" }) -- increment
keymap.set("n", "<leader>-", "<C-x>", { desc = "Decrement number" }) -- decrement

-- Split window management
keymap.set("n", "<leader>sv", "<C-w>v", { desc = "Split window vertically" }) -- split window vertically
keymap.set("n", "<leader>sh", "<C-w>s", { desc = "Split window horizontally" }) -- split window horizontally
keymap.set("n", "<leader>se", "<C-w>=", { desc = "Make splits equal size" }) -- make split windows equal width & height
keymap.set("n", "<leader>sx", "<cmd>close<CR>", { desc = "Close current split" }) -- close current split window
keymap.set("n", "<leader>sj", "<C-w>-", { desc = " make split window height shorter" }) -- make split window height shorter
keymap.set("n", "<leader>sk", "<C-w>+", { desc = "make split windows height taller" }) -- make split windows height taller
keymap.set("n", "<leader>sl", "<C-w>>5", { desc = "make split windows width bigger" }) -- make split windows width bigger
keymap.set("n", "<leader>ss", "<C-w><5", { desc = "make split windows width smaller" }) -- make split windows width smaller

-- Vim-maximizer
keymap.set("n", "<leader>sm", ":MaximizerToggle<CR>", { desc = "toggle maximize tab" }) -- toggle maximize tab

-- Tab management
keymap.set("n", "<leader>to", "<cmd>tabnew<CR>", { desc = "Open new tab" }) -- open new tab
keymap.set("n", "<leader>tx", "<cmd>tabclose<CR>", { desc = "Close current tab" }) -- close current tab
-- keymap.set("n", "<leader>tn", "<cmd>tabn<CR>", { desc = "Go to next tab" }) --  go to next tab
-- keymap.set("n", "<leader>tp", "<cmd>tabp<CR>", { desc = "Go to previous tab" }) --  go to previous tab
keymap.set("n", "<leader>tf", "<cmd>tabnew %<CR>", { desc = "Open current buffer in new tab" }) --  move current buffer to new tab
keymap.set("n", "<leader>tp", ":BufferLineCyclePrev<CR>", { desc = "Go to next tab" }) --  go to next tab
keymap.set("n", "<leader>tn", ":BufferLineCycleNext<CR>", { desc = "Go to previous tab" }) --  go to previous tab

-- Diff keymaps
keymap.set("n", "<leader>cc", ":diffput<CR>", { desc = "put diff from current to other during diff" }) -- put diff from current to other during diff
keymap.set("n", "<leader>cj", ":diffget 1<CR>", { desc = "get diff from left (local) during merge" }) -- get diff from left (local) during merge
keymap.set("n", "<leader>ck", ":diffget 3<CR>", { desc = "get diff from right (remote) during merge" }) -- get diff from right (remote) during merge
keymap.set("n", "<leader>cn", "]c", { desc = "next diff hunk" }) -- next diff hunk
keymap.set("n", "<leader>cp", "[c", { desc = "previous diff hunk" }) -- previous diff hunk

-- Nvim-tree
keymap.set("n", "<leader>ee", "<cmd>NvimTreeToggle<CR>", { desc = "Toggle file explorer" }) -- toggle file explorer
-- keymap.set("n", "<leader>ef", "<cmd>NvimTreeFindFileToggle<CR>", { desc = "Toggle file explorer on current file" }) -- toggle file explorer on current file
keymap.set("n", "<leader>ec", "<cmd>NvimTreeCollapse<CR>", { desc = "Collapse file explorer" }) -- collapse file explorer
keymap.set("n", "<leader>er", "<cmd>NvimTreeRefresh<CR>", { desc = "Refresh file explorer" }) -- refresh file explorer
keymap.set("n", "<leader>eo", ":NvimTreeFocus<CR>", { desc = "toggle focus to file explorer" }) -- toggle focus to file explorer
keymap.set("n", "<leader>ef", ":NvimTreeFindFile<CR>", { desc = "find file in file explorer" }) -- find file in file explorer

-- Telescope
keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "Fuzzy find files in cwd" })
keymap.set("n", "<leader>fr", "<cmd>Telescope oldfiles<cr>", { desc = "Fuzzy find recent files" })
keymap.set("n", "<leader>fs", "<cmd>Telescope live_grep<cr>", { desc = "Find string in cwd" })
keymap.set("n", "<leader>fc", "<cmd>Telescope grep_string<cr>", { desc = "Find string under cursor in cwd" })
keymap.set("n", "<leader>ft", "<cmd>TodoTelescope<cr>", { desc = "Find todos" })

-- Quickfix keymaps
keymap.set("n", "<leader>qo", ":copen<CR>", { desc = "open quickfix list" }) -- open quickfix list
keymap.set("n", "<leader>qf", ":cfirst<CR>", { desc = "jump to first quickfix list item" }) -- jump to first quickfix list item
keymap.set("n", "<leader>qn", ":cnext<CR>", { desc = "jump to next quickfix list item" }) -- jump to next quickfix list item
keymap.set("n", "<leader>qp", ":cprev<CR>", { desc = "jump to prev quickfix list item" }) -- jump to prev quickfix list item
keymap.set("n", "<leader>ql", ":clast<CR>", { desc = "jump to last quickfix list item" }) -- jump to last quickfix list item
keymap.set("n", "<leader>qc", ":cclose<CR>", { desc = "close quickfix list" }) -- close quickfix list

-- Git-blame
keymap.set("n", "<leader>gb", ":GitBlameToggle<CR>", { desc = "toggle git blame" }) -- toggle git blame

-- LSP
keymap.set("n", "<leader>gg", "<cmd>lua vim.lsp.buf.hover()<CR>", { desc = "hover" })
keymap.set("n", "gd", "<cmd>lua vim.lsp.buf.definition()<CR>", { desc = "goto definition" })
keymap.set("n", "gD", "<cmd>lua vim.lsp.buf.declaration()<CR>", { desc = "goto declaration" })
keymap.set("n", "gi", "<cmd>lua vim.lsp.buf.implementation()<CR>", { desc = "goto implementation" })
keymap.set("n", "gt", "<cmd>lua vim.lsp.buf.type_definition()<CR>", { desc = "type definition" })
keymap.set("n", "gr", "<cmd>lua vim.lsp.buf.references()<CR>", { desc = "references" })
keymap.set("n", "gs", "<cmd>lua vim.lsp.buf.signature_help()<CR>", { desc = "signature help" })
keymap.set("n", "rr", "<cmd>lua vim.lsp.buf.rename()<CR>", { desc = "rename" })
keymap.set("n", "gf", "<cmd>lua vim.lsp.buf.format({async = true})<CR>", { desc = "normal mode format" })
keymap.set("v", "gf", "<cmd>lua vim.lsp.buf.format({async = true})<CR>", { desc = "visual mode format" })
keymap.set("n", "ga", "<cmd>lua vim.lsp.buf.code_action()<CR>", { desc = "code action" })
keymap.set("n", "gl", "<cmd>lua vim.diagnostic.open_float()<CR>", { desc = "open float" })
keymap.set("n", "gp", "<cmd>lua vim.diagnostic.goto_prev()<CR>", { desc = "goto prev" })
keymap.set("n", "gn", "<cmd>lua vim.diagnostic.goto_next()<CR>", { desc = "goto next" })
keymap.set("n", "tr", "<cmd>lua vim.lsp.buf.document_symbol()<CR>", { desc = "document symbol" })
keymap.set("i", "<C-Space>", "<cmd>lua vim.lsp.buf.completion()<CR>", { desc = "completion" })

-- Filetype-specific keymaps (these can be done in the ftplugin directory instead if you prefer)
keymap.set("n", "<leader>go", function()
	if vim.bo.filetype == "python" then
		vim.api.nvim_command("PyrightOrganizeImports")
	end
end, { desc = "Pyright Organize Imports" })

keymap.set("n", "<leader>tc", function()
	if vim.bo.filetype == "python" then
		require("dap-python").test_class()
	end
end, { desc = "test class" })

keymap.set("n", "<leader>tm", function()
	if vim.bo.filetype == "python" then
		require("dap-python").test_method()
	end
end, { desc = "test method" })

-- Debugging
keymap.set("n", "<leader>bb", "<cmd>lua require'dap'.toggle_breakpoint()<cr>", { desc = "toggle breakpoint" })
keymap.set(
	"n",
	"<leader>bc",
	"<cmd>lua require'dap'.set_breakpoint(vim.fn.input('Breakpoint condition: '))<cr>",
	{ desc = "condition breakpoint" }
)
keymap.set(
	"n",
	"<leader>bl",
	"<cmd>lua require'dap'.set_breakpoint(nil, nil, vim.fn.input('Log point message: '))<cr>",
	{ desc = "log point message" }
)
keymap.set("n", "<leader>br", "<cmd>lua require'dap'.clear_breakpoints()<cr>", { desc = "clear breakpoint" })
keymap.set("n", "<leader>ba", "<cmd>Telescope dap list_breakpoints<cr>", { desc = "list breakpoint" })
keymap.set("n", "<leader>dc", "<cmd>lua require'dap'.continue()<cr>", { desc = "continue" })
keymap.set("n", "<leader>dj", "<cmd>lua require'dap'.step_over()<cr>", { desc = "step over" })
keymap.set("n", "<leader>dk", "<cmd>lua require'dap'.step_into()<cr>", { desc = "step into" })
keymap.set("n", "<leader>do", "<cmd>lua require'dap'.step_out()<cr>", { desc = "step out" })
keymap.set("n", "<leader>dd", function()
	require("dap").disconnect()
	require("dapui").close()
end, { desc = "disconnect dap" })
keymap.set("n", "<leader>dt", function()
	require("dap").terminate()
	require("dapui").close()
end, { desc = "terminate" })
keymap.set("n", "<leader>dr", "<cmd>lua require'dap'.repl.toggle()<cr>", { desc = "repl toggle" })
keymap.set("n", "<leader>dl", "<cmd>lua require'dap'.run_last()<cr>", { desc = "run last" })
keymap.set("n", "<leader>di", function()
	require("dap.ui.widgets").hover()
end, { desc = "hover" })
keymap.set("n", "<leader>d?", function()
	local widgets = require("dap.ui.widgets")
	widgets.centered_float(widgets.scopes)
end, { desc = "widget centered float" })
keymap.set("n", "<leader>df", "<cmd>Telescope dap frames<cr>", { desc = "telescope dap frames" })
keymap.set("n", "<leader>dh", "<cmd>Telescope dap commands<cr>", { desc = "telescope dap commands" })
keymap.set("n", "<leader>de", function()
	require("telescope.builtin").diagnostics({ default_text = ":E:" })
end, { desc = "telescope builtin" })
