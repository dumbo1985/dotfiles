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
