--- 弃用 API 兼容性补丁
--- 屏蔽插件中调用的已弃用 API 产生的警告
--- @module dengbo.core.deprecated_fix

local M = {}

--- 用新 API 覆盖 vim.lsp.buf_get_clients 的废弃桩函数
--- 一些插件仍在调用旧 API；
--- Neovim 0.12 的废弃桩在被调用时会发 deprecation 警告，
--- 因此必须**无条件覆盖**（不能用 if not ... 守卫——桩函数始终存在，守卫永远不生效）。
function M.fix_lsp_buf_get_clients()
	if vim.lsp.get_clients and vim.lsp.buf_get_clients then
		vim.lsp.buf_get_clients = function(bufnr)
			bufnr = (bufnr == nil or bufnr == 0) and vim.api.nvim_get_current_buf() or bufnr
			return vim.lsp.get_clients({ bufnr = bufnr })
		end
	end
end

--- 初始化兼容性补丁（在 lazy.nvim 加载插件之前调用）
function M.setup()
	M.fix_lsp_buf_get_clients()
end

return M
