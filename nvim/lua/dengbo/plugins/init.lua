return {
	-- 被其它插件作为 dependency 拉取；全局 defaults.lazy = true 时保持为懒加载即可
	"nvim-lua/plenary.nvim",
	-- 需在 Tmux/分窗间导航时尽早生效
	{ "christoomey/vim-tmux-navigator", lazy = false },
}
