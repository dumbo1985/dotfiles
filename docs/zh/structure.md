[← 返回 README](../../README.zh-CN.md)

## 📁 配置结构

```
.
├── install.sh                  # 一键部署脚本（软链 nvim/clangd/blerc、追加 bashrc、部署壁纸）
├── nvim/                       # Neovim 配置（软链到 ~/.config/nvim）
│   ├── init.lua                # 入口文件
│   ├── lazy-lock.json          # 插件版本锁定文件（回滚快照）
│   └── lua/dengbo/
│       ├── core/               # 核心配置（选项、键位、折叠、Neovide 等）
│       ├── platform/           # 平台相关模块（macOS 输入法实现，备用）
│       ├── lazy.lua            # 插件管理和主题加载
│       └── plugins/            # 插件配置（lsp/、telescope、treesitter、dap、formatting …）
├── bash/
│   └── jump.sh                 # 终端快速跳转命令（workspace / dengprojects）
├── ble/
│   └── blerc                   # ble.sh + fzf 集成（软链到 ~/.blerc）
├── clangd/
│   └── config.yaml             # 用户级 clangd 兜底配置（Qt6 公共库路径）
├── toolbox/                    # 命令行工具箱（需 sudo，手动运行，不由 install.sh 代跑）
│   ├── ubuntu24-cli-toolbox.sh # apt 官方源内现代 CLI 一键安装 + bashrc 别名块
│   └── install-extra-cli-tools.sh # 官方源外工具（GitHub Releases 预编译）
└── wallpaper/                  # 每日壁纸（GNOME/gsettings，与 nvim 无关，可跳过）
    ├── bin/                    # daily-wallpaper / install-daily-wallpaper / wallpaper-doctor
    └── systemd/                # daily-wallpaper.service / .timer
```

## 🧩 仓库内的其他配置

除 Neovim 外，仓库还管理三块"新机器上容易丢"的配置，均由 `install.sh` 自动接线：

- **终端快速跳转（`bash/jump.sh`）**：`workspace`、`dengprojects` 两个命令，任意位置敲命令名即进入对应目录，可带子目录参数直达，Tab 补全实时扫描目录。想加新目录，在 `jump.sh` 里仿照添加一行 `_def_jump 名字 "$HOME/某路径"` 即可。
- **ble.sh + fzf 集成（`ble/blerc`）**：保留 ble.sh 默认的 MULTILINE 行为（多行时 RET 插入换行、`C-j` 执行）。ble.sh 本体需另行安装（`git clone --recursive https://github.com/akinomyoga/ble.sh && make -C ble.sh install PREFIX=~/.local`，并在 `~/.bashrc` 里 source），没装它时此文件不生效。
- **clangd 公共库兜底（`clangd/config.yaml`）**：项目没跑过 CMake configure、没有 `compile_commands.json` 时，clangd 退化成裸 clang 会满屏报 Qt 头文件错误。该文件把 Ubuntu 24.04 apt 安装的 Qt6 头文件路径补进 `-isystem`，让"clone 下来直接看代码"也能正常跳转、不报错。项目有编译数据库时不冲突（`Add` 是追加，重复路径无害）。装了其他公共库（OpenCV/Eigen 等）要加路径时，用 `pkg-config --cflags <库名>` 判断（输出 `-I` 且不在默认搜索路径就要加），见文件内注释。
- **每日壁纸（`wallpaper/`）**：每天定时从 picsum 下载一张壁纸并自动清理旧图（默认只保留当前一张）。依赖 GNOME/gsettings；`install.sh` 部署脚本后由 `install-daily-wallpaper` 自动选路——systemd user timer 可用则用 timer，否则退到登录自启动并打印 cron 方案。管理命令：`install-daily-wallpaper status / now / uninstall`。
- **命令行工具箱（`toolbox/`）**：两个独立的安装脚本，见安装步骤第 8 步。仓库只保存脚本本身；本机的 `>>> cli-toolbox >>>` bashrc 块由脚本生成，不归 dotfiles 管理（与 `dotfiles:jump` 块互不干扰）。

