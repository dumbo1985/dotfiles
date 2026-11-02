# 鼠标外观与运动效果

按 `Super + Shift + C` 打开鼠标设置。也可以按 `Super + Space`，搜索“鼠标”进入，或运行：

```bash
~/.config/hypr/bin/cursor-picker
```

菜单分为外观、运动效果、摇动放大、尺寸和恢复默认。方向键选择，`Enter` 应用，`Esc` 取消；当前选项会标记出来。

## 先选外观，再选运动

**外观**改变箭头、链接手形、输入光标等指针图案和配色。菜单只提供本机已经安装、能够使用的主题。桌面主题和鼠标主题各自保存，换桌面配色时可以继续使用喜欢的指针。

本机已准备 16 套外观：

| 系列 | 可选外观 |
| --- | --- |
| Rosé Pine | 玫瑰松，当前默认 |
| Bibata Modern | 经典黑、冰白、琥珀 |
| Capitaine | 舰长深色、舰长浅色 |
| Catppuccin Mocha | 奶咖紫、薰衣草 |
| Nordzy | 北欧深色、北欧浅色 |
| Volantes | 飞羽深色、飞羽浅色 |
| 系统经典 | Adwaita、Yaru、DMZ White、DMZ Black |

喜欢圆润轮廓可以先试 Bibata，想接近 macOS 可以试 Capitaine；希望摇动放大时仍细腻，可选 Rosé Pine、Catppuccin 或 Nordzy 的原生 Hyprcursor 外观。

**运动效果**改变移动指针时的形状：

| 选项 | 效果 |
| --- | --- |
| 拉伸 `stretch` | 随移动方向轻微拉长，停下后恢复 |
| 倾斜 `tilt` | 移动时向左右侧倾 |
| 旋转 `rotate` | 随移动方向转动，像拖着箭头移动 |
| 关闭运动 `none` | 保持原来的朝向和形状 |

可以先试拉伸，再试倾斜；旋转更明显，长时间使用是否舒服取决于个人习惯。输入文字和精确定位时，文字光标与十字指针保留稳定形状。

## 摇动放大和尺寸

找不到鼠标时，快速左右摇动会暂时放大指针，停止后恢复。这个开关与运动效果独立：选择“关闭运动”后，仍可保留摇动放大；如果希望鼠标完全静止不变形，再把摇动放大关闭。

**尺寸**菜单提供 24、28、32、36 px。当前两块屏幕使用 125% 缩放，可以从 28 px 开始尝试，觉得不够明显再选 32 或 36 px。这里调整的是基础尺寸，摇动时会在此基础上暂时放大。

**恢复默认**会一起恢复 Rosé Pine 外观、拉伸效果、开启摇动放大和 28 px 尺寸。菜单中该操作有单独确认项，退出确认菜单即可取消。

## 命令行设置

查看当前设置及可用主题：

```bash
~/.config/hypr/bin/cursor-switch status
~/.config/hypr/bin/cursor-switch list
```

换外观时，使用 `list` 显示的主题 ID：

```bash
~/.config/hypr/bin/cursor-switch theme <主题ID>
```

例如换成冰白 Bibata，或回到玫瑰松：

```bash
~/.config/hypr/bin/cursor-switch theme bibata-ice
~/.config/hypr/bin/cursor-switch theme rose-pine
```

例如切换运动、大小或摇动放大：

```bash
~/.config/hypr/bin/cursor-switch mode tilt
~/.config/hypr/bin/cursor-switch size 32
~/.config/hypr/bin/cursor-switch shake on
```

只关闭运动变形：

```bash
~/.config/hypr/bin/cursor-switch mode none
```

关闭摇动放大：

```bash
~/.config/hypr/bin/cursor-switch shake off
```

恢复默认：

```bash
~/.config/hypr/bin/cursor-switch reset
```

菜单和命令会保存选择，重新登录后继续使用。记录位于 `~/.local/state/dotfiles-hyprland/cursor.json`；日常使用菜单即可，无需手工编辑它。

## 某些窗口里的鼠标没有变化

Ubuntu 的 libXcursor 默认只搜索旧路径 `~/.icons`，本套件的资源安装在 `~/.local/share/icons`。
切换器会安全建立兼容链接、设置 `XCURSOR_PATH`，并强制刷新主题缓存，避免选择新外观后静默回退系统默认。
不会覆盖原有的 `~/.icons` 内容；不要删除这个兼容入口。

鼠标设置会同步 Hyprland、GTK 和后续启动应用使用的主题与尺寸。已经打开的应用可能缓存了旧指针，关闭再打开通常即可刷新；旧终端的环境变量也可能保留旧主题，通过旧终端启动的程序会继承它。遇到这种情况，重新打开终端，或用 `Super + Space` 启动应用。

快速摇动时才变成另一种指针，通常是正常指针由旧应用提供、放大动画使用新主题。
先把鼠标移到桌面空白处验证所选外观；仅个别旧窗口不同的，保存工作后重新打开对应应用。

部分 Wayland 应用自行绘制指针，XWayland 应用也可能缓存自己的图案；浏览器网页、游戏和远程桌面还可以指定自定义光标，因此不能保证每个区域都显示完全相同的图案或运动。Flatpak 中的主题资源还受沙箱可见范围限制。

Xcursor 格式主题在大幅放大时可能没有原生 Hyprcursor 主题那么细腻。管理器会按主题格式选择兼容模式，避免放大时突然换成另一套指针；正常大小时仍使用所选主题。

## 动画插件不可用时

鼠标外观和尺寸依赖已经安装的主题资源，运动和摇动放大另外使用 `hypr-dynamic-cursors`。本机插件只在 Hyprland ABI 与构建时一致时加载；升级 Hyprland 后如果动画消失，先查看：

```bash
hyprctl plugin list
~/.config/hypr/bin/cursor-switch status
```

ABI 不匹配时需要重新构建插件。菜单中的选择可以保留，等插件兼容后再应用；不要强制加载旧二进制。安装和构建资源位于用户目录，鼠标设置不需要 sudo，也不需要注销当前会话。
