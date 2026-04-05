return {
	"williamboman/mason.nvim",
	dependencies = {
		"WhoIsSethDaniel/mason-tool-installer.nvim",
	},
	config = function()
		local mason = require("mason")
		local mason_tool_installer = require("mason-tool-installer")

		-- enable mason and configure icons
		mason.setup({
			-- pip = {
			-- 	install_args = { "--user" },
			-- 	pip_path = "~/.mason-python-env/bin/pip3", -- 使用虚拟环境的 pip
			-- },
			-- PATH = {
			-- 	python = "~/.mason-python-env/bin/python3", -- 使用虚拟环境的 python
			-- },

			ui = {
				icons = {
					package_installed = "✓",
					package_pending = "➜",
					package_uninstalled = "✗",
				},
			},
		})

		-- mason-lspconfig 的 ensure_installed / handlers 统一在 lspconfig.lua 配置，避免重复 setup

		mason_tool_installer.setup({
			ensure_installed = {
				"codelldb",
				"clangd",
				"clang-format",
				"prettier",
				"stylua",
				"isort",
				"black",
				"eslint_d",
				"debugpy",
				"flake8",
				"yamlfix",
				"taplo",
				"shellcheck",
				"gopls",
				"delve",
			},
		})
	end,
}
