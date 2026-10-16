[← Back to README](../../README.md)

## 🚀 Installation

### Requirements

- macOS (12+ recommended)
- **Neovim 0.12 or newer** — nvim-treesitter follows its `main` branch, which supports 0.12+ only (`brew install neovim` gives you the latest)
- **tree-sitter CLI 0.26.1+** — needed to compile parsers without prebuilt binaries (e.g. C/C++). Recommended: `brew install tree-sitter`
- Network access to GitHub
- A true-color terminal (e.g. iTerm2)

### 1. Install Homebrew

If Homebrew is not installed yet:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Neovim and dependencies

```bash
brew install neovim tree-sitter ripgrep fd universal-ctags node lazygit
```

What they are for: `ripgrep`/`fd` (Telescope search), `universal-ctags` (vim-gutentags symbol-index fallback when no LSP, optional), `node` (some LSP servers and the Markdown browser preview), `lazygit` (integrated via `<leader>gg`).

### 3. Install iTerm2 and a Nerd Font (recommended)

```bash
brew install --cask iterm2
brew install --cask font-meslo-lg-nerd-font
```

Set the font in iTerm2: `Preferences > Profiles > Text > Font`. Icons rendering as boxes usually means no Nerd Font is installed.

### 4. Install Neovide (optional, GUI editor)

```bash
brew install --cask neovide
```

Neovide supports Command shortcuts (`⌘S` save, `⌘C/⌘V` copy/paste) — see the Neovide section of the keymaps doc.

### 5. Install im-select (input-method auto-switching)

```bash
brew install laishulu/homebrew/im-select
```

No further setup: `core/init.lua` loads the input-method module automatically once `has("mac")` and an executable `im-select` are detected — the last IME is restored on entering Insert mode and English is restored on leaving it.

### 6. Clone the macOS config and link it

```bash
git clone --branch forMac https://github.com/dumbo1985/dotfiles.git ~/dotfiles
mkdir -p ~/.config
if [ -e ~/.config/nvim ] && [ ! -L ~/.config/nvim ]; then
  mv ~/.config/nvim ~/.config/nvim.backup
fi
ln -sfn ~/dotfiles/nvim ~/.config/nvim
```

If you already cloned the repo, `cd ~/dotfiles && git switch forMac` and then run the linking commands. An existing real config directory is backed up to `~/.config/nvim.backup` first.

### 7. First launch

```bash
nvim
```

On first launch `lazy.nvim` downloads the plugins, and Mason then installs the LSP servers and tools listed in the config. Restart Neovim when it finishes. Useful checks: `:Lazy` for plugin status, `:Mason` for tool status, `:LspInfo` for the LSP state of the current file.

For C/C++ projects, generate `compile_commands.json` — the clangd setup looks for it in the project's `build/` directory:

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

### 8. (Optional) C/C++ debugger

- **lldb**: `brew install llvm`; the adapter path is already configured as `/opt/homebrew/opt/llvm/bin/lldb-vscode` (see `plugins/nvim-dap-cpp.lua`).
- **gdb**: painful to sign on macOS — prefer lldb.

> 💡 Linux users: switch to the `forUbuntu` branch, which has a full Ubuntu 24.04 install guide plus whole-machine bootstrap scripts.
