# Ubuntu 24.04 上的 Hyprland

本配置针对 Ubuntu 24.04 amd64、GDM、Hyprland **0.57**，使用新的 Lua 配置格式。
支持 20 套协调配色与登录随机，带渐变边框、圆角、柔和阴影和窗口动画，搭配悬浮 Waybar、自动隐藏 Dock 与支持应用、文件搜索和计算的统一启动器。
保留 Neovide 自身的 `0.8` 不透明度，合成器不叠加全局窗口透明度。

第一次使用请先看 [中文新手教程：使用逻辑、快捷键与常见问题](BEGINNER.zh-CN.md)。

## 安装

软件来自 [cppiber/hyprland 第三方 PPA](https://launchpad.net/~cppiber/+archive/ubuntu/hyprland)，
不是 Ubuntu 或 Hyprland 官方维护的软件源。安装器核验签名指纹，并限制可从该源安装的软件包。
在本机预检中，完整依赖可以解算、无需卸载软件；会更新 PipeWire、libinput、libxkbcommon 等共享库。
这些库也由 GNOME 使用，选择 Ubuntu 会话并不会撤销软件包升级。

```bash
bash ~/dotfiles/hyprland/install.sh --check
bash ~/dotfiles/hyprland/install.sh --install
```

在自己的终端输入 sudo 密码，不要将密码发送到聊天。安装器不会修改 GDM、显卡驱动或注销当前会话。
安装前的软件包版本及安装计划保存在 `~/.local/state/dotfiles-hyprland/`，这只是记录，不是系统快照。
APT 会拒绝需要卸载现有软件的安装方案。脚本固定 Hyprland `0.57.0-1ppa2`；若该版本不再提供，
需重新核对版本和配置，不要盲目删掉版本限制。

只部署用户配置：

```bash
bash ~/dotfiles/hyprland/install.sh --configure
```

配置通过 `~/.config/hypr` 软链到本目录的 `config/`。
已有配置会先移动到上述状态目录中保存；安装后自动运行 `Hyprland --verify-config`。
基本安装器只部署 Hyprland；本机另已应用下述桌面套件，会修改用户 GTK/Qt 外观设置，并保留配置备份。Neovim 原有主题配置保持不变。

## 首次登录

保存工作后自行注销；在 GDM 中选中用户，点击齿轮选择 **Hyprland** 再登录。
状态栏、Dock、SwayNC 通知中心、桌面面板后台、剪贴板、Fcitx5、网络托盘、权限认证代理、壁纸和空闲锁屏会随会话启动。Mako 保留配置但不再运行。
Waybar、Mako、Hypridle 的 systemd 用户服务会被屏蔽，改由 Hyprland 启动钩子运行，
避免它们的系统级默认启用设置影响 GNOME；手动运行这些程序仍然正常。
壁纸使用本配置自带的 4K 光环图案，按显示器方向自动选择横屏或竖屏版本；与 GNOME 每日壁纸独立。
终端优先使用已有的 WezTerm（包括 Flatpak 版），找不到则使用 Kitty。
屏幕共享使用 Hyprland portal；文件选择使用 GTK portal。

| 快捷键 | 功能 |
| --- | --- |
| Super + Enter | 终端 |
| Super + Space | 统一启动器：应用、文件搜索、计算；再按关闭 |
| Super + Shift + Space | 原 Wofi 应用菜单 |
| Super + N | Neovide |
| Super + E | 文件管理器 |
| Super + B | 默认浏览器 |
| Super + Q | 关闭窗口 |
| Super + V | 切换浮动 |
| Super + F | 全屏 |
| Super + Shift + F | 最大化 |
| Super + 方向键 | 窗口焦点 |
| Super + 数字 | 切换工作区 |
| Super + O | 工作区缩略总览 |
| Super + Tab / Super + 反引号 | 切换应用 / 同应用窗口；Shift 反向 |
| Super + Shift + O / Super + Ctrl + O | 框选识字 / 代码识字 |
| Super + Shift + 数字 | 移动窗口到工作区 |
| Super + 鼠标左/右键拖动 | 移动/缩放窗口 |
| Print | 区域截图并复制 |
| Super + L | 锁屏 |
| Super + Shift + E | 注销（先保存工作） |

Neovide 原有 F11 继续交给 Neovide 处理。
五分钟空闲后锁屏；没有配置自动休眠或关机。

## 统一启动器：搜索与快捷操作

按 `Super + Space` 后直接输入内容，无需切换模式：输入 `Chrome` 查找应用，输入文件名搜索主目录中的普通文件，输入 `12*34`、`(100+20)/3` 或 `2^10` 实时显示计算结果。
普通搜索同时列出应用与文件，应用排在文件前；识别到算式时，计算结果优先显示。
默认跳过隐藏目录、缓存与依赖目录；已知文件位置时，也可以直接输入绝对路径或 `~/` 开头的路径。

方向键选择结果，Enter 启动应用或用默认程序打开文件；选中计算结果后 Enter 复制到剪贴板。
选中文件后按 `Ctrl + Enter` 打开其所在文件夹。Esc 或再次按 `Super + Space` 关闭启动器。

输入 `?` 查看更多功能。以下前缀与后面的内容之间留一个空格：

| 输入示例 | 功能 |
| --- | --- |
| `w neovide` | 按应用或标题搜索已打开的窗口，Enter 切换 |
| `v 关键词` | 搜索剪贴板历史，Enter 复制选中项 |
| `g Hyprland 教程` | 用浏览器搜索 Google |
| `github.com` | 直接在默认浏览器打开网址 |
| `dict hypothetical` | 联网查音标、释义与例句，Enter 复制选中的内容 |
| `10 km to mile`、`32 f to c` | 单位换算，Enter 复制结果 |
| `p dotfiles` | 搜索项目，用 Neovide 打开 |
| `t workspace` | 在终端连接或创建 tmux 会话，已有会话不会重复创建 |
| `s 日期` | 搜索文字片段，Enter 复制 |
| `锁屏`、`截图`、`切换主题` | 选择相应桌面操作后 Enter 执行 |

词典结果缓存 30 天；联网中文词典不可用时会尝试英文词典。单位换算支持长度、温度、容量、速度等；`GB` 按十进制、`GiB` 按二进制，`b` 表示位、`B` 表示字节。
文字片段在 `~/.config/hypr/launcher-snippets.json` 编辑，支持 `{{date}}`、`{{time}}`、`{{datetime}}`、`{{year}}` 占位符。邮箱片段默认读取本机 Git 邮箱，也可以在配置中填写自己的地址。
项目搜索使用默认项目目录；可创建 `~/.config/hypr/launcher-projects.json`，用 `{"roots": ["~/dotfiles", "~/Projects"]}` 指定搜索目录。

`bin/launcher` 是快捷键入口，`lib/launcher_ui.py` 绘制随当前主题变化的界面，`lib/launcher_features.py` 分发查询与帮助入口，`lib/launcher_search.py` 负责应用、文件搜索与计算；`lib/launcher_context.py` 和 `lib/launcher_knowledge.py` 提供窗口、剪贴板、项目等快捷功能及查词、换算。
需要原应用菜单时按 `Super + Shift + Space`，也可在终端运行：

```bash
wofi --show drun --conf ~/.config/hypr/wofi.conf --style ~/.config/hypr/wofi.css
```

## 快速预览与窗口布局记忆

文件管理器选中文件后按空格预览；启动器选中文件后按 `Alt + P` 预览。
`Super + Tab` 切应用，`Super + 反引号` 切同一应用的窗口；加 Shift 反向。
`Super + Shift + O` 框选中英文识字，`Super + Ctrl + O` 使用代码模式。
后台自动记住应用的显示器与工作区，浮动窗口也记住位置和大小。
完整说明见 [四项桌面工作流](MACOS.zh-CN.md)。

## 主题与壁纸

窗口、状态栏、菜单、通知与锁屏跟随当前主题。按 `Super + Shift + T` 从 Tokyo Night、Catppuccin、Nord、Gruvbox、Rosé Pine、Dracula、One Dark、Kanagawa 等 20 套配色中选择；默认每次登录随机且避开上次，配置重载不随机。
GTK3/4、Qt5/6 与 WezTerm 也跟随主题，配合 Papirus-Dark 图标，字体为 Noto Sans CJK SC 11。已打开的应用需要重启才完整更新，Flatpak 和自行绘制界面的应用可能仍使用自己的主题。
字体区域保持高对比度，不对所有应用叠加透明度。当前双屏保持 125% 缩放，右侧 DP-2 为竖屏。
两块显示器均使用 4K 75Hz；若线材或显示器出现闪屏，可将主配置中的两处 `@75` 改回 `@60`，运行 `hyprctl reload`。

### 动画与鼠标

窗口开关使用轻微缩放，窗口移动、拖动与调整分屏尺寸使用平滑过渡。
`Super + 数字` 或点击状态栏工作区时，随机选择横向推移、纵向电梯或缩略总览放大进入，避免连续两次重复同一种效果。
横向/纵向推移约 0.45 秒柔和减速，页间留 36 个逻辑像素；缩略动画约 0.65 秒，使用后台预先缓存的画面，不在按键时等待截图。
菜单轻微缩放，通知与控制面板从右侧滑入。
若目标工作区已经显示在另一块屏幕，数字快捷键只切换屏幕焦点，不触发工作区推移动画。
未聚焦窗口降低 8% 亮度，焦点边框柔和切换；活动窗口的蓝紫渐变边框缓慢循环。
持续循环边框会持续产生重绘，若更重视低功耗，将 `borderangle` 动画的 `enabled` 改为 `false`。

### 工作区应用提示与总览

状态栏显示 `1 Chrome`、`2 ChatGPT`、`9 Neovide` 等应用简称，多个同类窗口去重；
最多显示两个不同应用名，更多以 `+n` 表示。悬停查看全部窗口的应用和标题，约两秒刷新。
状态栏在两块屏幕显示会话的 1–10 工作区；当前焦点渐变高亮，另一屏幕可见工作区显示青色。
右侧分别显示有线 `enp6s0` 和无线 `wlp7s0`，同时连接时两者都会出现；
Wi-Fi 显示当前网络名，悬停可查看信号和 IP。点击任一个入口都可打开网络连接编辑器。

`Super + O` 随时打开独立的工作区总览：点击卡片或按数字进入，方向键选择后按 Enter，Esc 返回。
横屏四列、竖屏两列；`0` 对应工作区 10。总览使用访问过的工作区最近画面，
尚未缓存的工作区显示真实窗口位置和标题，并标记“预览未缓存”，不是实时视频。
预览只保存在当前用户的 `/run/user/<uid>/hypr-workspaces-*/previews/`，服务退出后清理。
没有使用尚未适配 0.57 的 Hyprspace/hyprexpo 插件；现有鼠标插件保持独立。

`bin/workspace-switch` 管理随机动画和总览服务，`lib/overview_ui.py` 绘制总览，
`bin/workspace-labels` 生成状态栏应用提示。总览运行需要 Python GI、Cairo、GTK3 和 GtkLayerShell；
本机缺失的 GI typelib/桥接已放在 `~/.local/share/hypr-motion/gtk-layer/`、`gtk-cairo/`，没有升级系统软件包。
服务错误日志在 `~/.local/state/dotfiles-hyprland/workspace-overview.log`。
若总览服务启动失败，数字切换会回退到原生滑动，避免影响正常窗口访问。

手动只使用某一种效果：

```bash
~/.config/hypr/bin/workspace-switch 2 --mode horizontal
~/.config/hypr/bin/workspace-switch 2 --mode vertical
~/.config/hypr/bin/workspace-switch 2 --mode overview
```

指针采用 [Rosé Pine Hyprcursor](https://github.com/ndom91/rose-pine-hyprcursor)（28px），
X11 使用 [BreezeX Rosé Pine](https://github.com/rose-pine/cursors) 回退。
这两个主题安装在 `~/.local/share/icons/`，仅复制本配置到另一台机器时，还需要安装这些指针资源。

本机已编译并启用 [hypr-dynamic-cursors](https://github.com/VirtCode/hypr-dynamic-cursors)：
快速移动时指针轻微拉伸，快速来回摇动时放大至 2–3 倍，停止后约 0.9 秒恢复。
文字插入与十字指针保持原形；客户端自行绘制的指针可能与主题指针表现不同。
插件二进制和构建记录位于 `~/.local/share/hypr-motion/`，源码、独立构建依赖和日志位于
`~/.cache/hypr-motion/`，没有为此安装系统软件包。
启动及重新应用主题时，`bin/cursor-effects` 核对完整 ABI 后再加载插件。
升级 Hyprland 或相关 ABI 后会跳过旧插件，需要重新构建；不要强制加载旧二进制。

按 `Super + Shift + C` 打开鼠标设置，可以选择 16 套外观、拉伸/倾斜/旋转、摇动放大和尺寸。
选择保存在 `~/.local/state/dotfiles-hyprland/cursor.json`，重新登录和换桌面配色均会保留。
详细操作见 [鼠标外观与运动效果](CURSORS.zh-CN.md)。
资源可用 `python3 tools/install-cursor-themes.py` 在用户目录安装。
本轮优化前的完整配置备份位于
`~/.local/state/dotfiles-hyprland/before-motion-20261029-145936/config/`。

修改外观后，无需注销即可重新应用：

```bash
~/.config/hypr/bin/apply-theme
```

它会检查配置、只重载外观配置，并重新启动状态栏、壁纸和总览服务，刷新通知样式。
壁纸原图及 PNG 位于 `config/wallpapers/`；重新生成可运行
`python3 ~/dotfiles/hyprland/tools/generate-wallpapers.py`（需要 Python Pillow、GI 和 GdkPixbuf）。

本次美化前的配置备份位于
`~/.local/state/dotfiles-hyprland/before-tokyo-night-20261029-135517/config/`。
需要恢复时，将其中的配置文件复制回 `~/dotfiles/hyprland/config/`，再运行上述重新应用命令；
这份旧备份没有 `bin/apply-theme`，不要用带删除选项的同步命令覆盖。

## 桌面套件

主题切换与登录随机见 [20 套主题教程](THEMES.zh-CN.md)。天气已设北京，顶栏左键天气可修改城市。Dock 触底显示，移开后自动隐藏。

完整入口、截图标注、壁纸、音乐频谱、场景和恢复说明见 [桌面套件使用附录](DESKTOP-SUITE.zh-CN.md)。
本机套件程序安装在 `~/.local/share/hypr-theme/`，GTK 主题在 `~/.local/share/themes/Tokyonight-Dark/`，
没有通过 sudo 安装本轮依赖。只复制仓库到新机器时，基本安装器不会自动准备这些用户资源，需额外部署。

## NVIDIA 与验证

本机是 RTX 5070 + AMD 双显卡，检测到 NVIDIA 驱动 595.99.02。
配置不强制 GPU 顺序，也不套用旧版 NVIDIA 的 `WLR_NO_HARDWARE_CURSORS` 等环境变量。
首次登录后核对多显示器、输入法、锁屏、飞书/浏览器屏幕共享以及 Neovide F11 透明效果。
依赖模拟与配置语法验证不能替代实际会话验证。

```bash
Hyprland --verify-config --config ~/.config/hypr/hyprland.lua
hyprctl configerrors
hyprctl monitors
systemctl --user status xdg-desktop-portal xdg-desktop-portal-hyprland
```

如果会话启动失败，可以回到登录界面选择 **Ubuntu**。必要时用 Ctrl+Alt+F3 进入 TTY 登录，
检查 `journalctl --user -b` 和 Hyprland 日志。返回图形界面的功能键依当前 VT 而定。

## 返回 GNOME 与卸载

注销 Hyprland，在登录界面选择 Ubuntu。GNOME 会话仍可使用；GTK 图标、字体和颜色偏好是用户共享设置，恢复方法见桌面套件附录。
如不再使用，可删除 `~/.config/hypr` 软链，再按需恢复状态目录中的旧配置。
如以后希望通过 systemd 管理这三个组件，可执行
`systemctl --user unmask waybar.service mako.service hypridle.service`；保留 GNOME 时不必取消屏蔽。
删除 PPA 源文件不会降级已升级的共享库；若需要完整撤销软件包变更，应根据安装前版本记录评估
`ppa-purge` 或恢复系统快照，不能仅删除源后执行 `apt autoremove`。

参考：[Hyprland 配置](https://wiki.hypr.land/configuring/)、
[PPA 构建源](https://github.com/cpiber/hyprland-ppa)。
