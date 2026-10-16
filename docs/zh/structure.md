[← 返回 README](../../README.zh-CN.md)

## 📁 配置结构

本分支只包含 Neovim 配置（`forUbuntu` 分支才是整机 dotfiles，含 shell/壁纸/工具箱）：

```
.
├── README.md / README.zh-CN.md   # 英文（默认）与中文说明
├── docs/
│   ├── en/                        # 英文详细文档（installation / structure / plugins / keymaps / usage / troubleshooting）
│   └── zh/                        # 中文详细文档（同上，一一对应）
└── nvim/                          # Neovim 配置（软链到 ~/.config/nvim）
    ├── init.lua                   # 入口文件
    ├── lazy-lock.json             # 插件版本锁定文件（回滚快照）
    └── lua/dengbo/
        ├── core/                  # 核心配置
        │   ├── init.lua           # 核心入口（加载输入法切换：has("mac") 且 im-select 存在时）
        │   ├── options.lua        # Neovim 选项
        │   ├── keymaps.lua        # 全局键位映射
        │   ├── neovide.lua        # Neovide GUI 配置（⌘S/⌘C/⌘V 等 Command 快捷键）
        │   ├── input_method.lua   # 输入法自动切换（im-select，macOS 专属，本分支主力启用）
        │   ├── deprecated_fix.lua # 弃用 API 兼容补丁
        │   ├── folding.lua        # 代码折叠
        │   └── lazy_init.lua      # lazy.nvim bootstrap
        ├── platform/
        │   └── input_method.lua   # 输入法切换的备用实现
        ├── ui/                    # 主题随机加载、透明度
        ├── lazy.lua               # 插件管理和主题加载
        └── plugins/               # 插件配置（lsp/、telescope、treesitter、outline、dap、gutentags、markdown、formatting …）
```

## 🧩 macOS 专属能力

- **输入法自动切换**：`core/init.lua` 检测到 `has("mac")` 且 `im-select` 可执行时自动加载 `core/input_method.lua`——进入插入模式恢复上次输入法、退出时自动切回英文（`com.apple.keylayout.ABC`），`:IMToggle` 手动切换。依赖 im-select（`brew install laishulu/homebrew/im-select`）。
- **Command 快捷键**：Neovide 内 `⌘S` 保存、`⌘C` 复制、`⌘V` 粘贴（Normal/Visual/Command/Insert/Terminal 全模式），配置在 `core/neovide.lua`。
- **lldb 调试路径**：`plugins/nvim-dap-cpp.lua` 的 lldb 适配器指向 `/opt/homebrew/opt/llvm/bin/lldb-vscode`（`brew install llvm`）。

其余配置（插件、键位、LSP、treesitter、outline 等）与 `forUbuntu` 分支的 nvim 完全一致，两边同步维护。
