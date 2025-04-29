return {
	"nvim-tree/nvim-tree.lua",
	dependencies = { "nvim-tree/nvim-web-devicons" },
	config = function()
		-- 推荐先禁用 netrw，不然偶尔打开会有冲突
		vim.g.loaded_netrw = 1
		vim.g.loaded_netrwPlugin = 1

		local nvimtree = require("nvim-tree")

		nvimtree.setup({
			sort_by = "case_sensitive",

			view = {
				width = 40,
				side = "left",
				relativenumber = true,
				signcolumn = "yes",
				preserve_window_proportions = true, -- 保持窗口比例更自然
			},

			update_cwd = true,
			update_focused_file = {
				enable = true,
				update_cwd = true,
				update_root = true, -- 推荐：切换根目录时同步更新
			},

			renderer = {
				group_empty = true,
				highlight_git = true, -- 推荐：高亮 Git 状态
				full_name = true, -- 推荐：长文件名不省略
				indent_markers = {
					enable = true,
				},
				icons = {
					show = {
						file = true,
						folder = true,
						folder_arrow = true,
						git = true,
					},
					glyphs = {
						folder = {
							arrow_closed = "", -- 关闭时的箭头
							arrow_open = "", -- 打开时的箭头
						},
					},
				},
			},

			actions = {
				open_file = {
					window_picker = {
						enable = false,
					},
					resize_window = true, -- 推荐：打开文件后自动调整大小
				},
			},

			filters = {
				dotfiles = false, -- 推荐：显示 dotfiles（隐藏文件）
				custom = { ".DS_Store" }, -- 自定义隐藏文件
			},

			git = {
				enable = true, -- 确保 git 显示开启
				ignore = false, -- 不忽略 .gitignore 文件
				timeout = 400, -- git 超时，防止卡住
			},

			system_open = {
				cmd = "open", -- MacOS 打开文件用 open
			},

			diagnostics = {
				enable = true, -- 推荐：显示 LSP 诊断信息
				icons = {
					hint = "",
					info = "",
					warning = "",
					error = "",
				},
			},

			hijack_cursor = true, -- 推荐：聚焦时光标自动跳到文件树
			respect_buf_cwd = true, -- 推荐：尊重 buffer 的 cwd
			sync_root_with_cwd = true, -- 推荐：跟随 Neovim cwd 自动切换
		})
	end,
}
