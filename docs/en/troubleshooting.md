[← Back to README](../../README.md)

## 🔧 Troubleshooting

### Plugin installation fails

Check your network and external dependencies first, then run `:Lazy sync` in Neovim to retry; Mason errors are visible with `:MasonLog`. Do not delete `~/.local/share/nvim` — it also holds the installed plugins and tools. To reinstall a single Mason package, select it in `:Mason`, or run `:MasonUninstall <package>` followed by `:MasonInstall <package>`.

### LSP server does not start

1. Check whether Mason installed the server: `:Mason`
2. Read the LSP log: `:LspLog`
3. Make sure the project has the relevant config file (e.g. `pyproject.toml`, `tsconfig.json`)

### The input method will not switch inside Neovim

1. Make sure `im-select` is installed and on your PATH (`brew install laishulu/homebrew/im-select`)
2. Test with `im-select` (it should print the current input source)
3. Check macOS privacy/security settings — your terminal app needs the relevant permissions

### Neovide fails with an OpenGL error

`Failed to create OpenGL context` usually points at the GPU driver or the GL environment. Verify with `LIBGL_ALWAYS_SOFTWARE=1 neovide`; if that works, inspect the renderer reported by `glxinfo -B` and make sure the correct GPU driver is installed.

### Colorscheme not loaded

1. Make sure the colorscheme plugin is installed: `:Lazy`
2. Load one manually: `:colorscheme tokyonight`

### Performance

1. Large-file handling is covered by `bigfile-nvim`
2. Check startup time: `:Lazy profile`
3. Disable plugins you do not need

