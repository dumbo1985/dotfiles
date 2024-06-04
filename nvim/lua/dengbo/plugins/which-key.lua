return {
	"folke/which-key.nvim",
	event = "VeryLazy",
	init = function()
		vim.o.timeout = true
		vim.o.timeoutlen = 500
	end,

	config = function()
		local whichkey = require("which-key")
		-- local legendary = require "legendary"

		-- local function keymap(lhs, rhs, desc)
		--   vim.keymap.set("n", lhs, rhs, { silent = true, desc = desc })
		-- end

		whichkey.setup()
		local keymap = {
			b = { name = "Breakpoint" },
			c = { name = "Diff" },
			d = { name = "Debug" },
			e = { name = "File Explorer" },
			f = { name = "Find" },
			g = { name = "Blame" },
			h = { name = "Hunk" },
			l = { name = "LazyGit" },
			m = { name = "Format" },
			n = { name = "Highlights" },
			q = { name = "Quickfix" },
			r = { name = "Redo" },
			s = { name = "Splite" },
			t = { name = "Tab" },
			x = { name = "Trouble" },
			w = { name = "Session" },
		}

		local opts = {
			mode = "n",
			prefix = "<leader>",
			buffer = nil,
			silent = true,
			noremap = true,
			nowait = false,
		}

		whichkey.register(keymap, opts)
		--- require("legendary.integrations.which-key").bind_whichkey(keymap, opts, false)

		local keymap_v = {
			d = {
				name = "Debug",
				e = { "<cmd>lua require'dapui'.eval()<cr>", "Evaluate" },
			},
		}
		opts = {
			mode = "v",
			prefix = "<leader>",
			buffer = nil,
			silent = true,
			noremap = true,
			nowait = false,
		}
		whichkey.register(keymap_v, opts)
		--- require("legendary.integrations.which-key").bind_whichkey(keymap_v, opts, false)
	end,
}
