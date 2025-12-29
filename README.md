# Neovim 配置

一个现代化、模块化的 Neovim 配置，遵循 SOLID 原则设计，支持跨平台使用（Linux、macOS、Windows）。

## ✨ 特性

- 🎨 **现代化 UI**：支持多种主题（tokyonight、kanagawa、catppuccin、rose-pine、sonokai、onenord），随机主题选择
- 🚀 **高性能**：使用 lazy.nvim 进行插件懒加载，优化启动速度
- 🔧 **LSP 支持**：完整的 Language Server Protocol 支持，包括 Mason 自动安装
- 🎯 **代码补全**：nvim-cmp 提供强大的自动补全功能
- 🌳 **语法高亮**：Treesitter 提供精确的语法高亮和代码折叠
- 🔍 **模糊搜索**：Telescope 提供强大的文件搜索和内容搜索
- 🐛 **调试支持**：nvim-dap 提供完整的调试功能（Python、C++）
- 📝 **代码格式化**：Conform.nvim 和多种格式化工具支持
- 🎨 **Neovide 支持**：完整的 Neovide GUI 配置
- 🏗️ **模块化设计**：遵循 SOLID 原则，代码结构清晰，易于维护

## 📋 系统要求

- **Neovim**: 0.12.0+ (推荐使用最新版本)
- **操作系统**: Linux、macOS 或 Windows
- **终端**: 支持真彩色的终端（推荐使用 Neovide 或 iTerm2）

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url> ~/dotfiles
cd ~/dotfiles
```

### 2. 创建符号链接

```bash
# Linux/macOS
ln -s ~/dotfiles/nvim ~/.config/nvim

# 或者使用绝对路径
ln -s /home/pnd-humanoid/dotfiles/nvim ~/.config/nvim
```

### 3. 安装依赖

#### Linux

```bash
# 基础工具
sudo apt update
sudo apt install -y git curl build-essential

# Ripgrep (用于 Telescope)
sudo apt install -y ripgrep

