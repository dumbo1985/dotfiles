return {
	"neovim/nvim-lspconfig",
	event = { "BufReadPre", "BufNewFile" },
	dependencies = {
		"hrsh7th/cmp-nvim-lsp",
		{ "antosha417/nvim-lsp-file-operations", config = true },
		{ "folke/neodev.nvim", opts = {} },
		{ "b0o/schemastore.nvim" }, -- JSON schema 支持
	},
	config = function()
		local lspconfig = require("lspconfig")
		local mason_lspconfig = require("mason-lspconfig")
		local cmp_nvim_lsp = require("cmp_nvim_lsp")
		local schemastore = require("schemastore")

		-- 诊断图标配置（类型安全版本）
		local severity_icons = {
			[vim.diagnostic.severity.ERROR] = { icon = " ", hl = "DiagnosticSignError" },
			[vim.diagnostic.severity.WARN] = { icon = " ", hl = "DiagnosticSignWarn" },
			[vim.diagnostic.severity.HINT] = { icon = "󰌵 ", hl = "DiagnosticSignHint" },
			[vim.diagnostic.severity.INFO] = { icon = " ", hl = "DiagnosticSignInfo" },
		}

		-- 设置诊断符号
		for _, config in pairs(severity_icons) do
			vim.fn.sign_define(config.hl, { text = config.icon, texthl = config.hl, numhl = "" })
		end

		-- 诊断显示配置
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

		-- 通用 on_attach 函数
		local on_attach = function(client, bufnr)
			-- 设置格式化快捷键
			vim.keymap.set("n", "<leader>cf", function()
				vim.lsp.buf.format({ async = true })
			end, { buffer = bufnr, desc = "[C]ode [F]ormat" })

			-- 其他常用快捷键
			local opts = { buffer = bufnr, silent = true }
			vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
			vim.keymap.set("n", "gr", require("telescope.builtin").lsp_references, opts)
			vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
		end

		-- 增强的 LSP 能力配置
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

		-- 特殊服务器配置
		local server_configs = {
			lua_ls = {
				settings = {
					Lua = {
						diagnostics = { globals = { "vim" } },
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

		-- Mason LSP 处理器配置
		mason_lspconfig.setup_handlers({
			function(server_name)
				local config = server_configs[server_name] or {}
				config.capabilities = capabilities
				config.on_attach = config.on_attach or on_attach
				lspconfig[server_name].setup(config)
			end,
		})
	end,
}
