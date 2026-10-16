[← 返回 README](../../README.zh-CN.md)

## 📖 使用说明

### 首次使用

1. 启动 Neovim 后，插件会自动安装
2. 等待 Mason 安装 LSP 服务器和工具（首次可能需要较长时间）
3. 主题会随机加载，每次启动可能不同

### 输入法

Ubuntu 使用 Fcitx5、IBus 等桌面输入法，Neovim 直接跟随系统输入法状态，无需额外配置。

本分支**没有启用** Linux 下的输入法自动切换：离开插入模式时自动切回英文、以及 `:IMToggle` 命令，都只在 macOS（配合 `im-select`）上实现。`core/init.lua` 已用 `has("mac")` 做了守卫，因此在 Ubuntu 上相关代码根本不会加载，也不会有副作用。如需在 Ubuntu 实现同样效果，可考虑 `fcitx5-remote` 自行编写 autocmd。

### 代码格式化

代码会在保存时自动格式化（`format_on_save`，超时 1000ms）。配置的格式器（见 `plugins/formatting.lua`）包括：

- Python: isort + black
- JavaScript/TypeScript/Svelte/CSS/SCSS/JSON/Markdown/GraphQL: prettier（CSS/SCSS 优先 prettierd）
- Lua: stylua
- Go: gofmt
- Rust: rustfmt
- Shell: shellcheck（`sh`）、beautysh（`bash`）
- 其他: yamlfix（yaml）、taplo（toml）、htmlbeautifier（html）、buf（proto）

### 调试配置

#### Python 调试

1. 确保已安装 `debugpy`（Mason 会自动安装）
2. 在代码中设置断点：`<leader>db`
3. 开始调试：`<leader>dc`

#### C/C++ 调试

1. 安装系统 GDB：`sudo apt install gdb`。Mason 会安装 `cpptools` 调试适配器。
2. 在 Neovim 中启动调试并选择 **`Launch file with gdb`** 配置（这一项在 Ubuntu 上开箱可用）。
3. ⚠️ **不要选择 `Launch with lldb`**。`plugins/nvim-dap-cpp.lua` 中的 lldb 适配器路径仍然写死为 macOS Homebrew 路径 `/opt/homebrew/opt/llvm/bin/lldb-vscode`，在 Ubuntu 上必然启动失败。若确实需要 lldb 调试，把该路径改为系统的 `lldb-vscode`（例如 `/usr/bin/lldb-vscode`，需 `sudo apt install lldb`）。

### 自定义配置

所有配置都在 `lua/dengbo/` 目录下，可以根据需要修改：

- **选项配置**：`core/options.lua`
- **键位映射**：`core/keymaps.lua`
- **插件配置**：`plugins/` 目录下对应文件
- **LSP 配置**：`plugins/lsp/lspconfig.lua`

