return {
	"stevearc/conform.nvim",
	event = { "BufReadPre", "BufNewFile" },
	opts = {
		formatters_by_ft = {
			bash = { "beautysh" },
			proto = { "buf" },
			rust = { "rustfmt" },
			javascript = { "prettier" },
			typescript = { "prettier" },
			javascriptreact = { "prettier" },
			typescriptreact = { "prettier" },
			svelte = { "prettier" },
			css = { "prettierd", "prettier" },
			scss = { "prettierd", "prettier" },
			sh = { "shellcheck" },
			html = { "htmlbeautifier" },
			json = { "prettier" },
			yaml = { "yamlfix" },
			toml = { "taplo" },
			markdown = { "prettier" },
			graphql = { "prettier" },
			liquid = { "prettier" },
			lua = { "stylua" },
			go = { "gofmt" },
			python = { "isort", "black" },
		},
		format_on_save = {
			lsp_fallback = true,
			async = false,
			timeout_ms = 1000,
		},
	},
	config = function(_, opts)
		require("conform").setup(opts)
		-- 注意：<leader>mp 已被 markdown.lua 的浏览器预览占用，这里改用 <leader>mf
		vim.keymap.set({ "n", "v" }, "<leader>mf", function()
			require("conform").format({
				lsp_fallback = true,
				async = false,
				timeout_ms = 1000,
			})
		end, { desc = "Format file or range (in visual mode)" })
	end,
}
