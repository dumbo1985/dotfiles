--- Lazy.nvim 主入口文件
--- 负责协调各个模块的初始化
--- @module dengbo.lazy

-- 首先修复弃用 API 的兼容性问题（必须在插件加载前）
require("dengbo.core.deprecated_fix").setup()

-- 初始化 Lazy.nvim
require("dengbo.core.lazy_init").setup()

-- 平台特定功能
require("dengbo.platform.input_method").setup()

-- 核心功能
require("dengbo.core.folding").setup()

-- UI 配置
require("dengbo.ui.neovide").setup()
require("dengbo.ui.transparent").setup()
require("dengbo.ui.theme").setup()
