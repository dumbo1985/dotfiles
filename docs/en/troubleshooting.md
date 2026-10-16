[← Back to README](../../README.md)

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

