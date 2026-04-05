return {
	-- https://github.com/mfussenegger/nvim-dap-python
	"mfussenegger/nvim-dap-python",
	ft = "python",
	dependencies = {
		-- https://github.com/mfussenegger/nvim-dap
		"mfussenegger/nvim-dap",
	},
	config = function()
		local py = vim.fn.exepath("python3")
		if py == "" then
			py = "/usr/bin/python3"
		end
		require("dap-python").setup(py)
	end,
}
