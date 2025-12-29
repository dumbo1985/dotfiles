--- Transparent 插件配置模块
--- 负责透明背景插件的配置
--- @module dengbo.ui.transparent

local M = {}

--- 初始化 Transparent 配置
--- @return nil
function M.setup()
	vim.g.transparent_groups = vim.list_extend(vim.g.transparent_groups or {}, { "ExtraGroup" })
end

return M

