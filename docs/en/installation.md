[← Back to README](../../README.md)

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
- symlinks `~/.config/clangd/config.yaml` (unconfigured projects still resolve Qt and other system libs; see [Other configs in this repo](structure.md))
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

> 💡 The macOS-only ability to switch back to English on `InsertLeave` via `im-select` is **not enabled on the `forUbuntu` branch**. If you want it, use the `forMac` branch or port it yourself. On Ubuntu you can bind an Fcitx5 "toggle Chinese/English" key (e.g. `Ctrl+Space`) instead.

### 8. (Optional) One-command CLI toolbox

```bash
bash ~/dotfiles/toolbox/ubuntu24-cli-toolbox.sh             # from apt: eza/bat/fd/zoxide/tmux/tig/direnv/fzf, ...
bash ~/dotfiles/toolbox/install-extra-cli-tools.sh --dry-run # outside apt: lazygit/dust/procs/fastfetch/zellij, ... (preview)
```

The first script installs modern CLI tools grouped by purpose and appends a marked `>>> cli-toolbox >>>` block to `~/.bashrc` (ls/ll aliases, zoxide/direnv/thefuck integration, fzf key bindings, colored man pages); re-running does not duplicate the block. The second downloads prebuilt binaries from each project's GitHub Releases (versions resolved at runtime) and supports `--dry-run`, per-tool selection, and `--force`. Both need sudo/network and are therefore not run by `install.sh`.

