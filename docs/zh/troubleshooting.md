[← 返回 README](../../README.zh-CN.md)

## 🔧 故障排除

### 插件安装失败

先检查网络和外部依赖，再在 Neovim 中运行 `:Lazy sync` 重试插件安装；Mason 工具的错误日志可用 `:MasonLog` 查看。不要直接删除 `~/.local/share/nvim`，其中还包含已安装的插件和工具。若仅需重装某个 Mason 包，可在 `:Mason` 中选择该包，或运行 `:MasonUninstall <包名>` 后再运行 `:MasonInstall <包名>`。

### LSP 服务器未启动

1. 检查 Mason 是否已安装服务器：`:Mason`
2. 查看 LSP 日志：`:LspLog`
3. 确保项目中有相应的配置文件（如 `pyproject.toml`、`tsconfig.json` 等）

### Ubuntu 输入法无法在 Neovim 中切换

本分支没有启用 Linux 的输入法自动切换（相关代码有 `has("mac")` 守卫，Ubuntu 下不会加载）。请确认 Fcitx5/IBus 已在 Ubuntu 桌面正常工作，Neovim 会使用系统当前输入法；通过桌面的中英文切换快捷键（如 `Ctrl+Space`）切换即可。

### AppImage 无法运行（Neovide / Neovim）

报错 `Cannot mount AppImage, please check your FUSE setup` 或 `fuse: device not found`，说明系统缺少 FUSE 支持。先按第 4 步尝试 `sudo modprobe fuse` 和安装 `libfuse2`；若仍不可用，用 `--appimage-extract` 解压后直接运行内部的真实二进制（详见第 4 步）。这是环境级问题，与配置文件无关。

### Neovide 启动报 OpenGL 错误

`Failed to create OpenGL context` 通常是显卡驱动或 GL 环境问题。先用 `LIBGL_ALWAYS_SOFTWARE=1 neovide` 验证是否为驱动问题；若是，检查 `glxinfo -B` 输出的渲染器，并确认已正确安装对应显卡驱动。

### 主题未加载

1. 确保主题插件已安装：`:Lazy`
2. 手动加载主题：`:colorscheme tokyonight`

### 性能问题

1. 检查大文件处理：已配置 `bigfile-nvim` 插件
2. 查看启动时间：`:Lazy profile`
3. 禁用不需要的插件

