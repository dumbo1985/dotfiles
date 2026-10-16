# dotfiles

A personal development-environment dotfiles collection (Neovim + shell jump commands + clangd fallback + ble.sh integration + daily wallpaper). The `forUbuntu` branch targets **Ubuntu 24.04** and includes LSP, debugging, formatting and completion setup; the `main` branch keeps the macOS configuration (including `im-select` input-method switching and Command-key mappings). A fresh machine only needs this repo cloned and `install.sh` run.

> 📌 **Everything below assumes Ubuntu 24.04.** No macOS/Homebrew instructions are included on this branch. If you are on macOS, switch to the `main` branch.

**English** | [中文](README.zh-CN.md)

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Layout](#-layout)
- [Other configs in this repo](#-other-configs-in-this-repo)
- [Main Plugins](#-main-plugins)
- [Keymaps](#-keymaps)
- [Usage](#-usage)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

- 🎨 **Multiple colorschemes**: randomly loaded (tokyonight, kanagawa, catppuccin, rose-pine, sonokai, onenord)
- 🔧 **LSP support**: full language-server integration with automatic install and setup
- 🐛 **Debugging**: for Python, C/C++, Go and more
- 📝 **Formatting**: automatic formatting for many languages
- 🔍 **Fuzzy finding**: Telescope for files and content
- 🌳 **Syntax highlighting**: Tree-sitter
- 📋 **Completion**: nvim-cmp
- 🎯 **Input method**: Ubuntu uses the desktop IME (Fcitx5/Rime, etc.) with no plugin switching; `im-select` auto-switching is `main`-branch only
- 🖥️ **Neovide support**: tuned for the Neovide GUI
- 🧰 **Fast machine bootstrap**: `install.sh` deploys nvim / clangd / blerc / jump commands / daily wallpaper in one idempotent run

## 🚀 Installation

### Requirements

- Ubuntu 24.04 LTS (commands below assume x86-64)
- Network access to GitHub
- **Neovim 0.12 or newer is required** — nvim-treesitter follows its `main` branch, which only supports 0.12+; the version in the Ubuntu repositories may lag behind the plugins used here
- **tree-sitter CLI 0.26.1+** — needed to compile parsers without a prebuilt binary (C/C++, for example). The Ubuntu package is too old, install it from the [tree-sitter releases](https://github.com/tree-sitter/tree-sitter/releases):
  ```bash
  curl -fL -o ~/tree-sitter.gz https://github.com/tree-sitter/tree-sitter/releases/download/v0.27.1/tree-sitter-linux-x64.gz
  gunzip -f ~/tree-sitter.gz && mv ~/tree-sitter ~/.local/bin/tree-sitter && chmod +x ~/.local/bin/tree-sitter
  ```
- A true-color terminal (e.g. GNOME Terminal, WezTerm)

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y git curl unzip build-essential ripgrep fd-find \
  python3 python3-venv python3-pip nodejs npm golang-go \
  g++ gdb cmake shellcheck wl-clipboard xclip \
  universal-ctags global
```

`universal-ctags` (the `ctags` command) and `global` (GNU GLOBAL, provides `gtags`) build a symbol index via **vim-gutentags**. They are the fallback for jumping around in projects that have no LSP or no `compile_commands.json`; skip them if you never open such projects.

`nodejs`/`npm` and `golang-go` are needed for the JavaScript/TypeScript and Go tooling as well as the Markdown browser preview; you can skip them if you only use C/C++ and Lua, but Mason will report installation failures for the related tools. `wl-clipboard` and `xclip` provide Wayland/X11 clipboard support (Neovim's `"+y`/`"+p` depend on them).

Note that `beautysh`, `yamlfix`, `taplo`, `htmlbeautifier` and friends are installed by Mason and need no apt package; `stylua` for Lua is handled by Mason as well.

### 2. Install Neovim

Use the official Linux release rather than the possibly outdated version in the Ubuntu 24.04 repositories. Check the current asset name in Neovim's [Linux install instructions](https://github.com/neovim/neovim/blob/master/INSTALL.md#linux) first. The example below uses the x86-64 tarball:

```bash
mkdir -p ~/.local/opt ~/.local/bin
curl -fLo /tmp/nvim-linux-x86_64.tar.gz \
  https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
tar -xzf /tmp/nvim-linux-x86_64.tar.gz -C ~/.local/opt
ln -sfn ~/.local/opt/nvim-linux-x86_64/bin/nvim ~/.local/bin/nvim
```

Make sure `~/.local/bin` is on your `PATH`. On Ubuntu's default Bash, add this line to `~/.bashrc` and reopen the terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Confirm the new version is actually the one running:

```bash
command -v nvim
nvim --version | head -n 2
```

On ARM64, pick the corresponding `arm64` asset from the official instructions.

> 💡 If you downloaded the **Neovim AppImage** instead, hosts without FUSE also need the `--appimage-extract` approach described in step 4 — otherwise the `nvim` command fails with a FUSE mount error.

### 3. Install a Nerd Font (recommended)

Nerd Fonts provide the icons used in the statusline, file tree and dashboard. Install Meslo Nerd Font for the current user:

```bash
mkdir -p ~/.local/share/fonts/Meslo
curl -fLo /tmp/Meslo.zip \
  https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.zip
unzip -o /tmp/Meslo.zip -d ~/.local/share/fonts/Meslo
fc-cache -f
```

Select **MesloLGS Nerd Font Mono** in your terminal settings. If icons are missing, check the selected font and `fc-cache`, then restart the terminal.

### 4. (Optional) Install Neovide

Neovide is a separate GUI and is not required to use this configuration. On Ubuntu/Linux, grab the AppImage or archive from [Neovide Releases](https://github.com/neovide/neovide/releases), then run `neovide`.

> ⚠️ **Verify FUSE first.** AppImages are mounted through FUSE; on hosts without `/dev/fuse` (kernel module not loaded, or a container/restricted environment) running the AppImage directly fails with `Cannot mount AppImage, please check your FUSE setup`. To check and fix:
>
> ```bash
> ls /dev/fuse                    # no output means FUSE is unavailable
> sudo modprobe fuse              # try loading the kernel module
> sudo apt install -y libfuse2    # AppImages need the FUSE 2 compatibility layer
> ```
>
> If `/dev/fuse` is still missing after loading the module (common in containers or trimmed kernels), fall back to **extracting the AppImage** instead of mounting it:
>
> ```bash
> mkdir -p ~/Applications/neovide && cd ~/Applications/neovide
> cp ~/Downloads/neovide.AppImage .
> chmod +x neovide.AppImage
> ./neovide.AppImage --appimage-extract     # unpacks squashfs-root/
> ~/Applications/neovide/squashfs-root/usr/bin/neovide --version
> ```
>
> Once it works, symlink it into `~/.local/bin`:
>
> ```bash
> ln -sf ~/Applications/neovide/squashfs-root/usr/bin/neovide ~/.local/bin/neovide
> ```
>
> To launch it from the application menu, also create a desktop entry:
>
> ```bash
> mkdir -p ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
> cp ~/Applications/neovide/squashfs-root/neovide.svg \
>   ~/.local/share/icons/hicolor/scalable/apps/neovide.svg
> cat > ~/.local/share/applications/neovide.desktop <<'EOF'
> [Desktop Entry]
> Type=Application
> Name=Neovide
> Exec=/home/$USER/.local/bin/neovide %F
> Icon=neovide
> Categories=Utility;TextEditor;
> Terminal=false
> EOF
> update-desktop-database ~/.local/share/applications
> ```
>
> The `--appimage-extract` trick works for **any** AppImage (the official Neovim AppImage, other GUI tools) and is the general fallback when FUSE is unavailable.

Neovide's dedicated shortcuts use the macOS Command modifier (`<D-s>` and friends). These do not fire on Ubuntu — use the general shortcuts below instead (e.g. `<leader>ww` to save).

If Neovide fails with `Failed to create OpenGL context`, your GPU driver or GL environment is at fault. Verify with software rendering first:

```bash
LIBGL_ALWAYS_SOFTWARE=1 neovide
```

### 5. Clone the Ubuntu config and bootstrap in one step

```bash
git clone --branch forUbuntu https://github.com/dumbo1985/dotfiles.git ~/dotfiles
~/dotfiles/install.sh
```

`install.sh` is idempotent — safe to re-run — and wires everything up:

- symlinks `~/.config/nvim → ~/dotfiles/nvim` (an existing real directory is backed up as `*.pre-dotfiles.bak`)
- symlinks `~/.config/clangd/config.yaml` (unconfigured projects still resolve Qt and other system libs; see [Other configs in this repo](#-other-configs-in-this-repo))
- symlinks `~/.blerc` (ble.sh + fzf integration; harmless if ble.sh is not installed)
- appends a marked block to `~/.bashrc` sourcing `bash/jump.sh` (the `workspace` / `dengprojects` jump commands)
- copies the daily-wallpaper scripts from `wallpaper/` to `~/.local/bin` and picks a scheduler automatically

On machines where you don't want the wallpaper feature, run `~/dotfiles/install.sh --skip-wallpaper`.

<details>
<summary>Manual method (equivalent, for nvim-only machines)</summary>

```bash
mkdir -p ~/.config
if [ -e ~/.config/nvim ] && [ ! -L ~/.config/nvim ]; then
  mv ~/.config/nvim ~/.config/nvim.backup
fi
ln -sfn ~/dotfiles/nvim ~/.config/nvim
```

If you already cloned the repo, `cd ~/dotfiles && git switch forUbuntu` and then run the linking commands. An existing real config directory is backed up to `~/.config/nvim.backup` first.

</details>

### 6. First launch

```bash
nvim
```

On first launch `lazy.nvim` downloads the plugins, and Mason then installs the LSP servers and tools listed in the config. Restart Neovim when it finishes. Useful checks: `:Lazy` for plugin status, `:Mason` for tool status, `:LspInfo` for the LSP state of the current file.

For C/C++ projects, generate `compile_commands.json` — the clangd setup looks for it in the project's `build/` directory:

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

### 7. (Optional) Enable a Chinese input method

Ubuntu uses the desktop IME; Neovim simply follows the system input method and needs no extra plugin. With Fcitx5/Rime:

```bash
sudo apt install fcitx5 fcitx5-rime fcitx5-config-qt im-config
im-config -n fcitx5
```

Log out and back in, then open the Fcitx 5 config tool and add Rime. Also make sure the clipboard helpers are present (if you skipped step 1):

```bash
sudo apt install -y wl-clipboard xclip    # Wayland / X11 clipboard
```

> 💡 The macOS-only ability to switch back to English on `InsertLeave` via `im-select` is **not enabled on the `forUbuntu` branch**. If you want it, use the `main` branch or port it yourself. On Ubuntu you can bind an Fcitx5 "toggle Chinese/English" key (e.g. `Ctrl+Space`) instead.

### 8. (Optional) One-command CLI toolbox

```bash
bash ~/dotfiles/toolbox/ubuntu24-cli-toolbox.sh             # from apt: eza/bat/fd/zoxide/tmux/tig/direnv/fzf, ...
bash ~/dotfiles/toolbox/install-extra-cli-tools.sh --dry-run # outside apt: lazygit/dust/procs/fastfetch/zellij, ... (preview)
```

The first script installs modern CLI tools grouped by purpose and appends a marked `>>> cli-toolbox >>>` block to `~/.bashrc` (ls/ll aliases, zoxide/direnv/thefuck integration, fzf key bindings, colored man pages); re-running does not duplicate the block. The second downloads prebuilt binaries from each project's GitHub Releases (versions resolved at runtime) and supports `--dry-run`, per-tool selection, and `--force`. Both need sudo/network and are therefore not run by `install.sh`.

## 📁 Layout

```
.
├── install.sh                  # idempotent bootstrap (symlinks nvim/clangd/blerc, bashrc block, wallpaper deploy)
├── nvim/                       # Neovim config (symlinked to ~/.config/nvim)
│   ├── init.lua                # entry point
│   ├── lazy-lock.json          # plugin version lockfile (rollback snapshot)
│   └── lua/dengbo/
│       ├── core/               # core config (options, keymaps, folding, Neovide, ...)
│       ├── platform/           # platform modules (macOS IME implementation, spare)
│       ├── lazy.lua            # plugin manager and colorscheme loading
│       └── plugins/            # plugin configs (lsp/, telescope, treesitter, dap, formatting, ...)
├── bash/
│   └── jump.sh                 # terminal jump commands (workspace / dengprojects)
├── ble/
│   └── blerc                   # ble.sh + fzf integration (symlinked to ~/.blerc)
├── clangd/
│   └── config.yaml             # user-level clangd fallback (Qt6 system-lib paths)
├── toolbox/                    # CLI toolbox (needs sudo, run manually; not run by install.sh)
│   ├── ubuntu24-cli-toolbox.sh # modern CLI tools from apt + bashrc alias block
│   └── install-extra-cli-tools.sh # tools outside apt (GitHub Releases binaries)
└── wallpaper/                  # daily wallpaper (GNOME/gsettings; skippable, unrelated to nvim)
    ├── bin/                    # daily-wallpaper / install-daily-wallpaper / wallpaper-doctor
    └── systemd/                # daily-wallpaper.service / .timer
```

## 🧩 Other configs in this repo

Besides Neovim, the repo manages three things that are easy to lose on a new machine, all wired up by `install.sh`:

- **Shell jump commands (`bash/jump.sh`)**: `workspace` and `dengprojects` cd into their directories from anywhere, accept a subdirectory argument, and complete subdirectories live via Tab. To add a new one, append a line like `_def_jump name "$HOME/some/path"` in `jump.sh`.
- **ble.sh + fzf integration (`ble/blerc`)**: keeps ble.sh's default MULTILINE behavior (RET inserts a newline in multiline input; `C-j` executes). ble.sh itself must be installed separately (`git clone --recursive https://github.com/akinomyoga/ble.sh && make -C ble.sh install PREFIX=~/.local`, then source it from `~/.bashrc`); the file is inert without it.
- **clangd system-lib fallback (`clangd/config.yaml`)**: without a compile database (project never configured via CMake), clangd falls back to bare clang and floods Qt headers with errors. This file adds the Qt6 header paths of the Ubuntu 24.04 apt packages via `-isystem`, so "clone and start reading" projects still jump correctly. Projects with their own `compile_commands.json` are unaffected (`Add` is appended; duplicate paths are harmless). To add other system libs (OpenCV/Eigen, ...), check with `pkg-config --cflags <name>` — see the comments inside the file.
- **Daily wallpaper (`wallpaper/`)**: fetches a new picsum wallpaper on schedule and prunes old ones (keeps only the current one by default). Requires GNOME/gsettings; after deploy, `install-daily-wallpaper` picks the scheduler — systemd user timer when available, otherwise a login autostart plus printed cron instructions. Manage with `install-daily-wallpaper status / now / uninstall`.
- **CLI toolbox (`toolbox/`)**: two standalone installer scripts, see installation step 8. The repo stores the scripts only; the `>>> cli-toolbox >>>` bashrc block they generate is owned by the scripts, not by dotfiles (it does not conflict with the `dotfiles:jump` block).

## 🔌 Main Plugins

### Core

- **lazy.nvim** - plugin manager
- **nvim-lspconfig** - LSP configuration
- **mason.nvim** - LSP/DAP/formatter installer
- **nvim-cmp** - completion engine
- **telescope.nvim** - fuzzy finder
- **nvim-treesitter** - syntax highlighting and parsing
- **render-markdown.nvim** - renders Markdown headings, lists, quotes, code blocks and checkboxes in Neovim
- **markdown-preview.nvim** - live Markdown preview in the browser

### UI

- **alpha-nvim** - dashboard
- **bufferline.nvim** - buffer tabline
- **lualine.nvim** - statusline
- **nvim-tree** - file tree
- **which-key.nvim** - keymap hints
- **noice.nvim** - modern UI

### Development

- **nvim-dap** - debugger
- **conform.nvim** - formatting
- **nvim-lint** - linting
- **gitsigns.nvim** - Git integration
- **todo-comments.nvim** - TODO highlighting
- **vim-gutentags** - automatic ctags/gtags index (fallback when there is no LSP)

### Editing

- **nvim-autopairs** - auto-close brackets
- **nvim-surround** - surround manipulation
- **Comment.nvim** - commenting
- **lightspeed.nvim** - fast motion (requires typing characters)
- **flash.nvim** - one-key window-wide jump (no typing; `<leader>j`)

### Colorschemes

Randomly loaded:
- tokyonight
- kanagawa
- catppuccin
- rose-pine
- sonokai
- onenord

## ⌨️ Keymaps

### Leader key

Leader is `<Space>`.

> 💡 **Tip**: press `<Space>` and pause briefly to see every available shortcut (provided by which-key).

### Basics

| Key | Action | Mode |
|--------|------|------|
| `<leader>ww` | Save file | Normal |
| `<leader>wq` | Save and quit | Normal |
| `<leader>qq` | Force quit without saving | Normal |
| `jk` / `ii` | Leave insert mode | Insert |
| `n` | Next search hit, centered | Normal |
| `N` | Previous search hit, centered | Normal |
| `G` | Go to end of file, centered | Normal |
| `<C-d>` | Scroll down, centered | Normal |
| `<C-u>` | Scroll up, centered | Normal |
| `<leader>nh` | Clear search highlight | Normal |
| `gx` | Open the link under the cursor | Normal |
| `<leader>+` | Increment number | Normal |
| `<leader>-` | Decrement number | Normal |

### File search (Telescope)

| Key | Action |
|--------|------|
| `<leader>ff` | Find files |
| `<leader>fr` | Recently opened files |
| `<leader>fs` | Search string project-wide |
| `<leader>fc` | Search the string under the cursor |
| `<leader>ft` | Find TODOs |

**Inside Telescope**:
| Key | Action |
|--------|------|
| `<C-k>` | Previous result |
| `<C-j>` | Next result |
| `<C-q>` | Send selection to quickfix and open it |

> 📍 Config: `lua/dengbo/plugins/telescope.lua`

### File tree (NvimTree)

| Key | Action |
|--------|------|
| `<leader>ee` | Toggle file tree |
| `<leader>ec` | Collapse file tree |
| `<leader>er` | Refresh file tree |
| `<leader>eo` | Focus file tree |
| `<leader>ef` | Reveal current file in tree |

### Buffers and tabs

| Key | Action |
|--------|------|
| `<leader>td` | Close buffer, keep the tab |
| `<leader>tl` | List all buffers (Telescope) |
| `<leader>to` | Open a new tab |
| `<leader>tx` | Close current tab |
| `<leader>tf` | Open current buffer in a new tab |
| `<leader>tp` | Previous tab (BufferLine) |
| `<leader>tn` | Next tab (BufferLine) |
| `<leader>t]` | Next tab (native) |
| `<leader>t[` | Previous tab (native) |
| `<leader>th` | Move buffer left |
| `<leader>tr` | Move buffer right |

### Splits

| Key | Action |
|--------|------|
| `<leader>sv` | Vertical split |
| `<leader>sh` | Horizontal split |
| `<leader>se` | Equalize split sizes |
| `<leader>sx` | Close current split |
| `<leader>sj` | Decrease split height |
| `<leader>sk` | Increase split height |
| `<leader>sl` | Increase split width |
| `<leader>ss` | Decrease split width |
| `<leader>sm` | Toggle maximize window |
| `,w` | Pick a window (Window Picker) |
| `,W` | Swap two windows (Window Picker) |

> 📍 Window Picker config: `lua/dengbo/plugins/window-picker.lua`

### LSP

> ⚠️ **Note**: these are buffer-local and only active while an LSP client is attached.

| Key | Action | Mode |
|--------|------|------|
| `K` | Hover information | Normal |
| `gd` | Go to definition | Normal |
| `gD` | Go to declaration | Normal |
| `gi` | Go to implementation | Normal |
| `gt` | Go to type definition | Normal |
| `gr` | Find references (Telescope) | Normal |
| `gs` | Signature help | Normal |
| `rr` | Rename | Normal |
| `<leader>cf` | Format code | Normal |
| `<leader>cf` | Format selection | Visual |
| `ga` | Code action | Normal |
| `tr` | Document symbols | Normal |

> 📍 Config: `lua/dengbo/plugins/lsp/lspconfig.lua`

### Diagnostics

| Key | Action |
|--------|------|
| `gl` | Show diagnostics (float) |
| `gp` | Previous diagnostic |
| `gn` | Next diagnostic |
| `<leader>en` | Next error (errors only) |
| `<leader>ep` | Previous error (errors only) |

### Formatting and linting

| Key | Action | Mode |
|--------|------|------|
| `<leader>mp` | Format file or selection | Normal/Visual |
| `<leader>l` | Lint current file | Normal |

> 📍 Formatting config: `lua/dengbo/plugins/formatting.lua`  
> 📍 Linting config: `lua/dengbo/plugins/linting.lua`  
> 💡 Code is formatted on save and linted on buffer enter, after write, and on leaving insert mode.

### Markdown writing and preview

Opening a `.md` file enables Markdown rendering and browser preview. Rendering styles headings, lists, quotes, code blocks and checkboxes for readability while the raw Markdown stays editable. Press `<Space>` to see the related shortcuts.

| Key | Action |
|--------|------|
| `<leader>mt` | Toggle in-editor Markdown rendering |
| `<leader>mp` | Toggle live browser preview |

The browser preview updates as you edit and stays open when Neovim exits. First use installs the preview components; Node.js/npm is required (covered in the install steps).

> 📍 Config: `nvim/lua/dengbo/plugins/markdown.lua`

### Debugging (DAP)

| Key | Action | Category |
|--------|------|------|
| `<leader>db` | Toggle breakpoint | Breakpoints |
| `<leader>bc` | Set conditional breakpoint | Breakpoints |
| `<leader>bl` | Set log point | Breakpoints |
| `<leader>br` | Clear all breakpoints | Breakpoints |
| `<leader>ba` | List all breakpoints (Telescope) | Breakpoints |
| `<leader>dc` | Continue | Control |
| `<leader>dj` | Step over | Control |
| `<leader>dk` | Step into | Control |
| `<leader>do` | Step out | Control |
| `<leader>dd` | Disconnect | Control |
| `<leader>dt` | Terminate | Control |
| `<leader>dl` | Run last debug session | Control |
| `<leader>dp` | Toggle REPL | Control |
| `<leader>di` | Hover a variable | Inspection |
| `<leader>d?` | Float variable scopes | Inspection |
| `<leader>df` | Call stack (Telescope) | Inspection |
| `<leader>dh` | Debug commands (Telescope) | Inspection |
| `<leader>de` | Find debug error messages (Telescope) | Inspection |
| `<leader>de` | Evaluate expression (in DAP UI) | Visual mode |

> 📍 Config: `lua/dengbo/plugins/nvim-dap*.lua`

### Folding

| Key | Action |
|--------|------|
| `<leader>zc` | Fold current block |
| `<leader>zo` | Unfold current block |
| `<leader>za` | Toggle fold |
| `<leader>zR` | Unfold all |
| `<leader>zM` | Fold all |

### Diff

| Key | Action |
|--------|------|
| `<leader>cc` | Put the change into the other buffer |
| `<leader>cj` | Take the change from the left |
| `<leader>ck` | Take the change from the right |
| `<leader>cn` | Next diff hunk |
| `<leader>cp` | Previous diff hunk |

### Quickfix

| Key | Action |
|--------|------|
| `<leader>qo` | Open quickfix list |
| `<leader>qf` | Jump to first quickfix entry |
| `<leader>qn` | Next quickfix entry |
| `<leader>qp` | Previous quickfix entry |
| `<leader>ql` | Jump to last quickfix entry |
| `<leader>qc` | Close quickfix list |

### Trouble

| Key | Action |
|--------|------|
| `<leader>xx` | Toggle Trouble |
| `<leader>xw` | Workspace diagnostics |
| `<leader>xd` | Document diagnostics |
| `<leader>xq` | Quickfix list |
| `<leader>xl` | Location list |
| `<leader>xt` | TODOs in Trouble |

> 📍 Config: `lua/dengbo/plugins/trouble.lua`

### Git

| Key | Action |
|--------|------|
| `<leader>gb` | Toggle Git blame |
| `<leader>lg` | Open LazyGit |

> 📍 LazyGit config: `lua/dengbo/plugins/lazygit.lua`

### Symbols outline

| Key | Action | Scope |
|--------|------|------|
| `<leader>es` | Toggle symbols outline | Global |
| `<Esc>` / `q` | Close | Outline window |
| `<Cr>` | Jump to location | Outline window |
| `o` | Focus location | Outline window |
| `<C-space>` | Hover symbol | Outline window |
| `K` | Toggle preview | Outline window |
| `r` | Rename symbol | Outline window |
| `a` | Code action | Outline window |
| `h` | Collapse | Outline window |
| `l` | Expand | Outline window |
| `W` | Collapse all | Outline window |
| `E` | Expand all | Outline window |
| `R` | Reset folds | Outline window |

> 📍 Config: `lua/dengbo/plugins/symbols-outline.lua`

### Tags (ctags / gtags)

Symbol index generated by **vim-gutentags**. When an LSP client is attached Neovim uses the LSP `tagfunc` first, so this is mostly the fallback for projects with no language server and no `compile_commands.json`.

| Key | Action | Mode/Notes |
|--------|------|-----------|
| `<C-]>` | Jump to definition of symbol under cursor | Normal |
| `<C-t>` | Jump back (pop the tag stack) | Normal |
| `g]` | List all matches and pick one | Normal |
| `<C-W>]` | Jump to definition in a horizontal split | Normal |
| `:tag <name>` | Jump to a symbol by name | Command |
| `:ts <name>` | Search the tag list | Command |
| `:Telescope tags` | Fuzzy search project-wide symbols | Command |
| `:Telescope current_buffer_tags` | Fuzzy search symbols in the current file | Command |

> 📍 Config: `lua/dengbo/plugins/gutentags.lua`
> 💡 Index files live in `~/.cache/nvim/tags/` — never written into your project. They are generated the first time you enter a project and updated incrementally in the background on save.
> 💡 To use GNU GLOBAL instead: set `vim.g.gutentags_modules = { "ctags", "gtags_cscope" }` in that file. From the shell, `gtags` builds the index, `global -x <symbol>` finds definitions and `global -rx <symbol>` finds references.

### Terminal

Opened with `Ctrl+Y` as a floating window (toggleterm).

| Key | Action | Mode |
|--------|------|------|
| `<C-y>` | Toggle terminal float | Normal |
| `<C-S-v>` | Paste from system clipboard | Terminal |
| `<leader>pp` | Paste (backup) | Terminal |
| `<M-v>` | Paste (Alt+V backup) | Terminal |
| `<C-S-c>` | Copy to system clipboard | Terminal |
| `<leader>yy` | Copy (backup) | Terminal |
| `<M-c>` | Copy (Alt+C backup) | Terminal |

> 📍 Config: `lua/dengbo/plugins/toggleterm.lua` and `lua/dengbo/core/keymaps.lua`

> 💡 **Why not `Ctrl+V`?** In normal mode `<C-v>` is Neovim's native **visual block mode** (column selection). Overriding it to paste would silently remove a high-frequency editing feature, so it is left untouched. To paste from the system clipboard in normal/visual mode, use `"+p`.

> 💡 **If `Ctrl+Shift+V` does nothing**, Neovide may be failing to report `<C-S-字母>` on your setup. Use `<leader>pp` or `<M-v>` instead — they are equivalent.

### Other

| Key | Action | Mode/Notes |
|--------|------|-----------|
| `]t` | Next TODO comment | Normal |
| `[t` | Previous TODO comment | Normal |
| `<leader>s` | Substitute (with a motion) | Normal |
| `<leader>ss` | Substitute the whole line | Normal |
| `<leader>S` | Substitute to end of line | Normal |
| `<leader>s` | Substitute selection | Visual |
| `<leader>j` | Flash jump (window-wide, no typing) | Normal/Visual/Operator |
| `<leader>J` | Flash jump (backwards, window-wide) | Normal/Visual/Operator |
| `<leader>jr` | Flash remote | Operator |
| `<leader>jR` | Flash Treesitter search | Operator/Visual |
| `<C-s>` | Toggle Flash search | Command |
| `f` | Search forward and jump (Lightspeed; requires typing) | Normal/Visual/Operator |
| `F` | Search backward and jump (Lightspeed; requires typing) | Normal/Visual/Operator |
| `<C-space>` | Init / grow selection node | Tree-sitter |
| `<BS>` | Shrink selection node | Tree-sitter |
| `<C-k>` | Previous completion item | Insert (nvim-cmp) |
| `<C-j>` | Next completion item | Insert (nvim-cmp) |
| `<C-b>` | Scroll docs up | Insert (nvim-cmp) |
| `<C-f>` | Scroll docs down | Insert (nvim-cmp) |
| `<C-Space>` | Trigger completion | Insert (nvim-cmp) |
| `<C-e>` | Close completion window | Insert (nvim-cmp) |
| `<CR>` | Confirm selection (no auto-select) | Insert (nvim-cmp) |

> 📍 TODO config: `lua/dengbo/plugins/todo-comments.lua`  
> 📍 Substitute config: `lua/dengbo/plugins/substitute.lua`  
> 📍 Flash config: `lua/dengbo/plugins/flash.lua` 💡 `<leader>j` gives one-key window-wide jumps (recommended, no conflicts)  
> 📍 Lightspeed config: `lua/dengbo/plugins/lightspeed.lua` ⚠️ overrides native `f`/`F` and requires typing  
> 📍 Tree-sitter config: `lua/dengbo/plugins/treesitter.lua`  
> 📍 Completion config: `lua/dengbo/plugins/nvim-cmp.lua`

### Filetype-specific

| Key | Action | Filetype |
|--------|------|----------|
| `<leader>go` | Organize imports (Pyright) | Python |
| `<leader>tc` | Test current class | Python |
| `<leader>tm` | Test current method | Python |
| `<leader>ch` | Switch source/header | C/C++ |

### Neovide-specific shortcuts (⚠️ macOS only for now)

These mappings use the Command modifier (`<D-*>`), which is hardcoded with no platform guard, so they **do not work on Ubuntu**. Use the general shortcuts above instead (save with `<leader>ww`; copy/paste with `y`/`p` or the system clipboard registers `"+y`/`"+p`).

| Key | Action | Mode |
|--------|------|------|
| `<D-s>` | Save (Command+S) | Normal |
| `<D-c>` | Copy (Command+C) | Visual |
| `<D-v>` | Paste (Command+V) | Normal/Visual/Command/Insert/Terminal |

> 📍 Config: `lua/dengbo/core/neovide.lua`

### Input method

On Ubuntu the IME is not switched by a plugin — Neovim follows the desktop environment (Fcitx5/Rime, etc.). The macOS-only ability to switch back to English on `InsertLeave` via `:IMToggle` is **not enabled on this branch**.

> 📍 Config: `lua/dengbo/core/input_method.lua` (loaded only when `has("mac")` is true and `im-select` is executable)  
> 📍 Spare implementation: `lua/dengbo/platform/input_method.lua`

### Which-Key hints

Press `<Space>` and pause briefly (500 ms by default) to see all available shortcuts.

> 📍 Config: `lua/dengbo/plugins/which-key.lua`

### Finding every shortcut

If a shortcut is missing here, look in:

- **Global keymaps**: `lua/dengbo/core/keymaps.lua`
- **LSP keymaps**: `lua/dengbo/plugins/lsp/lspconfig.lua`
- **Plugin-specific keymaps**: the relevant file under `lua/dengbo/plugins/*.lua`
- **Neovide keymaps**: `lua/dengbo/core/neovide.lua`

Or search them all with `:Telescope keymaps`.

## 📖 Usage

### First run

1. Plugins install automatically on launch
2. Wait for Mason to install LSP servers and tools (the first run can take a while)
3. A colorscheme is loaded at random, so it may differ on each start

### Input method

Ubuntu uses a desktop IME such as Fcitx5 or IBus; Neovim follows the system input method and needs no extra configuration.

This branch does **not** enable Linux IME auto-switching: both the "switch back to English on `InsertLeave`" behaviour and the `:IMToggle` command are macOS-only (via `im-select`). `core/init.lua` guards them with `has("mac")`, so the code is never even loaded on Ubuntu and has no side effects. If you want the same behaviour on Ubuntu, consider writing an autocmd around `fcitx5-remote`.

### Formatting

Code is formatted on save (`format_on_save`, 1000 ms timeout). The configured formatters (see `plugins/formatting.lua`) are:

- Python: isort + black
- JavaScript/TypeScript/Svelte/CSS/SCSS/JSON/Markdown/GraphQL: prettier (prettierd preferred for CSS/SCSS)
- Lua: stylua
- Go: gofmt
- Rust: rustfmt
- Shell: shellcheck (`sh`), beautysh (`bash`)
- Others: yamlfix (yaml), taplo (toml), htmlbeautifier (html), buf (proto)

### Debugging

#### Python

1. Make sure `debugpy` is installed (Mason does this automatically)
2. Set a breakpoint: `<leader>db`
3. Start debugging: `<leader>dc`

#### C/C++

1. Install system GDB: `sudo apt install gdb`. Mason installs the `cpptools` debug adapter.
2. Start debugging in Neovim and pick the **`Launch file with gdb`** configuration — this one works out of the box on Ubuntu.
3. ⚠️ **Do not pick `Launch with lldb`.** The lldb adapter path in `plugins/nvim-dap-cpp.lua` is still hardcoded to the macOS Homebrew location `/opt/homebrew/opt/llvm/bin/lldb-vscode` and will always fail on Ubuntu. If you genuinely need lldb, point it at the system `lldb-vscode` (e.g. `/usr/bin/lldb-vscode`, requires `sudo apt install lldb`).

### Customising

Everything lives under `lua/dengbo/`:

- **Options**: `core/options.lua`
- **Keymaps**: `core/keymaps.lua`
- **Plugin config**: the matching file under `plugins/`
- **LSP config**: `plugins/lsp/lspconfig.lua`

## 🔧 Troubleshooting

### Plugin installation fails

Check your network and external dependencies first, then run `:Lazy sync` in Neovim to retry; Mason errors are visible with `:MasonLog`. Do not delete `~/.local/share/nvim` — it also holds the installed plugins and tools. To reinstall a single Mason package, select it in `:Mason`, or run `:MasonUninstall <package>` followed by `:MasonInstall <package>`.

### LSP server does not start

1. Check whether Mason installed the server: `:Mason`
2. Read the LSP log: `:LspLog`
3. Make sure the project has the relevant config file (e.g. `pyproject.toml`, `tsconfig.json`)

### The input method will not switch inside Neovim

This branch does not enable Linux IME auto-switching (the code is guarded by `has("mac")` and never loads on Ubuntu). Confirm Fcitx5/IBus works on the Ubuntu desktop — Neovim uses the current system input method. Switch with the desktop's toggle key (e.g. `Ctrl+Space`).

### AppImage will not run (Neovide / Neovim)

`Cannot mount AppImage, please check your FUSE setup` or `fuse: device not found` means FUSE is missing. Try `sudo modprobe fuse` and installing `libfuse2` as described in step 4; if that still fails, use `--appimage-extract` to unpack and run the real binary inside (see step 4). This is an environment-level issue unrelated to the config.

### Neovide fails with an OpenGL error

`Failed to create OpenGL context` usually points at the GPU driver or the GL environment. Verify with `LIBGL_ALWAYS_SOFTWARE=1 neovide`; if that works, inspect the renderer reported by `glxinfo -B` and make sure the correct GPU driver is installed.

### Colorscheme not loaded

1. Make sure the colorscheme plugin is installed: `:Lazy`
2. Load one manually: `:colorscheme tokyonight`

### Performance

1. Large-file handling is covered by `bigfile-nvim`
2. Check startup time: `:Lazy profile`
3. Disable plugins you do not need

## 📝 Changelog

### forUbuntu branch (2026)

- ✅ Rewrote the install guide for Ubuntu 24.04 and dropped macOS-only steps
- ✅ Documented the general `--appimage-extract` workaround for hosts without FUSE
- ✅ Added Markdown rendering and browser preview (`<leader>mt` / `<leader>mp`)
- ✅ Added Linux terminal clipboard keymaps for the toggleterm float
- ✅ Fixed the `vim.lsp.buf_get_clients` deprecation warning
- ✅ Fixed the deprecated Neovide option `neovide_transparency` → `neovide_opacity`
- ✅ Updated symbols-outline icons to Nerd Font v3 codepoints
- ✅ Made English the default README (`README.zh-CN.md` keeps the Chinese version)
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

The `forUbuntu` branch targets Ubuntu 24.04; the install guide and some Neovide/debug settings on `main` target macOS.
