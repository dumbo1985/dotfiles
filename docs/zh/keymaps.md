[← 返回 README](../../README.zh-CN.md)

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

### Markdown 写作与预览

打开 `.md` 文件后会自动启用 Markdown 渲染和浏览器预览。渲染会把标题、列表、引用、代码块及任务清单显示为更易读的样式；原始 Markdown 语法仍可正常编辑。按 `<Space>` 可查看对应快捷键提示。

| 快捷键 | 功能 |
|--------|------|
| `<leader>mt` | 切换 Neovim 内 Markdown 渲染 |
| `<leader>mp` | 在浏览器中打开/关闭实时预览 |

浏览器预览会随文档编辑更新，并在关闭 Neovim 时保持浏览器页面不自动关闭。首次使用会安装预览所需组件；需要 Node.js/npm（安装步骤已包含）。

> 📍 配置：`nvim/lua/dengbo/plugins/markdown.lua`

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

### 标签跳转（ctags / gtags）

由 **vim-gutentags** 自动生成的符号索引。有 LSP 附着时 Neovim 会优先使用 LSP 的 `tagfunc`，所以这一套主要用于没有语言服务器、也没有 `compile_commands.json` 的项目。

| 快捷键 | 功能 | 模式/说明 |
|--------|------|------|
| `<C-]>` | 跳转到光标下符号的定义 | Normal |
| `<C-t>` | 跳回上一个位置（弹出标签栈） | Normal |
| `g]` | 列出所有匹配项并选择 | Normal |
| `<C-W>]` | 横向分屏跳转到定义 | Normal |
| `:tag <name>` | 按名称跳转到符号 | 命令 |
| `:ts <name>` | 搜索标签列表 | 命令 |
| `:Telescope tags` | 模糊搜索全项目符号 | 命令 |
| `:Telescope current_buffer_tags` | 模糊搜索当前文件符号 | 命令 |

> 📍 配置：`lua/dengbo/plugins/gutentags.lua`
> 💡 索引文件统一放在 `~/.cache/nvim/tags/`，不会写入你的项目；首次进入项目时生成，之后保存文件时后台增量更新。
> 💡 想改用 GNU GLOBAL：把该文件中的 `vim.g.gutentags_modules` 改成 `{ "ctags", "gtags_cscope" }`。命令行用法：`gtags` 生成索引，`global -x <符号>` 查定义，`global -rx <符号>` 查引用。

### 终端

用 `Ctrl+Y` 呼出浮动终端（toggleterm）。

| 快捷键 | 功能 | 模式 |
|--------|------|------|
| `<C-y>` | 切换终端浮窗 | Normal |
| `<C-S-v>` | 粘贴系统剪贴板 | Terminal |
| `<leader>pp` | 粘贴（备用） | Terminal |
| `<M-v>` | 粘贴（Alt+V 备用） | Terminal |
| `<C-S-c>` | 复制到系统剪贴板 | Terminal |
| `<leader>yy` | 复制（备用） | Terminal |
| `<M-c>` | 复制（Alt+C 备用） | Terminal |

> 📍 配置：`lua/dengbo/plugins/toggleterm.lua` 与 `lua/dengbo/core/keymaps.lua`

> 💡 **为什么不用 `Ctrl+V`？** normal 模式下 `<C-v>` 是 Neovim 原生的**可视块模式**（列选择），覆盖它会静默废掉这个高频功能，因此保留原样。普通/可视模式下从系统剪贴板粘贴请用 `"+p`。

> 💡 **若 `Ctrl+Shift+V` 无反应**，可能是 Neovide 在你的环境里无法上报 `<C-S-字母>` 组合键，改用 `<leader>pp` 或 `<M-v>` 即可，效果完全相同。

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

### Neovide 特定快捷键（⚠️ 目前仅对 macOS 有效）

下列映射使用 Command（`<D-*>`）修饰键，代码中写死了 `<D-*>` 且没有平台判断，因此**在 Ubuntu 上不会生效**。Ubuntu 请使用上文的通用快捷键（保存用 `<leader>ww`，复制粘贴用 `y`/`p` 或系统剪贴板 `"+y`/`"+p`）。

| 快捷键 | 功能 | 模式 |
|--------|------|------|
| `<D-s>` | 保存（Command+S） | Normal |
| `<D-c>` | 复制（Command+C） | Visual |
| `<D-v>` | 粘贴（Command+V） | Normal/Visual/Command/Insert/Terminal |

> 📍 配置：`lua/dengbo/core/neovide.lua`

### 输入法

Ubuntu 下不使用插件切换输入法，直接跟随桌面环境（Fcitx5/Rime 等）的当前输入法状态。离开插入模式自动切回英文的 `:IMToggle` 能力仅针对 macOS 实现，**本分支未启用**。

> 📍 配置：`lua/dengbo/core/input_method.lua`（仅在 `has("mac")` 为真且 `im-select` 可执行时加载）  
> 📍 备用实现：`lua/dengbo/platform/input_method.lua`

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

