require("dengbo.core.options")
require("dengbo.core.keymaps")
require("dengbo.core.neovide")
-- 必须在 lazy.nvim 加载插件之前打补丁，屏蔽旧 API 的弃用警告
require("dengbo.core.deprecated_fix").setup()
if vim.fn.has("mac") == 1 and vim.fn.executable("im-select") == 1 then
	require("dengbo.core.input_method")
end