return {
	"neovim/nvim-lspconfig",
	event = { "BufReadPre", "BufNewFile" },
	dependencies = {
		"hrsh7th/cmp-nvim-lsp",
		{ "antosha417/nvim-lsp-file-operations", config = true },
		{ "folke/neodev.nvim", opts = {} }, -- ✅ 提供 Neovim API 类型支持
		{ "b0o/schemastore.nvim" }, -- JSON schema 支持
		"williamboman/mason.nvim",
		"williamboman/mason-lspconfig.nvim",
	},
	config = function()
		-- 初始化 Mason
		require("mason").setup()
		require("mason-lspconfig").setup()

		local lspconfig = require("lspconfig")
		local mason_lspconfig = require("mason-lspconfig")
		local cmp_nvim_lsp = require("cmp_nvim_lsp")
		local schemastore = require("schemastore")

		-- 初始化 Neodev（必须在 lua_ls.setup 之前）
		require("neodev").setup({})

		-- 诊断图标配置
		local severity_icons = {
			[vim.diagnostic.severity.ERROR] = { icon = " ", hl = "DiagnosticSignError" },
			[vim.diagnostic.severity.WARN] = { icon = " ", hl = "DiagnosticSignWarn" },
			[vim.diagnostic.severity.HINT] = { icon = "󰌵 ", hl = "DiagnosticSignHint" },
			[vim.diagnostic.severity.INFO] = { icon = " ", hl = "DiagnosticSignInfo" },
		}

		for _, config in pairs(severity_icons) do
			vim.fn.sign_define(config.hl, { text = config.icon, texthl = config.hl, numhl = "" })
		end

		vim.diagnostic.config({
			virtual_text = {
				spacing = 2,
				prefix = "▎",
				format = function(diagnostic)
					local config = severity_icons[diagnostic.severity] or { icon = "" }
					return string.format("%s %s", config.icon, diagnostic.message)
				end,
			},
			signs = true,
			underline = { severity = { min = vim.diagnostic.severity.WARN } },
			severity_sort = true,
			float = {
				focusable = true,
				style = "minimal",
				border = "rounded",
				source = "if_many",
				header = "",
				prefix = function(diagnostic)
					local config = severity_icons[diagnostic.severity] or { icon = "" }
					return string.format("%s [%s]", config.icon, diagnostic.source or "LSP")
				end,
			},
		})

		local on_attach = function(client, bufnr)
			vim.keymap.set("n", "<leader>cf", function()
				vim.lsp.buf.format({ async = true })
			end, { buffer = bufnr, desc = "[C]ode [F]ormat" })

			local opts = { buffer = bufnr, silent = true }
			vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
			vim.keymap.set("n", "gr", require("telescope.builtin").lsp_references, opts)
			vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
		end

		local capabilities = vim.tbl_deep_extend("force", cmp_nvim_lsp.default_capabilities(), {
			textDocument = {
				foldingRange = {
					dynamicRegistration = false,
					lineFoldingOnly = true,
				},
			},
			workspace = {
				didChangeWatchedFiles = {
					dynamicRegistration = true,
				},
			},
		})

		local server_configs = {
			clangd = {
				cmd = {
					"clangd",
					"--background-index",
					"--pch-storage=memory",
					"--suggest-missing-includes",
					"--clang-tidy",
					"--compile-commands-dir=build",
					"--completion-style=detailed",
					"--header-insertion=never",
				},
			},
			lua_ls = {
				settings = {
					Lua = {
						diagnostics = { globals = { "vim" } }, -- ✅ 告诉 LSP 这个是全局变量
						completion = { callSnippet = "Replace" },
						workspace = { checkThirdParty = false },
						telemetry = { enable = false },
					},
				},
			},
			tsserver = {
				settings = {
					typescript = {
						inlayHints = {
							includeInlayParameterNameHints = "all",
							includeInlayParameterNameHintsWhenArgumentMatchesName = false,
							includeInlayFunctionParameterTypeHints = true,
							includeInlayVariableTypeHints = true,
							includeInlayPropertyDeclarationTypeHints = true,
							includeInlayFunctionLikeReturnTypeHints = true,
							includeInlayEnumMemberValueHints = true,
						},
					},
				},
			},
			jsonls = {
				settings = {
					json = {
						schemas = schemastore.json.schemas(),
						validate = { enable = true },
					},
				},
			},
			svelte = {
				on_attach = function(client, bufnr)
					on_attach(client, bufnr)
					vim.api.nvim_create_autocmd("BufWritePost", {
						pattern = { "*.js", "*.ts" },
						callback = function(ctx)
							client.notify("$/onDidChangeTsOrJsFile", { uri = ctx.match })
						end,
					})
				end,
			},
		}
	end,
}
