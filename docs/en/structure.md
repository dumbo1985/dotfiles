[← Back to README](../../README.md)

## 📁 Layout

This branch contains the Neovim config only (the `forUbuntu` branch is the whole-machine dotfiles repo with shell/wallpaper/toolbox):

```
.
├── README.md / README.zh-CN.md   # English (default) and Chinese READMEs
├── docs/
│   ├── en/                        # detailed English docs (installation / structure / plugins / keymaps / usage / troubleshooting)
│   └── zh/                        # detailed Chinese docs (same set, one-to-one)
└── nvim/                          # Neovim config (symlinked to ~/.config/nvim)
    ├── init.lua                   # entry point
    ├── lazy-lock.json             # plugin version lockfile (rollback snapshot)
    └── lua/dengbo/
        ├── core/                  # core config
        │   ├── init.lua           # core entry (loads IME switching when has("mac") + im-select)
        │   ├── options.lua        # Neovim options
        │   ├── keymaps.lua        # global keymaps
        │   ├── neovide.lua        # Neovide GUI config (⌘S/⌘C/⌘V Command shortcuts)
        │   ├── input_method.lua   # IME auto-switching (im-select; macOS-only, active on this branch)
        │   ├── deprecated_fix.lua # deprecated-API compatibility shims
        │   ├── folding.lua        # code folding
        │   └── lazy_init.lua      # lazy.nvim bootstrap
        ├── platform/
        │   └── input_method.lua   # spare IME implementation
        ├── ui/                    # random colorscheme loading, transparency
        ├── lazy.lua               # plugin manager and colorscheme loading
        └── plugins/               # plugin configs (lsp/, telescope, treesitter, outline, dap, gutentags, markdown, formatting, ...)
```

## 🧩 macOS-specific capabilities

- **IME auto-switching**: `core/init.lua` loads `core/input_method.lua` automatically once `has("mac")` and an executable `im-select` are detected — the last IME is restored on entering Insert mode, English (`com.apple.keylayout.ABC`) on leaving it; `:IMToggle` switches manually. Requires im-select (`brew install laishulu/homebrew/im-select`).
- **Command shortcuts**: inside Neovide, `⌘S` save, `⌘C` copy, `⌘V` paste (Normal/Visual/Command/Insert/Terminal), configured in `core/neovide.lua`.
- **lldb debug path**: the lldb adapter in `plugins/nvim-dap-cpp.lua` points to `/opt/homebrew/opt/llvm/bin/lldb-vscode` (`brew install llvm`).

Everything else (plugins, keymaps, LSP, treesitter, outline, ...) is identical to the nvim tree on the `forUbuntu` branch; the two are kept in sync.
