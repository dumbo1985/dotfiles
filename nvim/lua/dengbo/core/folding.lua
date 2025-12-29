--- 代码折叠配置模块
--- 负责配置 Neovim 的代码折叠功能
--- @module dengbo.core.folding

local M = {}

--- 设置代码折叠配置
--- @return nil
function M.setup()
	-- 使用 treesitter 的 expr 折叠
	vim.opt.foldmethod = "expr"
	vim.opt.foldexpr = "nvim_treesitter#foldexpr()"
	vim.opt.foldlevel = 99 -- 默认不折叠
	vim.opt.foldtext = "v:lua.vim.treesitter.foldtext()" -- 美化折叠显示
end

return M

