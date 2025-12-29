--- 输入法切换模块（macOS 特定）
--- 负责在插入模式切换时自动切换输入法
--- @module dengbo.platform.input_method

local M = {}

--- 检查是否为 macOS
--- @return boolean
local function is_macos()
	return vim.fn.has("mac") == 1
end

--- 检查 im-select 命令是否可用
--- @return boolean
local function is_im_select_available()
	return vim.fn.executable("im-select") == 1
end

--- 初始化输入法切换功能
--- @return nil
function M.setup()
	if not is_macos() then
		return
	end

	if not is_im_select_available() then
		return
	end

	local last_input_method = nil

	-- 离开插入模式时切换到英文
	vim.api.nvim_create_autocmd("InsertLeave", {
		callback = function()
			local ok, result = pcall(function()
				return vim.fn.system("im-select"):gsub("\n", "")
			end)
			if ok then
				last_input_method = result
				pcall(function()
					vim.fn.system("im-select com.apple.keylayout.ABC")
				end)
			end
		end,
	})

	-- 进入插入模式时恢复之前的输入法
	vim.api.nvim_create_autocmd("InsertEnter", {
		callback = function()
			if last_input_method then
				pcall(function()
					vim.fn.system("im-select " .. last_input_method)
				end)
			end
		end,
	})
end

return M

