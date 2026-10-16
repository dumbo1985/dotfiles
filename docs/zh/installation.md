[← 返回 README](../../README.zh-CN.md)

## 🚀 安装步骤

### 前置要求

- macOS 系统（推荐 macOS 12+）
- **必须使用 Neovim 0.12 或更新版本** —— nvim-treesitter 跟随其 `main` 分支，该分支只支持 0.12+（`brew install neovim` 即为最新版）
- **tree-sitter CLI 0.26.1+** —— 用于编译没有预编译包的 parser（如 C/C++）。推荐 `brew install tree-sitter`
- 可访问 GitHub 的网络
- 支持真彩色的终端（如 iTerm2）

### 1. 安装 Homebrew

如果还没有安装 Homebrew：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装 Neovim 与依赖工具

```bash
brew install neovim tree-sitter ripgrep fd universal-ctags node lazygit
```

各工具用途：`ripgrep`/`fd`（Telescope 搜索）、`universal-ctags`（vim-gutentags 无 LSP 时的跳转兜底，可省）、`node`（部分 LSP 与 Markdown 浏览器预览）、`lazygit`（`<leader>gg` 集成）。

### 3. 安装 iTerm2 与 Nerd Font（推荐）

```bash
brew install --cask iterm2
brew install --cask font-meslo-lg-nerd-font
```

在 iTerm2 中设置字体：`Preferences > Profiles > Text > Font` 选择安装的 Nerd Font。图标显示为方块通常就是没装 Nerd Font。

### 4. 安装 Neovide（可选，GUI 编辑器）

```bash
brew install --cask neovide
```

Neovide 支持 Command 快捷键（`⌘S` 保存、`⌘C/⌘V` 复制粘贴），见键位映射文档的 Neovide 小节。

### 5. 安装 im-select（输入法自动切换）

```bash
brew install laishulu/homebrew/im-select
```

安装后无需任何配置：`core/init.lua` 检测到 `has("mac")` 且 `im-select` 可执行时会自动加载输入法切换模块——进入插入模式恢复上次输入法、退出时自动切回英文。

### 6. 获取 macOS 配置并建立链接

```bash
git clone --branch forMac https://github.com/dumbo1985/dotfiles.git ~/dotfiles
mkdir -p ~/.config
if [ -e ~/.config/nvim ] && [ ! -L ~/.config/nvim ]; then
  mv ~/.config/nvim ~/.config/nvim.backup
fi
ln -sfn ~/dotfiles/nvim ~/.config/nvim
```

如果已经克隆过仓库，进入 `~/dotfiles` 后运行 `git switch forMac`，再执行链接命令即可。已有的真实配置目录会先备份为 `~/.config/nvim.backup`。

### 7. 首次启动

```bash
nvim
```

首次启动会通过 `lazy.nvim` 下载插件；Mason 随后会安装配置列表中的 LSP 和开发工具。安装完成后重启 Neovim。可在 Neovim 中运行 `:Lazy` 查看插件状态、`:Mason` 查看工具状态、`:LspInfo` 查看当前文件的 LSP 状态。

C/C++ 项目建议生成 `compile_commands.json`，因为 clangd 配置会查找项目 `build/` 目录：

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

### 8.（可选）C/C++ 调试器

- **lldb**：`brew install llvm`，适配器路径已配置为 `/opt/homebrew/opt/llvm/bin/lldb-vscode`（见 `plugins/nvim-dap-cpp.lua`）。
- **gdb**：macOS 上签名繁琐，推荐直接用 lldb。

> 💡 Linux 用户请切换到 `forUbuntu` 分支，那里有针对 Ubuntu 24.04 的完整安装流程与整机部署脚本。
