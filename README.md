# dotfiles

A personal development-environment dotfiles collection (Neovim + shell jump commands + clangd fallback + ble.sh integration + daily wallpaper). The `forUbuntu` branch targets **Ubuntu 24.04** and includes LSP, debugging, formatting and completion setup; the `forMac` branch keeps the macOS configuration (including `im-select` input-method switching and Command-key mappings). A fresh machine only needs this repo cloned and `install.sh` run.

> 📌 **Everything below assumes Ubuntu 24.04.** No macOS/Homebrew instructions are included on this branch. If you are on macOS, switch to the `forMac` branch.

**English** | [中文](README.zh-CN.md)

## 🚀 Quick start (new machine)

```bash
# 1. Install Neovim >= 0.12 (the only manual prerequisite; skip the apt line if git/curl exist)
sudo apt install -y git curl
mkdir -p ~/.local/opt ~/.local/bin
curl -fLo /tmp/nvim.tar.gz https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
tar -xzf /tmp/nvim.tar.gz -C ~/.local/opt
ln -sfn ~/.local/opt/nvim-linux-x86_64/bin/nvim ~/.local/bin/nvim

# 2. Clone + one-command bootstrap (no sudo needed for this step)
git clone --branch forUbuntu https://github.com/dumbo1985/dotfiles.git ~/dotfiles
~/dotfiles/install.sh          # add --skip-wallpaper if you don't want the wallpaper feature

# 3. Run the apt command the script prints at the end (ripgrep / ctags / gdb etc., needs sudo), then reopen the terminal
```

After these three steps: the `workspace` / `dengprojects` terminal jump commands work; nvim installs its plugins on first launch; for C/C++ projects run `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` once for full LSP navigation — unconfigured projects still get the Qt6 fallback, so they don't drown in errors.

**Optional** (needs sudo, see [installation](docs/en/installation.md) step 8):

```bash
bash ~/dotfiles/toolbox/ubuntu24-cli-toolbox.sh               # modern CLI tools from apt
bash ~/dotfiles/toolbox/install-extra-cli-tools.sh --dry-run  # tools outside apt (preview first)
```

**Updating an existing machine**: `cd ~/dotfiles && git pull && ./install.sh` (idempotent, safe to re-run).

## ✨ Features

- 🎨 **Multiple colorschemes**: randomly loaded (tokyonight, kanagawa, catppuccin, rose-pine, sonokai, onenord)
- 🔧 **LSP support**: full language-server integration with automatic install and setup
- 🐛 **Debugging**: for Python, C/C++, Go and more
- 📝 **Formatting**: automatic formatting for many languages
- 🔍 **Fuzzy finding**: Telescope for files and content
- 🌳 **Syntax highlighting**: Tree-sitter
- 📋 **Completion**: nvim-cmp
- 🎯 **Input method**: Ubuntu uses the desktop IME (Fcitx5/Rime, etc.) with no plugin switching; `im-select` auto-switching is `forMac`-branch only
- 🖥️ **Neovide support**: tuned for the Neovide GUI
- 🧰 **Fast machine bootstrap**: `install.sh` deploys nvim / clangd / blerc / jump commands / daily wallpaper in one idempotent run

## 📋 Table of Contents

The details live in `docs/en/`, split by topic:

| Doc | Contents |
|---|---|
| [Installation](docs/en/installation.md) | Requirements, system deps, Neovim/Nerd Font/Neovide, install.sh, first launch, input method, CLI toolbox |
| [Structure](docs/en/structure.md) | Repo tree + other configs in the repo (jump commands / blerc / clangd fallback / wallpaper / toolbox) |
| [Plugins](docs/en/plugins.md) | Plugin list (core / UI / development / editing / colorschemes) |
| [Keymaps](docs/en/keymaps.md) | The full keymap cheat sheet |
| [Usage](docs/en/usage.md) | First run, formatting, debugging setup, customising |
| [Troubleshooting](docs/en/troubleshooting.md) | Common errors and fixes |

## 📝 Changelog

### forUbuntu branch (2026)

- ✅ Rewrote the install guide for Ubuntu 24.04 and dropped macOS-only steps
- ✅ Documented the general `--appimage-extract` workaround for hosts without FUSE
- ✅ Added Markdown rendering and browser preview (`<leader>mt` / `<leader>mp`)
- ✅ Added Linux terminal clipboard keymaps for the toggleterm float
- ✅ Fixed the `vim.lsp.buf_get_clients` deprecation warning
- ✅ Fixed the deprecated Neovide option `neovide_transparency` → `neovide_opacity`
- ✅ Updated symbols-outline icons to Nerd Font v3 codepoints
- ✅ Promoted the repo to whole-machine dotfiles: idempotent `install.sh` + `bash/jump.sh`, `ble/blerc`, `clangd/config.yaml`, `wallpaper/`, `toolbox/`
- ✅ Stopped pinning plugin branches (the committed `lazy-lock.json` remains as a rollback snapshot); Neovim requirement raised to 0.12+
- ✅ Slimmed the README down to a quick start + index; details split into `docs/zh/` and `docs/en/`
- ⚠️ Known leftovers: Neovide's `<D-*>` keymaps and the lldb adapter path are still macOS-only (see the relevant sections)

### Earlier work (2024)

- ✅ Fixed duplicated config loading
- ✅ Fixed LSP servers not being enabled
- ✅ Cleaned up keymaps to avoid conflicts
- ✅ Refactored the config layout for maintainability
- ✅ Split the Neovide and input-method config into their own modules
- ✅ Fixed a misplaced symbols-outline keymap

## 🤝 Contributing

Issues and pull requests are welcome.

## 📄 License

MIT License

## 🔗 Links

- [Neovim documentation](https://neovim.io/doc/)
- [Lazy.nvim documentation](https://github.com/folke/lazy.nvim)
- [Mason.nvim documentation](https://github.com/williamboman/mason.nvim)

---

The `forUbuntu` branch targets Ubuntu 24.04; the install guide and some Neovide/debug settings on `forMac` target macOS.
