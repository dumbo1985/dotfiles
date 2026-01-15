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
			local opts = { buffer = bufnr, silent = true, noremap = true }

			-- LSP 键位映射（buffer-local，只在有 LSP 客户端时生效）
			-- 使用 vim.lsp.buf 直接映射，确保正确工作
			vim.keymap.set("n", "K", vim.lsp.buf.hover, vim.tbl_extend("force", opts, { desc = "显示悬停信息" }))
			
			-- 跳转到定义 - 直接使用 vim.lsp.buf.definition，不要包装在函数中
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, vim.tbl_extend("force", opts, { desc = "跳转到定义" }))
			
			vim.keymap.set("n", "gD", vim.lsp.buf.declaration, vim.tbl_extend("force", opts, { desc = "跳转到声明" }))
			vim.keymap.set("n", "gi", vim.lsp.buf.implementation, vim.tbl_extend("force", opts, { desc = "跳转到实现" }))
			vim.keymap.set("n", "gt", vim.lsp.buf.type_definition, vim.tbl_extend("force", opts, { desc = "跳转到类型定义" }))
			vim.keymap.set("n", "gr", function()
				require("telescope.builtin").lsp_references()
			end, vim.tbl_extend("force", opts, { desc = "查找引用" }))
			vim.keymap.set("n", "gs", vim.lsp.buf.signature_help, vim.tbl_extend("force", opts, { desc = "函数签名提示" }))
			vim.keymap.set("n", "rr", vim.lsp.buf.rename, vim.tbl_extend("force", opts, { desc = "重命名" }))
			vim.keymap.set("n", "<leader>cf", function()
				vim.lsp.buf.format({ async = true })
			end, { buffer = bufnr, desc = "[C]ode [F]ormat", silent = true, noremap = true })
			vim.keymap.set("v", "<leader>cf", function()
				vim.lsp.buf.format({ async = true })
			end, { buffer = bufnr, desc = "[C]ode [F]ormat selection", silent = true, noremap = true })
			vim.keymap.set("n", "ga", vim.lsp.buf.code_action, vim.tbl_extend("force", opts, { desc = "代码操作" }))
			vim.keymap.set("n", "tr", vim.lsp.buf.document_symbol, vim.tbl_extend("force", opts, { desc = "文档符号列表" }))
		end

		-- 使用 autocmd 确保在所有 LSP 客户端附加时设置映射
		-- 这可以覆盖任何默认的 on_attach，确保我们的映射被设置
		vim.api.nvim_create_autocmd("LspAttach", {
			group = vim.api.nvim_create_augroup("UserLspConfig", {}),
			callback = function(event)
				local client = vim.lsp.get_client_by_id(event.data.client_id)
				if client then
					on_attach(client, event.buf)
				end
			end,
		})

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
				on_attach = on_attach, -- 明确设置 on_attach
			},
			lua_ls = {
				on_attach = on_attach, -- 明确设置 on_attach
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
				on_attach = on_attach, -- 明确设置 on_attach
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
				on_attach = on_attach, -- 明确设置 on_attach
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
		mason_lspconfig.setup({
			ensure_installed = vim.tbl_keys(server_configs),
			automatic_installation = true,
			-- 设置处理器：为所有服务器配置
			handlers = {
				-- 为每个服务器明确设置处理器
				function(server_name)
					-- 如果服务器在 server_configs 中有自定义配置，使用自定义配置
					if server_configs[server_name] then
						local config = vim.deepcopy(server_configs[server_name])
						-- 强制设置 capabilities 和 on_attach，确保覆盖任何默认值
						config.capabilities = capabilities
						config.on_attach = on_attach -- 强制使用我们的 on_attach，覆盖任何默认值
						-- 检查服务器是否存在并设置
						if lspconfig[server_name] then
							lspconfig[server_name].setup(config)
						else
							vim.notify("LSP 服务器 '" .. server_name .. "' 未找到", vim.log.levels.WARN)
						end
					else
						-- 否则使用默认配置（包含我们的 on_attach）
						if lspconfig[server_name] then
							lspconfig[server_name].setup({
								capabilities = capabilities,
								on_attach = on_attach,
							})
						end
					end
				end,
			},
		})


		-- 添加诊断命令
		vim.api.nvim_create_user_command("LspDiagnostics", function()
			local bufnr = vim.api.nvim_get_current_buf()
			local clients = vim.lsp.get_active_clients({ bufnr = bufnr })
			
			if #clients == 0 then
				vim.notify("当前缓冲区没有活动的 LSP 客户端", vim.log.levels.WARN)
				vim.notify("请检查：", vim.log.levels.INFO)
				vim.notify("1. LSP 服务器是否已安装（:Mason）", vim.log.levels.INFO)
				vim.notify("2. 文件类型是否正确（当前: " .. vim.bo.filetype .. "）", vim.log.levels.INFO)
				vim.notify("3. LSP 日志（:LspLog）", vim.log.levels.INFO)
			else
				local msg = "活动的 LSP 客户端：\n"
				for _, client in ipairs(clients) do
					msg = msg .. "- " .. client.name
					if client.supports_method("textDocument/definition") then
						msg = msg .. " ✓ 支持跳转到定义"
					else
						msg = msg .. " ✗ 不支持跳转到定义"
					end
					msg = msg .. "\n"
				end
				vim.notify(msg, vim.log.levels.INFO)
			end
		end, { desc = "显示 LSP 诊断信息" })
	end,
}
