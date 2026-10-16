[← Back to README](../../README.md)

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

