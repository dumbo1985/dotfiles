--- 弃用 API 兼容性补丁
--- 修复插件中使用的已弃用 API
--- @module dengbo.core.deprecated_fix

local M = {}

--- 修复 vim.lsp.buf_get_clients 的弃用警告
--- 为 symbols-outline.nvim 等插件提供兼容性
--- 注意：在 Neovim 0.12+ 中，buf_get_clients 已被移除
function M.fix_lsp_buf_get_clients()
	-- 在 Neovim 0.12+ 中，buf_get_clients 已被移除
	-- 我们需要在插件加载前创建兼容层
	if vim.lsp.get_clients then
		-- 创建兼容函数，将 buf_get_clients 映射到 get_clients
		if not vim.lsp.buf_get_clients then
			vim.lsp.buf_get_clients = function(bufnr)
				-- 使用新的 API：vim.lsp.get_clients({ bufnr = bufnr })
				bufnr = bufnr or vim.api.nvim_get_current_buf()
				local clients = vim.lsp.get_clients({ bufnr = bufnr })
				-- 返回格式兼容旧 API
				return clients
			end
		end
	end
end

--- 初始化兼容性补丁
--- 必须在插件加载前调用
function M.setup()
	-- 在插件加载前修复弃用 API
	M.fix_lsp_buf_get_clients()
end

return M

