# 20 套主题与登录随机

这套 Hyprland 配置可以在 20 套配色之间切换。先按 `Super + Shift + T` 打开主题菜单，输入中文或英文名称筛选，用方向键选择、`Enter` 应用，`Esc` 取消。随机换色和登录随机开关固定在列表顶部。也可以运行：

```bash
~/.config/hypr/bin/theme-picker
```

主题沿用现在的平铺、工作区、面板和窗口操作逻辑。`Super + 数字` 切工作区、`Super + Q` 关闭窗口等快捷键继续按原来的方式使用。

## 20 套主题怎么选

| 主题 | 命令中的 ID | 主要观感 |
| --- | --- | --- |
| Tokyo Night · 东京夜景 | `tokyo-night` | 蓝紫霓虹，当前桌面的原始配色 |
| Catppuccin Mocha · 奶咖 | `catppuccin-mocha` | 柔和奶紫与粉彩，圆润温暖 |
| Nord · 北欧极夜 | `nord` | 冷灰底色与冰蓝强调，清爽克制 |
| Gruvbox · 复古暖棕 | `gruvbox` | 暖棕、金黄与橄榄绿，复古终端气质 |
| Rosé Pine · 玫瑰松 | `rose-pine` | 深紫底色、玫瑰粉与雾蓝，安静柔和 |
| Dracula · 德古拉 | `dracula` | 经典紫灰底色，搭配鲜明粉紫与薄荷绿 |
| One Dark · 原子深空 | `one-dark` | Atom 经典冷灰，柔和蓝绿与暖橙 |
| Everforest · 常青森林 | `everforest` | 森林绿灰与柔和暖色，采用中等深色底 |
| Kanagawa · 神奈川之浪 | `kanagawa` | 墨色夜海、和纸暖白与低饱和蓝紫 |
| Monokai Pro · 暖灰霓彩 | `monokai-pro` | 暖灰背景与 Monokai Pro 的六色强调 |
| Solarized Dark · 日光深色 | `solarized-dark` | 经典蓝绿墨底，精简色阶与黄铜强调 |
| Ayu Mirage · 海市蜃楼 | `ayu-mirage` | 深蓝灰与明亮琥珀，清透的 Ayu Mirage |
| Material Ocean · 深海材质 | `material-ocean` | Material Deep Ocean 墨蓝与粉彩强调 |
| Nightfox · 夜狐 | `nightfox` | 深海军蓝、柔白文字与温暖的果色 |
| Carbonfox · 碳狐 | `carbonfox` | Carbon 风格炭黑，冰蓝、洋红与青绿 |
| Oxocarbon · 氧化碳 | `oxocarbon` | IBM Carbon 系黑白层次，亮蓝与玫红 |
| Sonokai · 索诺凯 | `sonokai` | 清晰石墨灰与鲜亮果色，采用默认变体 |
| GitHub Dark · 代码夜色 | `github-dark` | GitHub 经典深色，冷黑底与清晰蓝色 |
| Synthwave '84 · 合成波八四 | `synthwave-84` | 八十年代霓虹紫、荧光粉与电光青 |
| Catppuccin Macchiato · 玛奇朵 | `catppuccin-macchiato` | 比 Mocha 更明亮的蓝紫底与柔和奶彩 |

这些名称表示本配置对相应色板的适配，部分小字和选中文字做了对比度调整。GTK 应用主题基于现有主题结构调整颜色；窗口装饰和控件布局仍沿用当前结构。每套主题没有安装另一份第三方整套 dotfiles。

配色会协调顶栏、Dock、菜单、通知、桌面面板、音量提示、工作区总览、窗口边框与阴影、锁屏和音乐频谱；GTK3/4、Qt5/6、WezTerm、Bash 提示符和壁纸也会使用对应色板。字体、布局、显示器的 125% 缩放保持原有设置，Neovim 继续使用自己的主题机制。

## 立即换成指定主题

例如切换到 Nord：

