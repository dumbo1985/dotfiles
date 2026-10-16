[← 返回 README](../../README.zh-CN.md)

## 📖 使用说明

### 首次使用

1. 启动 Neovim 后，插件会自动安装
2. 等待 Mason 安装 LSP 服务器和工具（首次可能需要较长时间）
3. 主题会随机加载，每次启动可能不同

### 输入法

macOS 上的输入法自动切换已启用（配合 `im-select`）：

- 进入插入模式时，自动恢复上次使用的输入法
- 退出插入模式时，自动切换到英文输入法（`com.apple.keylayout.ABC`）
- 使用 `:IMToggle` 命令手动切换

`core/init.lua` 用 `has("mac")` 且 `im-select` 可执行做了守卫，未安装 im-select 时相关代码不会加载。安装方式见[安装文档](installation.md)第 5 步。

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

1. 安装 lldb：`brew install llvm`。Mason 会安装 `cpptools` 调试适配器。
2. 在 Neovim 中启动调试并选择 **`Launch with lldb`** 配置——适配器路径已指向 `/opt/homebrew/opt/llvm/bin/lldb-vscode`，本分支开箱可用。
3. `Launch file with gdb` 配置在 macOS 上不可用（gdb 需要繁琐的签名），请统一使用 lldb。

### 自定义配置

所有配置都在 `lua/dengbo/` 目录下，可以根据需要修改：

- **选项配置**：`core/options.lua`
- **键位映射**：`core/keymaps.lua`
- **插件配置**：`plugins/` 目录下对应文件
- **LSP 配置**：`plugins/lsp/lspconfig.lua`

