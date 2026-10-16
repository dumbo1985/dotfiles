# dotfiles (forMac)

个人 **macOS** Neovim 配置（Homebrew、iTerm2、im-select 输入法自动切换、Neovide 的 Command 快捷键）。nvim 配置树与 `forUbuntu` 分支保持同步——只有平台相关部分不同。

> 📌 **本分支仅面向 macOS。** Ubuntu 24.04（或含 shell/壁纸/工具箱的整机 dotfiles）请切换到 `forUbuntu` 分支。

[English](README.md) | **中文**

## 🚀 快速使用（新 Mac）

```bash
# 1. 装 Neovim ≥ 0.12 和依赖（需先装 Homebrew）
brew install neovim tree-sitter ripgrep fd universal-ctags node lazygit
brew install laishulu/homebrew/im-select   # 可选：输入法自动切换

# 2. clone + 建立软链
git clone --branch forMac https://github.com/dumbo1985/dotfiles.git ~/dotfiles
mkdir -p ~/.config
[ -e ~/.config/nvim ] && [ ! -L ~/.config/nvim ] && mv ~/.config/nvim ~/.config/nvim.backup
ln -sfn ~/dotfiles/nvim ~/.config/nvim

# 3. 启动——首次运行自动安装插件
nvim
```

推荐补装：`brew install --cask iterm2 font-meslo-lg-nerd-font neovide`。完整细节见[安装文档](docs/zh/installation.md)。

**已有机器更新配置**：`cd ~/dotfiles && git pull`（软链自动指向刷新后的配置树）。

## ✨ 功能特性

- 🎨 **多主题支持**：随机加载主题（tokyonight, kanagawa, catppuccin, rose-pine, sonokai, onenord）
- 🔧 **LSP 支持**：完整的语言服务器协议支持，自动安装和配置
- 🐛 **调试功能**：支持 Python、C/C++（lldb）、Go 等语言的调试
- 📝 **代码格式化**：自动格式化，支持多种语言
- 🔍 **模糊搜索**：Telescope 强大的文件搜索和内容搜索
- 🌳 **语法高亮**：Tree-sitter（main 分支，需 Neovim 0.12+）
- 📋 **自动补全**：nvim-cmp 提供智能代码补全
- 🎯 **输入法自动切换**：im-select 在进入插入模式时恢复上次输入法、退出时自动切回英文（`:IMToggle` 手动切换）
- 🖥️ **Neovide 支持**：⌘S/⌘C/⌘V Command 快捷键，针对 GUI 优化
- 🔁 **与 forUbuntu 同步**：两个分支的 nvim 配置完全一致

## 📋 目录

详细内容按主题拆分到 `docs/zh/` 下：

| 文档 | 内容 |
|---|---|
| [安装文档](docs/zh/installation.md) | Homebrew、Neovim 0.12+/tree-sitter CLI、iTerm2/Nerd Font/Neovide、im-select、首次启动、lldb |
| [配置结构](docs/zh/structure.md) | 仓库目录树 + macOS 专属能力（输入法切换 / Command 快捷键 / lldb 路径） |
| [主要插件](docs/zh/plugins.md) | 插件清单（核心功能 / UI / 开发工具 / 编辑增强 / 主题） |
| [键位映射](docs/zh/keymaps.md) | 全部快捷键速查表 |
| [使用说明](docs/zh/usage.md) | 首次使用、输入法、格式化、调试配置、自定义方式 |
| [故障排除](docs/zh/troubleshooting.md) | 常见报错与解法 |

## 📝 更新日志

### 2026

- ✅ nvim 配置树整体同步自 `forUbuntu` 分支：nvim-treesitter main 分支重写（需 Neovim 0.12+）、telescope 解锁跟随上游、symbols-outline.nvim 换成 hedyhli/outline.nvim、新增 gutentags/markdown/deprecated_fix 模块、lazy-lock 快照
- ✅ 分支由 `main` 改名为 `forMac`；仓库默认分支改为 `forUbuntu`
- ✅ README 重写为英文默认 + 中文版，详细内容拆分至 `docs/`

### 早期优化（2024）

- ✅ 修复重复加载配置问题；修复 LSP 服务器配置未启用问题
- ✅ 优化键位映射，避免冲突；重构配置结构，提高可维护性
- ✅ 分离 Neovide 和输入法配置到独立模块

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Neovim 官方文档](https://neovim.io/doc/)
- [Lazy.nvim 文档](https://github.com/folke/lazy.nvim)
- [Mason.nvim 文档](https://github.com/williamboman/mason.nvim)

---

本分支面向 macOS。安装指南与整机部署脚本在 `forUbuntu` 分支。
