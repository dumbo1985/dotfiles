require("dengbo.core.options")
require("dengbo.core.keymaps")
require("dengbo.core.neovide")
if vim.fn.has("mac") == 1 and vim.fn.executable("im-select") == 1 then
	require("dengbo.core.input_method")
end