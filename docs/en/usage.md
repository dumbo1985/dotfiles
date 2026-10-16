[← Back to README](../../README.md)

## 📖 Usage

### First run

1. Plugins install automatically on launch
2. Wait for Mason to install LSP servers and tools (the first run can take a while)
3. A colorscheme is loaded at random, so it may differ on each start

### Input method

IME auto-switching is enabled on macOS (via `im-select`):

- the last used IME is restored on entering Insert mode
- English (`com.apple.keylayout.ABC`) is restored on leaving Insert mode
- `:IMToggle` switches manually

`core/init.lua` guards the module with `has("mac")` plus an `im-select` executable check, so nothing loads when im-select is missing. See [installation](installation.md) step 5 for how to install it.

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

1. Install lldb: `brew install llvm`. Mason installs the `cpptools` debug adapter.
2. Start debugging in Neovim and pick the **`Launch with lldb`** configuration — the adapter path points to `/opt/homebrew/opt/llvm/bin/lldb-vscode` and works out of the box on this branch.
3. The `Launch file with gdb` configuration does not work on macOS (gdb requires cumbersome code signing) — use lldb.

### Customising

Everything lives under `lua/dengbo/`:

- **Options**: `core/options.lua`
- **Keymaps**: `core/keymaps.lua`
- **Plugin config**: the matching file under `plugins/`
- **LSP config**: `plugins/lsp/lspconfig.lua`

