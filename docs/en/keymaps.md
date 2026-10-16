[← Back to README](../../README.md)

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

