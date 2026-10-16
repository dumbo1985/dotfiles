-- 符号大纲：hedyhli/outline.nvim
-- 原 simrat39/symbols-outline.nvim 已于 2023 年停止维护，其 jsx.lua 调用
-- nvim-treesitter 旧 API（parsers.get_parser），在 nvim-treesitter main
-- 分支 + Neovim 0.12 下报 "attempt to call field 'get_parser' (a nil value)"。
-- outline.nvim 是社区维护的活跃替代，键位与观感保持一致。
return {
	"hedyhli/outline.nvim",
	cmd = { "Outline", "OutlineOpen", "OutlineClose" },
	keys = {
		{ "<leader>es", "<cmd>Outline<CR>", desc = "Toggle symbol outline" },
	},
	opts = {
		highlight_hovered_item = true,
		show_guides = true,
		guides = { enabled = true },
		outline_window = {
			position = "right",
			relative_width = true,
			width = 15,
			auto_close = false,
			show_numbers = false,
			show_relative_numbers = false,
			wrap = false,
		},
		outline_items = {
			show_symbol_details = true,
		},
		preview_window = {
			auto_preview = false,
		},
		keymaps = {
			close = { "<Esc>", "q" },
			goto_location = "<Cr>",
			peek_location = "o", -- outline.nvim 中对应旧 focus_location 的动作名
			hover_symbol = "<C-space>",
			toggle_preview = "K",
			rename_symbol = "r",
			code_actions = "a",
			fold = "h",
			unfold = "l",
			fold_all = "W",
			unfold_all = "E",
			fold_reset = "R",
		},
		symbols = {
			icons = {
				File = { icon = "󰈙", hl = "@text.uri" },
				Module = { icon = "󰆧", hl = "@namespace" },
				Namespace = { icon = "󰅩", hl = "@namespace" },
				Package = { icon = "󰅩", hl = "@namespace" },
				Class = { icon = "𝓒", hl = "@type" },
				Method = { icon = "ƒ", hl = "@method" },
				Property = { icon = "", hl = "@method" },
				Field = { icon = "󰆧", hl = "@field" },
				Constructor = { icon = "", hl = "@constructor" },
				Enum = { icon = "ℰ", hl = "@type" },
				Interface = { icon = "󰅩", hl = "@type" },
				Function = { icon = "", hl = "@function" },
				Variable = { icon = "", hl = "@constant" },
				Constant = { icon = "", hl = "@constant" },
				String = { icon = "𝓐", hl = "@string" },
				Number = { icon = "#", hl = "@number" },
				Boolean = { icon = "⊨", hl = "@boolean" },
				Array = { icon = "󰅩", hl = "@constant" },
				Object = { icon = "⦿", hl = "@type" },
				Key = { icon = "🔐", hl = "@type" },
				Null = { icon = "NULL", hl = "@type" },
				EnumMember = { icon = "", hl = "@field" },
				Struct = { icon = "𝓢", hl = "@type" },
				Event = { icon = "🗲", hl = "@type" },
				Operator = { icon = "+", hl = "@operator" },
				TypeParameter = { icon = "𝙏", hl = "@parameter" },
				Component = { icon = "󰅩", hl = "@function" },
				Fragment = { icon = "󰅩", hl = "@constant" },
			},
		},
	},
}
