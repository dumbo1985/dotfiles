[← 返回 README](../../README.zh-CN.md)

## 🚀 安装步骤

### 前置要求

- Ubuntu 24.04 LTS（以下命令以 x86-64 为例）
- 可访问 GitHub 的网络
- **必须使用 Neovim 0.12 或更新版本** —— nvim-treesitter 跟随其 `main` 分支，该分支只支持 0.12+；Ubuntu 仓库中的版本可能落后于本配置使用的插件
- **tree-sitter CLI 0.26.1+** —— 用于编译没有预编译包的 parser（如 C/C++）。Ubuntu 仓库里的版本太旧，需从 [tree-sitter 发布页](https://github.com/tree-sitter/tree-sitter/releases)安装：
  ```bash
  curl -fL -o ~/tree-sitter.gz https://github.com/tree-sitter/tree-sitter/releases/download/v0.27.1/tree-sitter-linux-x64.gz
  gunzip -f ~/tree-sitter.gz && mv ~/tree-sitter ~/.local/bin/tree-sitter && chmod +x ~/.local/bin/tree-sitter
  ```
- 支持真彩色的终端（如 GNOME Terminal、WezTerm）

### 1. 安装系统依赖

```bash
sudo apt update
sudo apt install -y git curl unzip build-essential ripgrep fd-find \
  python3 python3-venv python3-pip nodejs npm golang-go \
  g++ gdb cmake shellcheck wl-clipboard xclip \
  universal-ctags global
```

`universal-ctags`（提供 `ctags` 命令）与 `global`（GNU GLOBAL，提供 `gtags`）用于 **vim-gutentags** 生成符号索引，是"没有 LSP、也没有 `compile_commands.json`"的项目里的跳转兜底方案；如果不会打开这类项目，可以不装。

`nodejs`/`npm` 与 `golang-go` 用于 JavaScript/TypeScript、Go 的语言工具以及 Markdown 浏览器预览；若只使用 C/C++ 和 Lua，可以不装，但 Mason 会对相应工具显示安装失败。`wl-clipboard` 和 `xclip` 分别提供 Wayland/X11 剪贴板支持（Neovim 的 `"+y`/`"+p` 依赖它们）。

另外，本配置的格式化器包含 `beautysh`、`yamlfix`、`taplo`、`htmlbeautifier` 等工具，这些由 Mason 自动安装，无需 apt；但 `stylua` 格式化 Lua 需要系统中有对应可执行文件，Mason 会一并处理。

### 2. 安装 Neovim

推荐使用 Neovim 官方 Linux 发布包，而不是 Ubuntu 24.04 仓库中可能较旧的版本。先在 Neovim 官方 [Linux 安装说明](https://github.com/neovim/neovim/blob/master/INSTALL.md#linux)中确认当前发布包名称。以下以 x86-64 tar 包为例：

```bash
mkdir -p ~/.local/opt ~/.local/bin
curl -fLo /tmp/nvim-linux-x86_64.tar.gz \
  https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
tar -xzf /tmp/nvim-linux-x86_64.tar.gz -C ~/.local/opt
ln -sfn ~/.local/opt/nvim-linux-x86_64/bin/nvim ~/.local/bin/nvim
```

确保 `~/.local/bin` 在 `PATH` 中；Ubuntu 默认 Bash 可将下面一行加入 `~/.bashrc`，然后重新打开终端：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

确认实际运行的是新版本：

```bash
command -v nvim
nvim --version | head -n 2
```

如果电脑是 ARM64，请从官方安装说明选择对应的 `arm64` 包。

> 💡 若下载到的是 **Neovim AppImage**，在 FUSE 不可用的机器上同样需要按上面第 4 步的 `--appimage-extract` 方式解压后运行，否则 `nvim` 命令会直接报 FUSE 挂载错误。

### 3. 安装 Nerd Font（推荐）

Nerd Font 用于显示状态栏、文件树和启动页图标。下载 Meslo Nerd Font 压缩包并安装到当前用户：

```bash
mkdir -p ~/.local/share/fonts/Meslo
curl -fLo /tmp/Meslo.zip \
  https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.zip
unzip -o /tmp/Meslo.zip -d ~/.local/share/fonts/Meslo
fc-cache -f
```

在终端设置中选择 **MesloLGS Nerd Font Mono**。如果终端图标缺失，先检查所选字体和 `fc-cache`，再重启终端。

### 4.（可选）安装 Neovide

Neovide 是独立的图形界面，不是使用本配置的必需项。Ubuntu/Linux 可在 [Neovide Releases](https://github.com/neovide/neovide/releases) 下载 AppImage 或压缩包，安装后运行 `neovide` 即可。

> ⚠️ **务必先确认 FUSE 可用**。AppImage 依赖 FUSE 挂载，若系统缺少 `/dev/fuse`（内核未加载 `fuse` 模块，或处于容器/受限环境中），直接执行 AppImage 会报 `Cannot mount AppImage, please check your FUSE setup`。检查与修复：
>
> ```bash
> ls /dev/fuse                    # 无输出说明 FUSE 不可用
> sudo modprobe fuse              # 尝试加载内核模块
> sudo apt install -y libfuse2    # AppImage 需要 FUSE 2 兼容层
> ```
>
> 如果加载模块后仍无 `/dev/fuse`（常见于容器或精简内核），可以改用**免 FUSE 的解压方式**运行：
>
> ```bash
> mkdir -p ~/Applications/neovide && cd ~/Applications/neovide
> cp ~/Downloads/neovide.AppImage .
> chmod +x neovide.AppImage
> ./neovide.AppImage --appimage-extract     # 解压出 squashfs-root/
> ~/Applications/neovide/squashfs-root/usr/bin/neovide --version
> ```
>
> 确认可用后软链到 `~/.local/bin`：
>
> ```bash
> ln -sf ~/Applications/neovide/squashfs-root/usr/bin/neovide ~/.local/bin/neovide
> ```
>
> 如需在应用菜单里搜索启动，可再创建一个桌面入口：
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
> 这个 `--appimage-extract` 技巧对**任何** AppImage 都适用（例如 Neovim 官方 AppImage、其他 GUI 工具），是 FUSE 不可用时的通用兜底方案。

Neovide 专用快捷键使用 macOS 的 Command 键映射（`<D-s>` 等），在 Ubuntu 下这些映射不会生效，请改用下文的通用快捷键（如 `<leader>ww` 保存）。

如果 Neovide 启动时报 `Failed to create OpenGL context`，说明显卡驱动或 GL 环境有问题，可先用软件渲染验证：

```bash
LIBGL_ALWAYS_SOFTWARE=1 neovide
```

### 5. 获取 Ubuntu 配置并一键部署

```bash
git clone --branch forUbuntu https://github.com/dumbo1985/dotfiles.git ~/dotfiles
~/dotfiles/install.sh
```

`install.sh` 是幂等的，重复执行安全，它会把仓库里的所有配置接线到位：

- 软链 `~/.config/nvim → ~/dotfiles/nvim`（已有真实目录会备份为 `*.pre-dotfiles.bak`）
- 软链 `~/.config/clangd/config.yaml`（未编译项目也能跳转 Qt 等公共库，见[仓库内的其他配置](structure.md)）
- 软链 `~/.blerc`（ble.sh + fzf 集成；未装 ble.sh 时无影响）
- 向 `~/.bashrc` 追加标记块，source `bash/jump.sh`（`workspace` / `dengprojects` 快速跳转命令）
- 复制 `wallpaper/` 下的每日壁纸脚本到 `~/.local/bin` 并自动选择调度方式

不想要壁纸功能的机器执行 `~/dotfiles/install.sh --skip-wallpaper`。

<details>
<summary>手动方式（与脚本等价，适合只想链接 nvim 的机器）</summary>

```bash
mkdir -p ~/.config
if [ -e ~/.config/nvim ] && [ ! -L ~/.config/nvim ]; then
  mv ~/.config/nvim ~/.config/nvim.backup
fi
ln -sfn ~/dotfiles/nvim ~/.config/nvim
```

如果已经克隆过仓库，进入 `~/dotfiles` 后运行 `git switch forUbuntu`，再执行链接命令即可。已有的真实配置目录会先备份为 `~/.config/nvim.backup`。

</details>

### 6. 首次启动

```bash
nvim
```

首次启动会通过 `lazy.nvim` 下载插件；Mason 随后会安装配置列表中的 LSP 和开发工具。安装完成后重启 Neovim。可在 Neovim 中运行 `:Lazy` 查看插件状态、`:Mason` 查看工具状态、`:LspInfo` 查看当前文件的 LSP 状态。

C/C++ 项目建议生成 `compile_commands.json`，因为 clangd 配置会查找项目 `build/` 目录：

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

### 7.（可选）启用中文输入法

Ubuntu 使用桌面输入法，Neovim 会自动跟随系统当前输入法，不需要额外插件。若使用 Fcitx5/Rime，可安装：

```bash
sudo apt install fcitx5 fcitx5-rime fcitx5-config-qt im-config
im-config -n fcitx5
```

注销并重新登录后，打开 Fcitx 5 配置工具并添加 Rime。另外建议安装剪贴板支持（若第 1 步未装）：

```bash
sudo apt install -y wl-clipboard xclip    # Wayland / X11 剪贴板
```

> 💡 macOS 上依靠 `im-select` 在离开插入模式时自动切回英文的能力**未在 `forUbuntu` 分支启用**，如需该功能请使用 `main` 分支或自行移植。Ubuntu 下可在 Fcitx5 中设置「中英文切换」快捷键（如 `Ctrl+Space`）来手动切换。

### 8.（可选）一键安装命令行工具箱

```bash
bash ~/dotfiles/toolbox/ubuntu24-cli-toolbox.sh       # apt 官方源内：eza/bat/fd/zoxide/tmux/tig/direnv/fzf 等
bash ~/dotfiles/toolbox/install-extra-cli-tools.sh --dry-run  # 官方源外：lazygit/dust/procs/fastfetch/zellij 等（先预览）
```

第一个脚本会按功能分组安装现代 CLI 工具，并往 `~/.bashrc` 追加带 `>>> cli-toolbox >>>` 标记的配置块（ls/ll 别名、zoxide/direnv/thefuck 集成、fzf 快捷键、彩色手册页），重复执行不会重复写入。第二个脚本从各项目 GitHub Releases 下载预编译二进制（版本号运行时动态获取），支持 `--dry-run` 预览、指定工具名安装、`--force` 重装。两者都需要 sudo / 网络，因此不由 `install.sh` 代跑。

