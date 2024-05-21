return {
	"rcarriga/nvim-dap-ui",

	event = "VeryLazy",

	dependencies = {
		"mfussenegger/nvim-dap",
		"nvim-neotest/nvim-nio",
	},

	config = function()
		local dap = require("dap")
		local dapui = require("dapui")
		dapui.setup()
		dap.listeners.after.event_initialized["dapui_config"] = function()
			dapui.open()
		end

		dap.listeners.before.event_terminated["dapui_config"] = function()
			dapui.close()
		end

		dap.listeners.before.event_exited["dapui_config"] = function()
			dapui.close()
		end

		-- set keymaps
		local keymap = vim.keymap -- for conciseness

		keymap.set("n", "<leader>db", "<cmd>DapToggleBreakpoint<CR>", { desc = "Add breakpoint at line" })
		keymap.set("n", "<leader>dr", "<cmd>DapContinue<CR>", { desc = "Start or continue the debugger" })
		keymap.set("n", "<leader>ds", "<cmd>DapStepInto<CR>", { desc = "Step into" })
		keymap.set("n", "<leader>dn", "<cmd>DapStepOver<CR>", { desc = "Step over" })
		keymap.set("n", "<leader>do", "<cmd>DapStepOut<CR>", { desc = "Step out" })
		keymap.set("n", "<leader>dt", "<cmd>DapTerminal<CR>", { desc = "Terminal" })
	end,
}
