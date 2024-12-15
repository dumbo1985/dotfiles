return {
	"echasnovski/mini.icons",

	config = function()
		-- Update the path passed to setup to point to your system or virtual env python binary
		require("mini.icons").setup(
			-- No need to copy this inside `setup()`. Will be used automatically.
			{
				-- Icon style: 'glyph' or 'ascii'
				style = "glyph",

				-- Customize per category. See `:h MiniIcons.config` for details.
				default = {},
				directory = {},
				extension = {},
				file = {},
				filetype = {},
				lsp = {},
				os = {},

				-- Control which extensions will be considered during "file" resolution
				use_file_extension = function(ext, file)
					return true
				end,
			}
		)
	end,
}
