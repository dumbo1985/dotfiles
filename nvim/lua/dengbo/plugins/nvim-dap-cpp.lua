return {
	"mfussenegger/nvim-dap",
	dependencies = {
		"rcarriga/nvim-dap-ui",
		"theHamsta/nvim-dap-virtual-text",
	},
	config = function()
		local dap = require("dap")

		-- GDB 配置
		dap.adapters.cppdbg = {
			id = "cppdbg",
			type = "executable",
			command = vim.fn.stdpath("data") .. "/mason/packages/cpptools/extension/debugAdapters/bin/OpenDebugAD7",
		}

		dap.configurations.cpp = {
			{
				name = "Launch file with gdb",
				type = "cppdbg",
				request = "launch",
				program = function()
					return vim.fn.input("Path to executable: ", vim.fn.getcwd() .. "/", "file")
				end,
				cwd = "${workspaceFolder}",
				stopAtEntry = true,
				setupCommands = {
					{
						text = "-enable-pretty-printing",
						description = "enable pretty printing",
						ignoreFailures = false,
					},
				},
			},
		}

		-- lldb 配置
		dap.adapters.lldb = {
			type = "executable",
			-- command = "/usr/bin/lldb-vscode", -- macOS 下可能是 /opt/homebrew/opt/llvm/bin/lldb-vscode
			command = "/opt/homebrew/opt/llvm/bin/lldb-vscode", -- macOS 下可能是 /opt/homebrew/opt/llvm/bin/lldb-vscode
			name = "lldb",
		}

		dap.configurations.c = dap.configurations.cpp
		dap.configurations.rust = dap.configurations.cpp

		dap.configurations.cpp[#dap.configurations.cpp + 1] = {
			name = "Launch with lldb",
			type = "lldb",
			request = "launch",
			program = function()
				return vim.fn.input("Path to executable: ", vim.fn.getcwd() .. "/", "file")
			end,
			cwd = "${workspaceFolder}",
			stopOnEntry = false,
			args = {},
		}
	end,
}
