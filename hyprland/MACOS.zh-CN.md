# 快速预览、窗口切换、截图识字与布局记忆

这四项功能沿用当前 Hyprland 桌面配置，不需要改变日常的应用或工作区操作。

## 文件快速预览

在文件管理器中选中文件，按 **空格** 打开预览；再次按空格或 Esc 关闭，Enter 用默认应用打开。
支持图片、PDF、视频和文本／源代码。PDF 可用左右方向键翻页；文本可以滚动。
文件夹显示目录概况，其他文件类型显示基本信息。

在 `Super + Space` 中搜索并选中文件后，按 **Alt + P** 预览。这里保留普通空格输入文件名，
也保留 `Ctrl + Space` 的输入法切换功能。

也可以在终端指定文件：

```bash
~/.config/hypr/bin/file-preview ~/dotfiles/README.md
~/.config/hypr/bin/file-preview --close
```

预览服务通过 Nautilus 自带的预览接口接收选中文件。服务在登录时启动，也可手动运行
`~/.config/hypr/bin/file-preview --start`。

## 应用和同应用窗口切换

| 快捷键 | 用途 |
| --- | --- |
| `Super + Tab` | 切换到下一个应用 |
| `Super + Shift + Tab` | 反向切换应用 |
| `Super + 反引号` | 切换当前应用的下一扇窗口 |
| `Super + Shift + 反引号` | 反向切换当前应用的窗口 |

反引号是英文键盘数字 1 左侧的 `` ` `` 键。多开 Neovide 时，先聚焦一扇 Neovide，再按
`Super + 反引号` 即可在同类窗口间切换。连续按键会沿列表轮换；停顿后按最近使用顺序重新开始。
若当前应用只有一扇窗口，则保持当前窗口。

要按窗口标题查找，仍可使用 `Super + W` 或在统一启动器中输入 `w neovide`。

## 截图识字

| 快捷键 | 用途 |
| --- | --- |
| `Super + Shift + O` | 框选中英文并识别为文字 |
| `Super + Ctrl + O` | 代码模式，尽量保留换行与空格 |

框选后在本机识别，成功后自动复制，回到目标应用粘贴即可。框选时 Esc 取消；没有识别出文字时保留原剪贴板。
也可在启动器中输入“识字”，或从截图菜单选择“框选识字”“代码识字”。

代码模式保留识别结果的排版，但缩进、标点、相似字符仍需核对。中文模型主要针对简体中文。
识别过程不会上传截图，临时图像在结束后删除。

只识别已有图片、将结果输出到终端：

```bash
~/.config/hypr/bin/screen-ocr --file /absolute/path/image.png --stdout
~/.config/hypr/bin/screen-ocr --file /absolute/path/code.png --code --stdout
~/.config/hypr/bin/screen-ocr --check
```

## 双屏窗口布局记忆

后台服务自动学习应用使用的显示器、工作区和浮动窗口位置。打开应用窗口时会尝试恢复记住的位置，
显示器断开再连接后会尝试把原窗口放回对应屏幕。目标屏幕没有连接时，不强行恢复到其他屏幕。

平铺窗口恢复屏幕和工作区，具体大小继续交给 Hyprland 的平铺布局；浮动窗口同时恢复位置和大小，
并限制在可见范围内。预览等临时窗口不会被记住。

窗口布局恢复不会启动应用。重新登录后先打开相应应用，编辑器文件、浏览器标签等内容由应用自身恢复。
同类窗口通过窗口标题和已有记录匹配；窗口标题完全相同或不断变化时，无法保证每一扇窗口都对应到原来的记录。

在启动器搜索“保存窗口布局”或“恢复窗口布局”，也可运行：

```bash
~/.config/hypr/bin/window-layout --status
~/.config/hypr/bin/window-layout --save
~/.config/hypr/bin/window-layout --restore --dry-run
~/.config/hypr/bin/window-layout --restore
```

`--save` 只保存当前布局；`--restore --dry-run` 只显示恢复计划。若想暂停自动记忆，运行
`~/.config/hypr/bin/window-layout --stop`；重新启用时运行 `--start`。

## 本机依赖

OCR 的 Tesseract 程序和中英文模型放在 `~/.local/share/hypr-ocr/`，
预览需要的可选媒体资源放在 `~/.local/share/hypr-preview/`。这些是用户目录资源。
迁移到新机器时，应同时准备依赖，或者通过 `install.sh` 安装对应系统软件包。

本轮修改前的配置备份位于
`~/.local/state/dotfiles-hyprland/before-macos-20261030-180302/`。
