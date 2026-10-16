--- 主题配置模块
--- 负责主题的随机选择和配置
--- @module dengbo.ui.theme

local M = {}

--- 主题配置表
--- @type table[]
local themes = {
	{
		name = "tokyonight",
		setup = function()
			pcall(function()
				require("tokyonight").setup({ style = "night" })
			end)
		end,
	},
	{
		name = "kanagawa",
		setup = function()
			pcall(function()
				require("kanagawa").setup({ background = { dark = "wave" } })
			end)
		end,
	},
	{
		name = "catppuccin",
		setup = function()
			pcall(function()
				require("catppuccin").setup({ flavour = "mocha" })
			end)
		end,
	},
	{
		name = "rose-pine",
		setup = function()
			pcall(function()
				require("rose-pine").setup({ variant = "main" })
			end)
		end,
	},
	{
		name = "sonokai",
		setup = function()
			vim.g.sonokai_style = "default"
		end,
	},
	{ name = "onenord", setup = function() end },
}

--- 随机选择一个主题并应用
--- @return nil
local function apply_random_theme()
	math.randomseed(os.time())
	local theme = themes[math.random(#themes)]
	theme.setup()
	vim.cmd("colorscheme " .. theme.name)
	vim.notify("🎨 Loaded random theme: " .. theme.name)
end

--- 初始化主题配置
--- @return nil
function M.setup()
	-- 延迟加载，避免阻塞启动
	vim.schedule(function()
		apply_random_theme()
	end)
end

return M

