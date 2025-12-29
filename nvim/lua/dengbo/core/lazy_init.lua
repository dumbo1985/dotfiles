--- Lazy.nvim 初始化模块
--- 负责 Lazy.nvim 的安装和基础配置
--- @module dengbo.core.lazy_init

local M = {}

--- 初始化 Lazy.nvim
--- @return nil
function M.setup()
	local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
	if not vim.loop.fs_stat(lazypath) then
		vim.fn.system({
			"git",
			"clone",
			"--filter=blob:none",
			"https://github.com/folke/lazy.nvim.git",
			"--branch=stable",
			lazypath,
		})
	end
	vim.opt.rtp:prepend(lazypath)

	-- 配置 Lazy.nvim
	require("lazy").setup(
		{ { import = "dengbo.plugins" }, { import = "dengbo.plugins.lsp" } },
		{
			checker = {
				enabled = true,
				notify = false,
			},
			change_detection = {
				notify = false,
			},
		}
	)
end

return M

