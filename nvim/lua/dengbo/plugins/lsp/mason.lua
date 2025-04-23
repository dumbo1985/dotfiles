return {
	"williamboman/mason.nvim",
	dependencies = {
		"williamboman/mason-lspconfig.nvim",
		"WhoIsSethDaniel/mason-tool-installer.nvim",
	},
	config = function()
		-- import mason
		local mason = require("mason")

		-- import mason-lspconfig
		local mason_lspconfig = require("mason-lspconfig")

		local mason_tool_installer = require("mason-tool-installer")

		-- enable mason and configure icons
		mason.setup({
			-- pip = {
			--     install_args = { "--user" },
			--     pip_path = "~/.mason-python-env/bin/pip3", -- 使用虚拟环境的 pip
			-- },
			-- PATH = {
			--     python = "~/.mason-python-env/bin/python3", -- 使用虚拟环境的 python
			-- },

			ui = {
				icons = {
					package_installed = "✓",
					package_pending = "➜",
					package_uninstalled = "✗",
				},
			},
		})

		mason_lspconfig.setup({
			-- list of servers for mason to install (lspconfig server 名称)
			ensure_installed = {
				"tsserver",
				"html",
				"cssls",
				"tailwindcss",
				"svelte",
				"lua_ls",
				"graphql",
				"emmet_ls",
				"pyright",
				"clangd",
				"gopls",
			},
			automatic_installation = true,
		})

		mason_tool_installer.setup({
			ensure_installed = {
				"codelldb", -- LLDB 调试器适配器
				"clangd", -- C/C++ LSP 服务器
				"clang-format", -- 代码格式化
				"cpptools", -- 备用调试适配器
				"cpplint", -- 代码风格检查
				"beautysh",
				"buf",
				"rustfmt",
				"htmlbeautifier",
				"prettier", -- prettier formatter
				"stylua", -- lua formatter
				"isort", -- python formatter
				"black", -- python formatter
				"pylint", -- python linter
				"eslint_d", -- js linter
				"python-lsp-server",
				"debugpy",
				"flake8",
				"mypy",
				"yamlfix",
				"taplo",
				"shellcheck",
				"gopls",
				"delve",
				"prisma-language-server", -- ✅ 添加 Prisma LSP（在 mason-tool-installer 中安装）
				"typescript-language-server",
			},
		})
	end,
}
