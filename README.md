# dotfiles (forMac)

A personal Neovim configuration for **macOS** (Homebrew, iTerm2, im-select input-method auto-switching, Command-key mappings in Neovide). The whole nvim tree is kept in sync with the `forUbuntu` branch — only the platform-specific parts differ.

> 📌 **This branch is macOS-only.** For Ubuntu 24.04 (or the whole-machine dotfiles with shell/wallpaper/toolbox), switch to the `forUbuntu` branch.

**English** | [中文](README.zh-CN.md)

## 🚀 Quick start (new Mac)

```bash
# 1. Install Neovim >= 0.12 and dependencies (Homebrew required)
brew install neovim tree-sitter ripgrep fd universal-ctags node lazygit
brew install laishulu/homebrew/im-select   # optional: IME auto-switching

# 2. Clone + link the config
git clone --branch forMac https://github.com/dumbo1985/dotfiles.git ~/dotfiles
mkdir -p ~/.config
[ -e ~/.config/nvim ] && [ ! -L ~/.config/nvim ] && mv ~/.config/nvim ~/.config/nvim.backup
ln -sfn ~/dotfiles/nvim ~/.config/nvim

# 3. Launch — plugins install themselves on first run
nvim
```

Recommended extras: `brew install --cask iterm2 font-meslo-lg-nerd-font neovide`. Full details in the [installation doc](docs/en/installation.md).

**Updating an existing machine**: `cd ~/dotfiles && git pull` (the symlink keeps pointing at the refreshed tree).

## ✨ Features

- 🎨 **Multiple colorschemes**: randomly loaded (tokyonight, kanagawa, catppuccin, rose-pine, sonokai, onenord)
- 🔧 **LSP support**: full language-server integration with automatic install and setup
- 🐛 **Debugging**: for Python, C/C++ (lldb), Go and more
- 📝 **Formatting**: automatic formatting for many languages
- 🔍 **Fuzzy finding**: Telescope for files and content
- 🌳 **Syntax highlighting**: Tree-sitter (main branch, Neovim 0.12+)
- 📋 **Completion**: nvim-cmp
- 🎯 **IME auto-switching**: im-select restores your input method in Insert mode and switches back to English on leave (`:IMToggle` for manual control)
- 🖥️ **Neovide support**: ⌘S/⌘C/⌘V Command shortcuts, tuned for the GUI
- 🔁 **Synced with forUbuntu**: the nvim config is identical on both branches

## 📋 Table of Contents

The details live in `docs/en/`, split by topic:

| Doc | Contents |
|---|---|
| [Installation](docs/en/installation.md) | Homebrew, Neovim 0.12+/tree-sitter CLI, iTerm2/Nerd Font/Neovide, im-select, first launch, lldb |
| [Structure](docs/en/structure.md) | Repo tree + macOS-specific capabilities (IME switching / Command shortcuts / lldb path) |
| [Plugins](docs/en/plugins.md) | Plugin list (core / UI / development / editing / colorschemes) |
| [Keymaps](docs/en/keymaps.md) | The full keymap cheat sheet |
| [Usage](docs/en/usage.md) | First run, IME, formatting, debugging setup, customising |
| [Troubleshooting](docs/en/troubleshooting.md) | Common errors and fixes |

## 📝 Changelog

### 2026

- ✅ Synced the whole nvim/ tree with the `forUbuntu` branch: nvim-treesitter main-branch rewrite (Neovim 0.12+ required), telescope unpinned, symbols-outline.nvim replaced by hedyhli/outline.nvim, gutentags/markdown/deprecated_fix modules, lazy-lock snapshot
- ✅ Branch renamed from `main` to `forMac`; `forUbuntu` is now the repo default
- ✅ README rewritten as English-default with a Chinese version, details split into `docs/`

### Earlier work (2024)

- ✅ Fixed duplicated config loading; fixed LSP servers not being enabled
- ✅ Cleaned up keymaps; refactored the config layout for maintainability
- ✅ Split the Neovide and input-method config into their own modules

## 🤝 Contributing

Issues and pull requests are welcome.

## 📄 License

MIT License

## 🔗 Links

- [Neovim documentation](https://neovim.io/doc/)
- [Lazy.nvim documentation](https://github.com/folke/lazy.nvim)
- [Mason.nvim documentation](https://github.com/williamboman/mason.nvim)

---

This branch targets macOS. The install guide and the whole-machine scripts live on `forUbuntu`.
