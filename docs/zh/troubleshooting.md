[← 返回 README](../../README.zh-CN.md)

## 🔧 故障排除

### 插件安装失败

先检查网络和外部依赖，再在 Neovim 中运行 `:Lazy sync` 重试插件安装；Mason 工具的错误日志可用 `:MasonLog` 查看。不要直接删除 `~/.local/share/nvim`，其中还包含已安装的插件和工具。若仅需重装某个 Mason 包，可在 `:Mason` 中选择该包，或运行 `:MasonUninstall <包名>` 后再运行 `:MasonInstall <包名>`。

### LSP 服务器未启动

1. 检查 Mason 是否已安装服务器：`:Mason`
2. 查看 LSP 日志：`:LspLog`
3. 确保项目中有相应的配置文件（如 `pyproject.toml`、`tsconfig.json` 等）

### 输入法自动切换不工作

1. 确保 `im-select` 已安装并在 PATH 中（`brew install laishulu/homebrew/im-select`）
2. 测试命令：`im-select`（应该输出当前输入法）
3. 检查 macOS 辅助功能/安全性与隐私设置，确认终端 App 有相应权限

### Neovide 启动报 OpenGL 错误

`Failed to create OpenGL context` 通常是显卡驱动或 GL 环境问题。先用 `LIBGL_ALWAYS_SOFTWARE=1 neovide` 验证是否为驱动问题；若是，检查 `glxinfo -B` 输出的渲染器，并确认已正确安装对应显卡驱动。

### 主题未加载

1. 确保主题插件已安装：`:Lazy`
2. 手动加载主题：`:colorscheme tokyonight`

### 性能问题

1. 检查大文件处理：已配置 `bigfile-nvim` 插件
2. 查看启动时间：`:Lazy profile`
3. 禁用不需要的插件