# Node.js (用于某些 LSP 服务器)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# lazygit
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v*([^"]+)".*/\1/')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf lazygit.tar.gz
sudo install lazygit /usr/local/bin

# Ruby (某些工具需要)
sudo apt install -y ruby-full

# Nerd Font (推荐)
# 下载并安装 MesloLGS Nerd Font 或其他 Nerd Font
```

#### macOS

```bash
# 使用 Homebrew
brew install git ripgrep node lazygit

# 安装 Nerd Font
brew install --cask font-meslo-lg-nerd-font

# 输入法切换工具 (可选，仅 macOS)
# 下载 im-select: https://github.com/daipeihust/im-select
# 将 im-select-mac 放入 /usr/local/bin
```

### 4. 启动 Neovim

```bash
nvim
```

首次启动时，lazy.nvim 会自动安装所有插件。这可能需要几分钟时间。

## 📁 配置结构

配置采用模块化设计，遵循 SOLID 原则：

```
nvim/
├── init.lua                    # 主入口文件
├── lazy-lock.json             # 插件版本锁定文件
└── lua/
    └── dengbo/
        ├── core/              # 核心功能模块
        │   ├── init.lua       # 核心模块初始化
        │   ├── options.lua    # Neovim 选项配置
        │   ├── keymaps.lua    # 键位映射
        │   ├── lazy_init.lua  # Lazy.nvim 初始化
        │   ├── folding.lua    # 代码折叠配置
        │   └── deprecated_fix.lua  # 弃用 API 兼容性补丁
        ├── ui/                # UI 相关模块
        │   ├── neovide.lua    # Neovide GUI 配置
        │   ├── theme.lua      # 主题配置
        │   └── transparent.lua # 透明背景配置
        ├── platform/          # 平台特定模块
        │   └── input_method.lua  # 输入法切换 (macOS)
        ├── plugins/           # 插件配置
        │   ├── init.lua       # 基础插件
        │   ├── lsp/          # LSP 相关插件
        │   │   ├── mason.lua  # Mason 配置
        │   │   └── lspconfig.lua  # LSP 服务器配置
        │   ├── nvim-cmp.lua  # 代码补全
        │   ├── telescope.lua  # 模糊搜索
        │   ├── treesitter.lua # 语法高亮
        │   └── ...           # 其他插件配置
        └── lazy.lua          # Lazy.nvim 协调器
```

### 设计原则

- **单一职责原则 (SRP)**: 每个模块只负责一个功能
- **开闭原则 (OCP)**: 易于扩展，无需修改现有代码
- **依赖倒置原则 (DIP)**: 高层模块不依赖低层模块，都依赖抽象

## 🔌 主要插件

### 核心功能
- **lazy.nvim**: 插件管理器
- **plenary.nvim**: Lua 工具库

### LSP 和补全
- **nvim-lspconfig**: LSP 配置
- **mason.nvim**: LSP 服务器管理器
- **nvim-cmp**: 代码补全引擎
- **LuaSnip**: 代码片段引擎
- **lsp_signature.nvim**: 函数签名提示

### UI 增强
- **lualine.nvim**: 状态栏
- **bufferline.nvim**: 标签页栏
- **nvim-tree.lua**: 文件树
- **alpha-nvim**: 启动界面
- **noice.nvim**: 现代化 UI
- **which-key.nvim**: 快捷键提示

### 搜索和导航
- **telescope.nvim**: 模糊搜索
- **lightspeed.nvim**: 快速跳转
- **nvim-treesitter**: 语法高亮

### 代码编辑
- **nvim-autopairs**: 自动配对
- **nvim-surround**: 括号操作
- **Comment.nvim**: 代码注释
- **conform.nvim**: 代码格式化
- **nvim-lint**: 代码检查

### Git 集成
- **gitsigns.nvim**: Git 状态显示
- **git-blame.nvim**: Git 责任显示
- **lazygit.nvim**: Git 终端界面

### 调试
- **nvim-dap**: 调试适配器协议
- **nvim-dap-ui**: 调试界面
- **nvim-dap-python**: Python 调试
- **nvim-dap-virtual-text**: 调试虚拟文本

### 主题
- **tokyonight.nvim**
- **kanagawa.nvim**
- **catppuccin**
- **rose-pine**
- **sonokai**
- **onenord.nvim**

## ⌨️ 快捷键参考

### Leader 键
默认 Leader 键为 `<Space>`

### 📁 文件操作

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>ww` | n | 保存文件 |
| `<leader>wq` | n | 保存并退出 |
| `<leader>qq` | n | 强制退出不保存 |
| `<leader>wr` | n | 恢复会话 |
| `<leader>ws` | n | 保存会话 |

### 📂 文件导航

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>ee` | n | 切换文件树 |
| `<leader>ec` | n | 收起文件树 |
| `<leader>er` | n | 刷新文件树 |
| `<leader>eo` | n | 聚焦文件树 |
| `<leader>ef` | n | 在文件树中定位文件 |
| `<leader>ff` | n | 查找文件 (Telescope) |
| `<leader>fr` | n | 最近打开的文件 |
| `<leader>fs` | n | 全局搜索字符串 |
| `<leader>fc` | n | 搜索光标下的字符串 |
| `<leader>ft` | n | 查找 TODO |

### 🎯 代码折叠

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>zc` | n | 折叠当前块 |
| `<leader>zo` | n | 展开当前块 |
| `<leader>za` | n | 切换折叠 |
| `<leader>zR` | n | 展开所有 |
| `<leader>zM` | n | 折叠所有 |

### ✏️ 代码编辑

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `jk` | i | 退出插入模式 |
| `ii` | i | 退出插入模式 |
| `<leader>mp` | n, v | 格式化文件/选中区域 |
| `<leader>l` | n | 触发代码检查 |
| `<leader>s` | n | 替换（配合 motion） |
| `<leader>ss` | n | 替换整行 |
| `<leader>S` | n | 替换到行尾 |
| `<leader>s` | v | 替换选中内容 |
| `<leader>+` | n | 数字加一 |
| `<leader>-` | n | 数字减一 |

### 🔍 搜索和导航

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `n` | n | 跳转下一个搜索项并居中 |
| `N` | n | 跳转上一个搜索项并居中 |
| `G` | n | 跳转文件末尾并居中 |
| `<C-d>` | n | 向下滚动并居中 |
| `<C-u>` | n | 向上滚动并居中 |
| `<leader>nh` | n | 清除搜索高亮 |
| `f` | n, x, o | Lightspeed 快速跳转 |
| `F` | n, x, o | Lightspeed 反向跳转 |
| `]t` | n | 跳转到下一个 TODO |
| `[t` | n | 跳转到上一个 TODO |

### 🪟 窗口管理

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>sv` | n | 垂直分屏 |
| `<leader>sh` | n | 水平分屏 |
| `<leader>se` | n | 使分屏大小相等 |
| `<leader>sx` | n | 关闭当前分屏 |
| `<leader>sj` | n | 减小分屏高度 |
| `<leader>sk` | n | 增加分屏高度 |
| `<leader>sl` | n | 增加分屏宽度 |
| `<leader>ss` | n | 减小分屏宽度 |
| `<leader>sm` | n | 切换最大化窗口 |
| `,w` | n | 选择窗口 |
| `,W` | n | 交换窗口 |

### 📑 标签页和缓冲区

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>td` | n | 关闭当前缓冲区但保留标签页 |
| `<leader>tl` | n | 列出所有缓冲区 |
| `<leader>to` | n | 打开新标签页 |
| `<leader>tx` | n | 关闭当前标签页 |
| `<leader>tf` | n | 当前缓冲区新开标签页 |
| `<leader>tp` | n | 切换到上一个标签页（BufferLine） |
| `<leader>tn` | n | 切换到下一个标签页（BufferLine） |
| `<leader>t]` | n | 切换到下一个标签页（原生） |
| `<leader>t[` | n | 切换到上一个标签页（原生） |
| `<leader>th` | n | 缓冲区向左移动 |
| `<leader>tr` | n | 缓冲区向右移动 |

### 🔧 LSP (Language Server Protocol)

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `K` | n | 显示函数文档（悬停） |
| `<leader>gg` | n | 悬停提示 |
| `gd` | n | 跳转到定义 |
| `gD` | n | 跳转到声明 |
| `gi` | n | 跳转到实现 |
| `gt` | n | 跳转到类型定义 |
| `gr` | n | 查找引用（Telescope） |
| `gs` | n | 函数签名提示 |
| `rr` | n | 重命名 |
| `ga` | n | 代码操作 |
| `<leader>ca` | n | 代码操作 |
| `gf` | n, v | 格式化（LSP） |
| `<leader>cf` | n | 格式化代码 |
| `gl` | n | 显示诊断信息 |
| `gp` | n | 跳转到上一个诊断 |
| `gn` | n | 跳转到下一个诊断 |
| `tr` | n | 文档符号列表 |
| `<leader>en` | n | 跳转到下一个 Error |
| `<leader>ep` | n | 跳转到上一个 Error |
| `<leader>ch` | n | 切换源文件/头文件（C/C++） |
| `<leader>go` | n | 整理导入（Python） |

### 🐛 调试 (DAP)

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>db` | n | 切换断点 |
| `<leader>bc` | n | 设置条件断点 |
| `<leader>bl` | n | 设置日志点 |
| `<leader>br` | n | 清除所有断点 |
| `<leader>ba` | n | 列出所有断点 |
| `<leader>dc` | n | 继续运行 |
| `<leader>dj` | n | 单步跳过 |
| `<leader>dk` | n | 单步进入 |
| `<leader>do` | n | 跳出函数 |
| `<leader>dd` | n | 断开调试 |
| `<leader>dt` | n | 结束调试 |
| `<leader>dp` | n | 切换 REPL |
| `<leader>dl` | n | 运行上一次调试 |
| `<leader>di` | n | 调试悬停变量 |
| `<leader>d?` | n | 浮动显示变量作用域 |
| `<leader>df` | n | 查看调用栈 |
| `<leader>dh` | n | 查看调试命令 |
| `<leader>de` | n | 查找调试错误信息 |
| `<leader>de` | v | 评估表达式 |
| `<leader>tc` | n | 测试当前类（Python） |
| `<leader>tm` | n | 测试当前方法（Python） |

### 🔀 Git 操作

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>gb` | n | 切换 Git 责任人显示 |
| `<leader>lg` | n | 打开 LazyGit |
| `]h` | n | 跳转到下一个 Git hunk |
| `[h` | n | 跳转到上一个 Git hunk |
| `<leader>hs` | n, v | Stage hunk |
| `<leader>hr` | n, v | Reset hunk |
| `<leader>hS` | n | Stage buffer |
| `<leader>hR` | n | Reset buffer |
| `<leader>hu` | n | Undo stage hunk |
| `<leader>hp` | n | Preview hunk |
| `<leader>hb` | n | Blame line |
| `<leader>hB` | n | Toggle line blame |
| `<leader>hd` | n | Diff this |
| `<leader>hD` | n | Diff this ~ |
| `ih` | o, x | 选择 Git hunk（文本对象） |

### 📋 Diff 操作

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>cc` | n | 把改动放到另一个缓冲区 |
| `<leader>cj` | n | 从左边取改动 |
| `<leader>ck` | n | 从右边取改动 |
| `<leader>cn` | n | 跳转到下一个差异块 |
| `<leader>cp` | n | 跳转到上一个差异块 |

### 📝 Quickfix 和诊断

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>qo` | n | 打开 quickfix 列表 |
| `<leader>qf` | n | 跳转到第一个 quickfix 项 |
| `<leader>qn` | n | 跳转到下一个 quickfix 项 |
| `<leader>qp` | n | 跳转到上一个 quickfix 项 |
| `<leader>ql` | n | 跳转到最后一个 quickfix 项 |
| `<leader>qc` | n | 关闭 quickfix 列表 |
| `<leader>xx` | n | 打开/关闭 Trouble 列表 |
| `<leader>xw` | n | 打开 Trouble 工作区诊断 |
| `<leader>xd` | n | 打开 Trouble 文档诊断 |
| `<leader>xq` | n | 打开 Trouble quickfix 列表 |
| `<leader>xl` | n | 打开 Trouble location 列表 |
| `<leader>xt` | n | 在 Trouble 中打开 TODOs |

### 🎨 其他工具

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<leader>es` | n | 打开符号大纲 |
| `gx` | n | 打开光标下的链接（跨平台） |

### 🍎 Neovide (macOS 专用)

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `<D-s>` | n | 保存（Command+S） |
| `<D-c>` | v | 复制（Command+C） |
| `<D-v>` | n, v, c, i | 粘贴（Command+V） |

## 🎨 主题

配置支持多种主题，每次启动会随机选择一个主题：

- **tokyonight** (night 风格)
- **kanagawa** (wave 背景)
- **catppuccin** (mocha 风格)
- **rose-pine** (main 变体)
- **sonokai** (default 风格)
- **onenord**

## 🔧 配置自定义

### 修改主题

编辑 `lua/dengbo/ui/theme.lua` 来修改主题列表或设置固定主题。

### 添加新插件

1. 在 `lua/dengbo/plugins/` 目录下创建新的 `.lua` 文件
2. 返回插件配置表
3. 重启 Neovim，lazy.nvim 会自动安装

### 修改键位映射

编辑 `lua/dengbo/core/keymaps.lua` 来添加或修改快捷键。

## 🌍 平台支持

### Linux
- ✅ 完全支持
- ✅ 自动检测并使用 `xdg-open` 打开链接
- ✅ 输入法切换功能自动禁用

### macOS
- ✅ 完全支持
- ✅ 支持 `im-select` 输入法自动切换
- ✅ 支持 Neovide GUI 配置
- ✅ 使用 `open` 命令打开链接

### Windows
- ✅ 基本支持
- ✅ 使用 `start` 命令打开链接

## 🐛 故障排除

### 插件安装失败

```bash
# 清理并重新安装
rm -rf ~/.local/share/nvim
rm -rf ~/.local/state/nvim
nvim
```

### LSP 服务器未启动

1. 运行 `:Mason` 检查服务器是否已安装
2. 运行 `:LspInfo` 查看 LSP 状态
3. 检查 `lua/dengbo/plugins/lsp/lspconfig.lua` 中的服务器配置

### 性能问题

1. 检查大文件插件是否正常工作：`:checkhealth bigfile`
2. 使用 `:Lazy profile` 查看插件加载时间
3. 禁用不需要的插件

## 📚 相关资源

- [Neovim 官方文档](https://neovim.io/doc/)
- [Lazy.nvim 文档](https://github.com/folke/lazy.nvim)
- [nvim-lspconfig 文档](https://github.com/neovim/nvim-lspconfig)

## 📝 更新日志

### 最新优化
- ✅ 按 SOLID 原则重构代码结构
- ✅ 修复跨平台兼容性问题
- ✅ 添加弃用 API 兼容性补丁
- ✅ 优化 LSP 服务器配置
- ✅ 改进错误处理和平台检测
- ✅ 优化 lazy-lock.json 排序

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**: 这是一个个人配置文件，根据您的需求进行调整。某些插件可能需要额外的系统依赖，请参考各插件的文档。
