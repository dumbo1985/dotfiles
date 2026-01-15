# dotfiles

个人 Neovim 配置文件集合，适用于 macOS 系统。包含完整的 LSP、调试、格式化、代码补全等功能配置。

> 💡 注意：本项目主要针对 macOS 系统配置，Ubuntu 分支请查看相应分支。

## 📋 目录

- [功能特性](#功能特性)
- [安装步骤](#安装步骤)
- [配置结构](#配置结构)
- [主要插件](#主要插件)
- [键位映射](#键位映射)
- [使用说明](#使用说明)
- [故障排除](#故障排除)

## ✨ 功能特性

- 🎨 **多主题支持**：随机加载主题（tokyonight, kanagawa, catppuccin, rose-pine, sonokai, onenord）
- 🔧 **LSP 支持**：完整的语言服务器协议支持，自动安装和配置
- 🐛 **调试功能**：支持 Python、C/C++、Go 等语言的调试
- 📝 **代码格式化**：自动格式化，支持多种语言
- 🔍 **模糊搜索**：Telescope 强大的文件搜索和内容搜索
- 🌳 **语法高亮**：Tree-sitter 提供更好的语法高亮
- 📋 **自动补全**：nvim-cmp 提供智能代码补全
- 🎯 **输入法切换**：自动在插入模式和普通模式间切换输入法
- 🖥️ **Neovide 支持**：针对 Neovide GUI 的优化配置

## 🚀 安装步骤

### 前置要求

1. **macOS 系统**（推荐 macOS 12+）
2. **Homebrew** 包管理器
3. **支持真彩色的终端**（如 iTerm2）

### 1. 安装 Homebrew

如果还没有安装 Homebrew：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装 iTerm2

推荐使用 iTerm2 以获得更好的颜色支持：

```bash
   brew install --cask iterm2
   ```

### 3. 安装 Nerd Font

安装一个 Nerd Font 以支持图标显示：

```bash
# 使用 Homebrew 安装 MesloLGS Nerd Font
brew install --cask font-meslo-lg-nerd-font

# 或者手动下载安装其他 Nerd Font
# https://www.nerdfonts.com/font-downloads
```

在 iTerm2 中设置字体：`Preferences > Profiles > Text > Font` 选择安装的 Nerd Font。

### 4. 安装 Neovim

```bash
brew install neovim
```

### 5. 安装 Neovide（可选，GUI 编辑器）

```bash
brew install --cask neovide
```

### 6. 安装其他依赖工具

```bash
# Ripgrep（用于文件搜索）
brew install ripgrep

# Node.js（用于某些 LSP 服务器）
brew install node

# LazyGit（Git 工具）
brew install lazygit

# Ruby（用于某些格式化工具）
brew install ruby

# im-select（输入法切换工具，macOS）
# 访问 https://github.com/daipeihust/im-select
# 下载 macOS 版本并放入 PATH（如 /usr/local/bin）
```

### 7. 配置 Neovim

```bash
# 克隆或下载此仓库
cd ~/dotfiles

# 创建符号链接
ln -s ~/dotfiles/nvim ~/.config/nvim
```

### 8. 启动 Neovim

首次启动 Neovim 时，插件会自动安装：

```bash
nvim
```

等待插件安装完成（可能需要几分钟）。

## 📁 配置结构

```
nvim/
├── init.lua                    # 入口文件
├── lazy-lock.json              # 插件版本锁定文件
└── lua/dengbo/
    ├── core/                   # 核心配置
    │   ├── init.lua           # 核心配置入口
    │   ├── options.lua        # Neovim 选项配置
    │   ├── keymaps.lua         # 全局键位映射
    │   ├── neovide.lua         # Neovide GUI 配置
    │   └── input_method.lua    # 输入法自动切换
    ├── lazy.lua                # 插件管理和主题加载
    └── plugins/                # 插件配置
        ├── init.lua           # 基础插件
        ├── lsp/               # LSP 相关插件
        │   ├── mason.lua      # Mason 包管理器
        │   └── lspconfig.lua   # LSP 服务器配置
        ├── nvim-cmp.lua       # 代码补全
        ├── telescope.lua      # 模糊搜索
        ├── treesitter.lua      # 语法高亮
        ├── nvim-dap.lua       # 调试器
        ├── formatting.lua     # 代码格式化
        ├── linting.lua        # 代码检查
        └── ...                # 其他插件配置
```

## 🔌 主要插件

### 核心功能

- **lazy.nvim** - 插件管理器
- **nvim-lspconfig** - LSP 配置
- **mason.nvim** - LSP/DAP/格式化工具管理器
- **nvim-cmp** - 代码补全引擎
- **telescope.nvim** - 模糊搜索
- **nvim-treesitter** - 语法高亮和代码解析

### UI 增强

- **alpha-nvim** - 启动界面
- **bufferline.nvim** - 缓冲区标签栏
- **lualine.nvim** - 状态栏
- **nvim-tree** - 文件树
- **which-key.nvim** - 键位提示
- **noice.nvim** - 现代化 UI

### 开发工具

- **nvim-dap** - 调试器
- **conform.nvim** - 代码格式化
- **nvim-lint** - 代码检查
- **gitsigns.nvim** - Git 集成
- **todo-comments.nvim** - TODO 高亮

### 编辑增强

- **nvim-autopairs** - 自动配对括号
- **nvim-surround** - 快速操作包围符号
- **Comment.nvim** - 代码注释
- **lightspeed.nvim** - 快速跳转（需要输入字符）
- **flash.nvim** - 一键全窗口跳转（无需输入字符，使用 `<leader>j`）

### 主题

支持的主题（随机加载）：
- tokyonight
- kanagawa
- catppuccin
- rose-pine
- sonokai
- onenord

## ⌨️ 键位映射

### Leader 键

Leader 键设置为 `<Space>`（空格键）

> 💡 **提示**：在 Neovim 中按 `<Space>` 后稍等片刻，会显示所有可用的快捷键提示（需要 which-key 插件）

### 基础操作

| 快捷键 | 功能 | 模式 |
|--------|------|------|
| `<leader>ww` | 保存文件 | Normal |
| `<leader>wq` | 保存并退出 | Normal |
| `<leader>qq` | 强制退出不保存 | Normal |
| `jk` / `ii` | 退出插入模式 | Insert |
| `n` | 跳转下一个搜索项并居中 | Normal |
| `N` | 跳转上一个搜索项并居中 | Normal |
| `G` | 跳转文件末尾并居中 | Normal |
| `<C-d>` | 向下滚动并居中 | Normal |
| `<C-u>` | 向上滚动并居中 | Normal |
| `<leader>nh` | 清除搜索高亮 | Normal |
| `gx` | 打开光标下的链接 | Normal |
| `<leader>+` | 数字加一 | Normal |
| `<leader>-` | 数字减一 | Normal |

### 文件搜索（Telescope）

| 快捷键 | 功能 |
|--------|------|
| `<leader>ff` | 查找文件 |
| `<leader>fr` | 最近打开的文件 |
| `<leader>fs` | 全局搜索字符串 |
| `<leader>fc` | 搜索光标下的字符串 |
| `<leader>ft` | 查找 TODO |

**Telescope 内部**（在 Telescope 窗口中）：
| 快捷键 | 功能 |
|--------|------|
| `<C-k>` | 上一个结果 |
| `<C-j>` | 下一个结果 |
| `<C-q>` | 发送选中项到 quickfix 列表并打开 |

> 📍 配置：`lua/dengbo/plugins/telescope.lua`

### 文件树（NvimTree）

| 快捷键 | 功能 |
|--------|------|
| `<leader>ee` | 切换文件树 |
| `<leader>ec` | 收起文件树 |
| `<leader>er` | 刷新文件树 |
| `<leader>eo` | 聚焦文件树 |
| `<leader>ef` | 在文件树中定位当前文件 |

### 缓冲区/标签页管理

| 快捷键 | 功能 |
|--------|------|
| `<leader>td` | 关闭当前缓冲区但保留标签页 |
| `<leader>tl` | 列出所有缓冲区（Telescope） |
| `<leader>to` | 打开新标签页 |
| `<leader>tx` | 关闭当前标签页 |
| `<leader>tf` | 当前缓冲区新开标签页 |
| `<leader>tp` | 切换到上一个标签页（BufferLine） |
| `<leader>tn` | 切换到下一个标签页（BufferLine） |
| `<leader>t]` | 切换到下一个标签页（原生） |
| `<leader>t[` | 切换到上一个标签页（原生） |
| `<leader>th` | 缓冲区向左移动 |
| `<leader>tr` | 缓冲区向右移动 |

### 分屏管理

| 快捷键 | 功能 |
|--------|------|
| `<leader>sv` | 垂直分屏 |
| `<leader>sh` | 水平分屏 |
| `<leader>se` | 使分屏大小相等 |
| `<leader>sx` | 关闭当前分屏 |
| `<leader>sj` | 减小分屏高度 |
| `<leader>sk` | 增加分屏高度 |
| `<leader>sl` | 增加分屏宽度 |
| `<leader>ss` | 减小分屏宽度 |
| `<leader>sm` | 切换最大化窗口 |
| `,w` | 选择窗口（Window Picker） |
| `,W` | 交换两个窗口（Window Picker） |

> 📍 Window Picker 配置：`lua/dengbo/plugins/window-picker.lua`

### LSP（语言服务器协议）

> ⚠️ **注意**：以下快捷键仅在 LSP 客户端激活时生效（buffer-local）

| 快捷键 | 功能 | 模式 |
|--------|------|------|
| `K` | 显示悬停信息 | Normal |
| `gd` | 跳转到定义 | Normal |
| `gD` | 跳转到声明 | Normal |
| `gi` | 跳转到实现 | Normal |
| `gt` | 跳转到类型定义 | Normal |
| `gr` | 查找引用（Telescope） | Normal |
| `gs` | 函数签名提示 | Normal |
| `rr` | 重命名 | Normal |
| `<leader>cf` | 格式化代码 | Normal |
| `<leader>cf` | 格式化选中内容 | Visual |
| `ga` | 代码操作 | Normal |
| `tr` | 文档符号列表 | Normal |

> 📍 配置：`lua/dengbo/plugins/lsp/lspconfig.lua`

### 诊断（Diagnostics）

| 快捷键 | 功能 |
|--------|------|
| `gl` | 显示诊断信息（浮动窗口） |
| `gp` | 跳转到上一个诊断 |
| `gn` | 跳转到下一个诊断 |
| `<leader>en` | 跳转到下一个错误（仅错误） |
| `<leader>ep` | 跳转到上一个错误（仅错误） |

### 代码格式化与检查

| 快捷键 | 功能 | 模式 |
|--------|------|------|
| `<leader>mp` | 手动格式化文件或选中内容 | Normal/Visual |
| `<leader>l` | 触发当前文件的代码检查 | Normal |

> 📍 格式化配置：`lua/dengbo/plugins/formatting.lua`  
> 📍 检查配置：`lua/dengbo/plugins/linting.lua`  
> 💡 代码会在保存时自动格式化，在进入缓冲区、写入后、离开插入模式时自动检查

### 调试（DAP）

| 快捷键 | 功能 | 分类 |
|--------|------|------|
| `<leader>db` | 切换断点 | 断点管理 |
| `<leader>bc` | 设置条件断点 | 断点管理 |
| `<leader>bl` | 设置日志点 | 断点管理 |
| `<leader>br` | 清除所有断点 | 断点管理 |
| `<leader>ba` | 列出所有断点（Telescope） | 断点管理 |
| `<leader>dc` | 继续运行 | 调试控制 |
| `<leader>dj` | 单步跳过（Step Over） | 调试控制 |
| `<leader>dk` | 单步进入（Step Into） | 调试控制 |
| `<leader>do` | 跳出函数（Step Out） | 调试控制 |
| `<leader>dd` | 断开调试 | 调试控制 |
| `<leader>dt` | 结束调试 | 调试控制 |
| `<leader>dl` | 运行上一次调试 | 调试控制 |
| `<leader>dp` | 切换 REPL | 调试控制 |
| `<leader>di` | 调试悬停变量 | 调试信息 |
| `<leader>d?` | 浮动显示变量作用域 | 调试信息 |
| `<leader>df` | 查看调用栈（Telescope） | 调试信息 |
| `<leader>dh` | 查看调试命令（Telescope） | 调试信息 |
| `<leader>de` | 查找调试错误信息（Telescope） | 调试信息 |
| `<leader>de` | 评估表达式（在 DAP UI 中） | Visual 模式 |

> 📍 配置：`lua/dengbo/plugins/nvim-dap*.lua`

### 代码折叠

| 快捷键 | 功能 |
|--------|------|
| `<leader>zc` | 折叠当前块 |
| `<leader>zo` | 展开当前块 |
| `<leader>za` | 切换折叠 |
| `<leader>zR` | 展开所有 |
| `<leader>zM` | 折叠所有 |

### Diff 操作

| 快捷键 | 功能 |
|--------|------|
| `<leader>cc` | 把改动放到另一个缓冲区 |
| `<leader>cj` | 从左边取改动 |
| `<leader>ck` | 从右边取改动 |
| `<leader>cn` | 跳转到下一个差异块 |
| `<leader>cp` | 跳转到上一个差异块 |

### Quickfix 列表

| 快捷键 | 功能 |
|--------|------|
| `<leader>qo` | 打开 quickfix 列表 |
| `<leader>qf` | 跳转到第一个 quickfix 项 |
| `<leader>qn` | 跳转到下一个 quickfix 项 |
| `<leader>qp` | 跳转到上一个 quickfix 项 |
| `<leader>ql` | 跳转到最后一个 quickfix 项 |
| `<leader>qc` | 关闭 quickfix 列表 |

### Trouble（诊断列表）

| 快捷键 | 功能 |
|--------|------|
| `<leader>xx` | 打开/关闭 Trouble 列表 |
| `<leader>xw` | 打开工作区诊断 |
| `<leader>xd` | 打开文档诊断 |
| `<leader>xq` | 打开 quickfix 列表 |
| `<leader>xl` | 打开位置列表 |
| `<leader>xt` | 在 Trouble 中打开 TODO |

> 📍 配置：`lua/dengbo/plugins/trouble.lua`

### Git 操作

| 快捷键 | 功能 |
|--------|------|
| `<leader>gb` | 切换 Git Blame 显示 |
| `<leader>lg` | 打开 LazyGit |

> 📍 LazyGit 配置：`lua/dengbo/plugins/lazygit.lua`

### 符号大纲（Symbols Outline）

| 快捷键 | 功能 | 位置 |
|--------|------|------|
| `<leader>es` | 切换符号大纲 | 全局 |
| `<Esc>` / `q` | 关闭 | 大纲窗口内 |
| `<Cr>` | 跳转到位置 | 大纲窗口内 |
| `o` | 聚焦位置 | 大纲窗口内 |
| `<C-space>` | 悬停符号 | 大纲窗口内 |
| `K` | 切换预览 | 大纲窗口内 |
| `r` | 重命名符号 | 大纲窗口内 |
| `a` | 代码操作 | 大纲窗口内 |
| `h` | 折叠 | 大纲窗口内 |
| `l` | 展开 | 大纲窗口内 |
| `W` | 折叠所有 | 大纲窗口内 |
| `E` | 展开所有 | 大纲窗口内 |
| `R` | 重置折叠 | 大纲窗口内 |

> 📍 配置：`lua/dengbo/plugins/symbols-outline.lua`

### 其他功能

| 快捷键 | 功能 | 模式/说明 |
|--------|------|-----------|
| `]t` | 跳转到下一个 TODO 注释 | Normal |
| `[t` | 跳转到上一个 TODO 注释 | Normal |
| `<leader>s` | 替换（配合 motion） | Normal |
| `<leader>ss` | 替换整行 | Normal |
| `<leader>S` | 替换到行尾 | Normal |
| `<leader>s` | 替换选中内容 | Visual |
| `<leader>j` | Flash 跳转（全窗口，无需输入字符） | Normal/Visual/Operator |
| `<leader>J` | Flash 跳转（向后，全窗口） | Normal/Visual/Operator |
| `<leader>jr` | Flash 远程操作 | Operator |
| `<leader>jR` | Flash Treesitter 搜索 | Operator/Visual |
| `<C-s>` | 切换 Flash 搜索 | Command |
| `f` | 向前搜索并跳转（Lightspeed，需输入字符） | Normal/Visual/Operator |
| `F` | 向后搜索并跳转（Lightspeed，需输入字符） | Normal/Visual/Operator |
| `<C-space>` | 初始化选择/增量选择节点 | Tree-sitter |
| `<BS>` | 递减选择节点 | Tree-sitter |
| `<C-k>` | 上一个补全项 | Insert（nvim-cmp） |
| `<C-j>` | 下一个补全项 | Insert（nvim-cmp） |
| `<C-b>` | 向上滚动文档 | Insert（nvim-cmp） |
| `<C-f>` | 向下滚动文档 | Insert（nvim-cmp） |
| `<C-Space>` | 显示补全建议 | Insert（nvim-cmp） |
| `<C-e>` | 关闭补全窗口 | Insert（nvim-cmp） |
| `<CR>` | 确认选择（不自动选择） | Insert（nvim-cmp） |

> 📍 TODO 配置：`lua/dengbo/plugins/todo-comments.lua`  
> 📍 替换配置：`lua/dengbo/plugins/substitute.lua`  
> 📍 Flash 配置：`lua/dengbo/plugins/flash.lua` 💡 使用 `<leader>j` 一键全窗口跳转（推荐，不冲突）  
> 📍 Lightspeed 配置：`lua/dengbo/plugins/lightspeed.lua` ⚠️ 覆盖原生 `f`/`F`，需要输入字符  
> 📍 Tree-sitter 配置：`lua/dengbo/plugins/treesitter.lua`  
> 📍 补全配置：`lua/dengbo/plugins/nvim-cmp.lua`

### 文件类型特定操作

| 快捷键 | 功能 | 文件类型 |
|--------|------|----------|
| `<leader>go` | 整理导入（Pyright） | Python |
| `<leader>tc` | 测试当前类 | Python |
| `<leader>tm` | 测试当前方法 | Python |
| `<leader>ch` | 切换源文件/头文件 | C/C++ |

### Neovide 特定快捷键

| 快捷键 | 功能 | 模式 |
|--------|------|------|
| `<D-s>` | 保存（Command+S） | Normal |
| `<D-c>` | 复制（Command+C） | Visual |
| `<D-v>` | 粘贴（Command+V） | Normal/Visual/Command/Insert/Terminal |

> 📍 配置：`lua/dengbo/core/neovide.lua`

### 输入法切换

| 命令/快捷键 | 功能 |
|------------|------|
| `:IMToggle` | 手动切换输入法 |

> 📍 配置：`lua/dengbo/core/input_method.lua`  
> 💡 输入法会在进入/退出插入模式时自动切换

### Which-Key 提示

按 `<Space>` 后稍等片刻（默认 500ms），会显示所有可用的快捷键提示。

> 📍 配置：`lua/dengbo/plugins/which-key.lua`

### 查找所有快捷键

如果某个快捷键没有在这里列出，可以在以下文件中查找：

- **全局键位映射**：`lua/dengbo/core/keymaps.lua`
- **LSP 键位映射**：`lua/dengbo/plugins/lsp/lspconfig.lua`
- **插件特定键位映射**：`lua/dengbo/plugins/*.lua` 各插件配置文件
- **Neovide 键位映射**：`lua/dengbo/core/neovide.lua`

或者使用 `:Telescope keymaps` 搜索所有已定义的快捷键。

## 📖 使用说明

### 首次使用

1. 启动 Neovim 后，插件会自动安装
2. 等待 Mason 安装 LSP 服务器和工具（首次可能需要较长时间）
3. 主题会随机加载，每次启动可能不同

### 输入法自动切换

配置已包含输入法自动切换功能：
- 进入插入模式时，自动恢复上次使用的输入法
- 退出插入模式时，自动切换到英文输入法
- 使用 `:IMToggle` 命令手动切换输入法

### 代码格式化

代码会在保存时自动格式化，支持的格式器：
- Python: isort + black
- JavaScript/TypeScript: prettier
- Lua: stylua
- Go: gofmt
- 其他语言请查看 `plugins/formatting.lua`

### 调试配置

#### Python 调试

1. 确保已安装 `debugpy`（Mason 会自动安装）
2. 在代码中设置断点：`<leader>db`
3. 开始调试：`<leader>dc`

#### C/C++ 调试

1. 确保已安装 `codelldb` 或 `cpptools`（Mason 会自动安装）
2. 需要配置 `launch.json` 或使用适配器配置
3. 查看 `plugins/nvim-dap-cpp.lua` 了解详细配置

### 自定义配置

所有配置都在 `lua/dengbo/` 目录下，可以根据需要修改：

- **选项配置**：`core/options.lua`
- **键位映射**：`core/keymaps.lua`
- **插件配置**：`plugins/` 目录下对应文件
- **LSP 配置**：`plugins/lsp/lspconfig.lua`

## 🔧 故障排除

### 插件安装失败

```bash
# 清理插件缓存
rm -rf ~/.local/share/nvim
rm -rf ~/.local/state/nvim
nvim  # 重新启动，插件会重新安装
```

### LSP 服务器未启动

1. 检查 Mason 是否已安装服务器：`:Mason`
2. 查看 LSP 日志：`:LspLog`
3. 确保项目中有相应的配置文件（如 `pyproject.toml`、`tsconfig.json` 等）

### 输入法切换不工作

1. 确保 `im-select` 已安装并在 PATH 中
2. 测试命令：`im-select`（应该输出当前输入法）
3. 检查 macOS 权限设置

### 主题未加载

1. 确保主题插件已安装：`:Lazy`
2. 手动加载主题：`:colorscheme tokyonight`

### 性能问题

1. 检查大文件处理：已配置 `bigfile-nvim` 插件
2. 查看启动时间：`:Lazy profile`
3. 禁用不需要的插件

## 📝 更新日志

### 最新优化（2024）

- ✅ 修复重复加载配置问题
- ✅ 修复 LSP 服务器配置未启用问题
- ✅ 优化键位映射，避免冲突
- ✅ 重构配置结构，提高可维护性
- ✅ 分离 Neovide 和输入法配置到独立模块
- ✅ 修复 symbols-outline 键位映射位置错误

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Neovim 官方文档](https://neovim.io/doc/)
- [Lazy.nvim 文档](https://github.com/folke/lazy.nvim)
- [Mason.nvim 文档](https://github.com/williamboman/mason.nvim)

---

**注意**：本配置主要针对 macOS 系统。如需在 Ubuntu/Linux 上使用，可能需要调整部分配置（如输入法切换工具）。
