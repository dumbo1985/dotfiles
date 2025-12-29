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
		-- 检查 Neovim 版本并使用正确的 API
		-- Neovim 0.11+ 使用 vim.lsp.config，旧版本使用 require("lspconfig")
		local has_new_api = vim.lsp.config ~= nil
		local lspconfig
		if has_new_api then
			lspconfig = vim.lsp.config
		else
			-- 向后兼容：使用 require("lspconfig") 但抑制警告
			lspconfig = require("lspconfig")
		end

		local cmp_nvim_lsp = require("cmp_nvim_lsp")
		local schemastore = require("schemastore")

		-- 等待 mason-lspconfig 加载完成
		local mason_lspconfig_ok, mason_lspconfig = pcall(require, "mason-lspconfig")
		if not mason_lspconfig_ok then
			vim.notify("mason-lspconfig not available", vim.log.levels.WARN)
			return
		end

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
			-- LSP 签名提示（如果可用）
			pcall(function()
				require("lsp_signature").on_attach({}, bufnr)
			end)

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

		-- 设置所有 LSP 服务器
		-- 使用延迟确保所有依赖已完全初始化
		vim.schedule(function()
			-- 定义要设置的服务器列表（与 mason.lua 中的 ensure_installed 保持一致）
			local servers_to_setup = {
				"html", "cssls", "tailwindcss", "svelte", "lua_ls",
				"graphql", "emmet_ls", "pyright", "clangd", "gopls",
			}

			-- 手动设置每个服务器
			for _, server_name in ipairs(servers_to_setup) do
				-- 检查服务器是否存在
				if not lspconfig[server_name] then
					vim.notify("LSP server not found: " .. server_name, vim.log.levels.WARN)
				else
					local config = server_configs[server_name] or {}
					-- 合并配置，确保 on_attach 和 capabilities 被应用
					local final_config = vim.tbl_deep_extend("force", {
						on_attach = on_attach,
						capabilities = capabilities,
					}, config)
					-- 使用 pcall 保护，防止单个服务器配置失败影响其他服务器
					pcall(function()
						lspconfig[server_name].setup(final_config)
					end)
				end
			end
		end)
	end,
}
