return {
	"mfussenegger/nvim-dap",
	opt = true,
	module = { "dap" },
	requires = {
		{
			"theHamsta/nvim-dap-virtual-text",
			module = { "nvim-dap-virtual-text" },
		},
		{
			"leoluz/nvim-dap-go",
			config = function()
				require("dap-go").setup()
			end,
		},
		{
			"rcarriga/nvim-dap-ui",
			module = { "dapui" },
		},
		"nvim-telescope/telescope-dap.nvim",
		{
			"jbyuki/one-small-step-for-vimkind",
			module = "osv",
		},
	},
	disable = false,
}
