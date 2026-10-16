return {
	"ludovicchabant/vim-gutentags",
	event = { "BufReadPre", "BufNewFile" },
	-- 没装 universal-ctags 时直接禁用，避免刷一堆找不到可执行文件的报错
	enabled = vim.fn.executable("ctags") == 1,
	init = function()
		-- 索引文件统一放缓存目录，不污染项目（gutentags 会自动 setlocal tags+=）
		vim.g.gutentags_cache_dir = vim.fn.stdpath("cache") .. "/tags"

		-- 需要 GNU GLOBAL（gtags）时改成 { "ctags", "gtags_cscope" }
		vim.g.gutentags_modules = { "ctags" }

		vim.g.gutentags_ctags_extra_args = {
			"--fields=+niazS", -- n:行号 i:继承 a:访问属性 z:kind 字母 S:签名
			"--extras=+q", -- q:为类成员生成 Class::member 形式的 tag
			"--kinds-C++=+px", -- p:函数原型 x:外部/前向声明
			"--output-format=e-ctags",
		}
		vim.g.gutentags_ctags_tagfile = ".tags"

		-- 项目根识别：git 仓库或构建文件所在目录
		vim.g.gutentags_add_default_project_roots = false
		vim.g.gutentags_project_root = { ".git", "compile_commands.json", "CMakeLists.txt", "meson.build" }
		vim.g.gutentags_exclude_project_root = { "/usr", "/opt", "/home/dengbo/.workbuddy" }

		-- 首次进入项目时生成；保存文件时后台增量更新
		vim.g.gutentags_generate_on_missing = 1
		vim.g.gutentags_generate_on_write = 1
		vim.g.gutentags_generate_on_empty_buffer = 0
		vim.g.gutentags_background_update = 1
		vim.g.gutentags_trace = 0

		-- 生成索引时不要弹出 quickfix 抢焦点
		vim.g.gutentags_fake_gutentags_quickfix = 1
	end,
}
