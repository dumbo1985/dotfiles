return {
	"mfussenegger/nvim-dap",
	event = "VeryLazy",
	dependencies = {
		{
			"leoluz/nvim-dap-go",
			config = function()
				require("dap-go").setup()
			end,
		},
		"jbyuki/one-small-step-for-vimkind",
	},
}