```bash
~/.config/hypr/bin/theme-switch nord
```

其他主题也使用表格中的 ID：

```bash
~/.config/hypr/bin/theme-switch tokyo-night
~/.config/hypr/bin/theme-switch catppuccin-mocha
~/.config/hypr/bin/theme-switch gruvbox
~/.config/hypr/bin/theme-switch rose-pine
```

桌面组件会刷新配色。已经打开的应用可能需要关闭后重新打开，才能完整读取新的应用主题，尤其是 GTK4 应用；Flatpak 沙箱、自绘界面和应用内单独指定的主题可能保留各自的外观。

## 随机一次与登录随机

当前默认开启登录随机。可以保留每次登录换一种配色，也可以按下面的方法关闭并固定喜欢的主题。

立即随机换一套主题：

```bash
~/.config/hypr/bin/theme-switch random
```

开启每次登录随机：

```bash
~/.config/hypr/bin/theme-switch auto on
```

开启后，下一次进入新的 Hyprland 会话会随机选择主题，并避开上一次使用的主题。普通配置重载，以及重新应用当前外观，都不会再次抽取主题，所以调整配置时桌面不会反复变色。

关闭登录随机：

```bash
~/.config/hypr/bin/theme-switch auto off
```

手动选中一套主题不会自动关闭登录随机。如果希望以后一直使用 Nord，依次执行：

```bash
~/.config/hypr/bin/theme-switch auto off
~/.config/hypr/bin/theme-switch nord
```

查看当前主题和登录随机是否开启：

```bash
~/.config/hypr/bin/theme-switch status
```

主题选择记录在 `~/.local/state/dotfiles-hyprland/theme.json`：`name` 是当前主题 ID，`random_on_login` 是登录随机开关。日常使用菜单和上述命令即可修改，无需手工编辑状态文件。

## 主题和日夜场景的区别

主题负责桌面配色；控制中心的“日间、夜间、专注”负责色温、非活动窗口亮度和勿扰状态。觉得整块屏幕偏黄时，先检查是否处于夜间场景；换主题本身不等于关闭暖色滤镜。

工作区切换的三种随机动画与登录随机主题分别控制。随机主题改变配色，不改变切工作区时的按键操作。

## 部分应用没有变色时

先用 `theme-switch status` 确认当前主题，再关闭并重新打开对应应用。终端中已经运行的 Bash 也可能继续保留旧提示符，新开终端即可读取更新后的配置。

如果顶栏或面板需要重新加载，运行：

```bash
~/.config/hypr/bin/apply-theme
```

该操作重新应用当前外观，不结束 Hyprland 会话，也不会触发一次新的登录随机。需要回到最初的蓝紫配色时，运行 `theme-switch tokyo-night`；若还希望下次登录保持它，先关闭登录随机。

## 想自己修改配色

`~/.config/hypr/themes/templates/` 保留 Tokyo Night 原始模板，主题切换工具根据这些模板生成顶栏、Dock、菜单、通知、电源菜单、锁屏、频谱和 Bash 配色文件。切换主题时会重新生成这些文件，直接修改生成后的 CSS 可能在下次切换时被覆盖。

需要长期调整间距、圆角或字体时，应修改对应模板，再重新应用主题。模板中的原始颜色也是换色工具识别颜色用途的依据；改动色值前先查看主题生成逻辑，避免出现某些区域没有跟随换色的情况。

GTK 配色资源可从本机已安装的 Tokyo Night GTK 基底生成：

```bash
python3 ~/dotfiles/hyprland/tools/build-gtk-themes.py --missing-only
```

`--missing-only` 跳过配色、生成器版本和样式文件都未变的资源。

基础安装器只部署基础 Hyprland 配置。把仓库迁移到新电脑时，还需要准备本机使用的 GTK 主题、图标和用户目录程序；资源与备份说明见 [桌面套件附录](DESKTOP-SUITE.zh-CN.md)。
