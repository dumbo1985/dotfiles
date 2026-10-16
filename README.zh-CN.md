# dotfiles

个人开发环境配置集合（Neovim + shell 跳转命令 + clangd 兜底 + ble.sh 集成 + 每日壁纸）。当前 `forUbuntu` 分支面向 **Ubuntu 24.04**，包含 LSP、调试、格式化和代码补全配置；`forMac` 分支保留 macOS 配置（含 `im-select` 输入法自动切换与 Command 键映射）。新机器只需 clone 本仓库并运行 `install.sh` 即可完成部署。

> 📌 **本分支的安装与使用说明均以 Ubuntu 24.04 为准**，不会包含 macOS（Homebrew 等）的安装方式。若你在 macOS 上使用，请切换到 `forMac` 分支。

[English](README.md) | **中文**

## 🚀 快速使用（新机器）

```bash
# 1. 装 Neovim ≥ 0.12（唯一必须提前手动做的；机器上已有 git/curl 则跳过 apt 行）
sudo apt install -y git curl
mkdir -p ~/.local/opt ~/.local/bin
curl -fLo /tmp/nvim.tar.gz https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
tar -xzf /tmp/nvim.tar.gz -C ~/.local/opt
ln -sfn ~/.local/opt/nvim-linux-x86_64/bin/nvim ~/.local/bin/nvim

# 2. clone + 一键部署（这一步不需要 sudo）
git clone --branch forUbuntu https://github.com/dumbo1985/dotfiles.git ~/dotfiles
~/dotfiles/install.sh          # 不想要壁纸功能就加 --skip-wallpaper

# 3. 照脚本末尾打印的命令补系统依赖（ripgrep / ctags / gdb 等，需 sudo），然后重开终端
```

做完这三步：终端里 `workspace` / `dengprojects` 跳转命令可用；进 nvim 首次启动自动装插件；C/C++ 项目跑一次 `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` 即可获得完整 LSP 跳转——没 configure 的项目也有 Qt6 兜底配置，不至于满屏报错。

**可选**（需要 sudo，见[安装文档](docs/zh/installation.md)第 8 步）：

```bash
bash ~/dotfiles/toolbox/ubuntu24-cli-toolbox.sh               # eza/bat/fd/tmux 等官方源内工具箱
bash ~/dotfiles/toolbox/install-extra-cli-tools.sh --dry-run  # lazygit/dust/fastfetch 等官方源外工具（先预览）
```

**已有机器更新配置**：`cd ~/dotfiles && git pull && ./install.sh`（幂等，可重复执行）。

## ✨ 功能特性

- 🎨 **多主题支持**：随机加载主题（tokyonight, kanagawa, catppuccin, rose-pine, sonokai, onenord）
- 🔧 **LSP 支持**：完整的语言服务器协议支持，自动安装和配置
- 🐛 **调试功能**：支持 Python、C/C++、Go 等语言的调试
- 📝 **代码格式化**：自动格式化，支持多种语言
- 🔍 **模糊搜索**：Telescope 强大的文件搜索和内容搜索
- 🌳 **语法高亮**：Tree-sitter 提供更好的语法高亮
- 📋 **自动补全**：nvim-cmp 提供智能代码补全
- 🎯 **输入法**：Ubuntu 使用桌面输入法（Fcitx5/Rime 等），无需插件切换；macOS 上的 `im-select` 自动切换仅在 `forMac` 分支启用
- 🖥️ **Neovide 支持**：针对 Neovide GUI 的优化配置
- 🧰 **整机快速迁移**：`install.sh` 一键把 nvim / clangd / blerc / 跳转命令 / 每日壁纸部署到新机器，幂等可重跑

## 📋 目录

详细内容按主题拆分到 `docs/zh/` 下：

| 文档 | 内容 |
|---|---|
| [安装文档](docs/zh/installation.md) | 前置要求、系统依赖、Neovim/Nerd Font/Neovide 安装、install.sh、首次启动、输入法、CLI 工具箱 |
| [配置结构](docs/zh/structure.md) | 仓库目录树 + 仓库内的其他配置（跳转命令 / blerc / clangd 兜底 / 壁纸 / 工具箱） |
| [主要插件](docs/zh/plugins.md) | 插件清单（核心功能 / UI / 开发工具 / 编辑增强 / 主题） |
| [键位映射](docs/zh/keymaps.md) | 全部快捷键速查表 |
| [使用说明](docs/zh/usage.md) | 首次使用、格式化、调试配置、自定义方式 |
| [故障排除](docs/zh/troubleshooting.md) | 常见报错与解法 |

## 📝 更新日志

### forUbuntu 分支（2026）

- ✅ 安装说明全面改写为 Ubuntu 24.04 流程，移除 macOS 专属步骤
- ✅ 新增 FUSE 缺失时用 `--appimage-extract` 运行 AppImage 的通用方案
- ✅ 新增 Markdown 渲染与浏览器预览（`<leader>mt` / `<leader>mp`）
- ✅ 新增 Linux 终端剪贴板快捷键（toggleterm 浮窗内）
- ✅ 修复 `vim.lsp.buf_get_clients` 弃用警告
- ✅ 修复 Neovide 废弃选项 `neovide_transparency` → `neovide_opacity`
- ✅ 更新 symbols-outline 图标至 Nerd Font v3 码点
- ✅ 仓库升级为整机配置：`install.sh` 幂等一键部署 + `bash/jump.sh`、`ble/blerc`、`clangd/config.yaml`、`wallpaper/`、`toolbox/`
- ✅ 插件不锁分支跟随上游（`lazy-lock.json` 仍提交作为回滚快照）；Neovim 要求提升至 0.12+
- ✅ README 精简为快速上手 + 索引，详细文档拆分至 `docs/zh/`、`docs/en/`
- ⚠️ 已知遗留：Neovide 的 `<D-*>` 快捷键、lldb 适配器路径仍为 macOS 配置（见对应章节）

### 早期优化（2024）

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

`forUbuntu` 分支的教程以 Ubuntu 24.04 为目标；`forMac` 分支中的安装说明和部分 Neovide/调试设置面向 macOS。
