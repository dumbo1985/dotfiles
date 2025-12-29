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

		-- 使用新的 API 配置诊断符号（避免弃用警告）
		vim.diagnostic.config({
			virtual_text = {
				spacing = 2,
				prefix = "▎",
				format = function(diagnostic)
					local config = severity_icons[diagnostic.severity] or { icon = "" }
					return string.format("%s %s", config.icon, diagnostic.message)
				end,
			},
			signs = {
				-- 使用新的 signs 配置方式
				text = {
					[vim.diagnostic.severity.ERROR] = severity_icons[vim.diagnostic.severity.ERROR].icon,
					[vim.diagnostic.severity.WARN] = severity_icons[vim.diagnostic.severity.WARN].icon,
					[vim.diagnostic.severity.HINT] = severity_icons[vim.diagnostic.severity.HINT].icon,
					[vim.diagnostic.severity.INFO] = severity_icons[vim.diagnostic.severity.INFO].icon,
				},
			},
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
			local opts = { buffer = bufnr, silent = true }

			-- LSP 键位映射（buffer-local，只在有 LSP 客户端时生效）
			vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
			vim.keymap.set("n", "gD", vim.lsp.buf.declaration, opts)
			vim.keymap.set("n", "gi", vim.lsp.buf.implementation, opts)
			vim.keymap.set("n", "gt", vim.lsp.buf.type_definition, opts)
			vim.keymap.set("n", "gr", require("telescope.builtin").lsp_references, opts)
			vim.keymap.set("n", "gs", vim.lsp.buf.signature_help, opts)
			vim.keymap.set("n", "rr", vim.lsp.buf.rename, opts)
			vim.keymap.set("n", "<leader>cf", function()
				vim.lsp.buf.format({ async = true })
			end, { buffer = bufnr, desc = "[C]ode [F]ormat" })
			vim.keymap.set("v", "<leader>cf", function()
				vim.lsp.buf.format({ async = true })
			end, { buffer = bufnr, desc = "[C]ode [F]ormat selection" })
			vim.keymap.set("n", "ga", vim.lsp.buf.code_action, opts)
			vim.keymap.set("n", "tr", vim.lsp.buf.document_symbol, opts)
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
			ts_ls = {
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

		-- 自动安装配置的 LSP 服务器
		-- 注意：mason.lua 中配置的服务器会自动安装，这里只确保 server_configs 中的服务器被安装
		mason_lspconfig.setup({
			ensure_installed = vim.tbl_keys(server_configs),
			automatic_installation = true,
			-- 设置处理器：为所有服务器配置
			handlers = {
				-- 默认处理器：为没有在 server_configs 中配置的服务器使用默认设置
				function(server_name)
					-- 如果服务器在 server_configs 中有自定义配置，使用自定义配置
					if server_configs[server_name] then
						local config = vim.deepcopy(server_configs[server_name])
						config.capabilities = capabilities
						config.on_attach = config.on_attach or on_attach
						-- 检查服务器是否存在
						local server = lspconfig[server_name]
						if server and server.setup then
							server.setup(config)
						end
					else
						-- 否则使用默认配置
						local server = lspconfig[server_name]
						if server and server.setup then
							server.setup({
								capabilities = capabilities,
								on_attach = on_attach,
							})
						end
					end
				end,
			},
		})
	end,
}
