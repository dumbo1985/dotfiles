[← Back to README](../../README.md)

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

