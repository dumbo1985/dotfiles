#!/usr/bin/env bash
#
# install.sh —— dotfiles 一键部署（幂等，可反复执行）
#
# 新机器完整流程：
#   git clone --branch forUbuntu https://github.com/dumbo1985/dotfiles.git ~/dotfiles
#   ~/dotfiles/install.sh
#
# 本脚本做"接线"（软链 / 追加 / 部署文件），不自动 sudo 装 apt 依赖——
# 结束时会打印依赖安装命令，自行确认后执行。
#
# 用法：
#   install.sh                  部署全部（nvim / clangd / blerc / 跳转命令 / 壁纸）
#   install.sh --skip-wallpaper 不部署壁纸脚本（只做开发环境）
#
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKIP_WALLPAPER=0
[[ "${1:-}" == "--skip-wallpaper" ]] && SKIP_WALLPAPER=1

say() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m警告:\033[0m %s\n' "$*" >&2; }

# link <仓库文件> <目标>：把目标变成指向仓库的软链；已有真实文件则备份为 *.pre-dotfiles.bak
link() {
	local src="$1" dst="$2"
	mkdir -p "$(dirname "$dst")"
	if [[ -L "$dst" ]]; then
		ln -sfn "$src" "$dst"
	elif [[ -e "$dst" ]]; then
		mv "$dst" "${dst}.pre-dotfiles.bak"
		warn "原有文件已备份为 ${dst}.pre-dotfiles.bak"
		ln -sfn "$src" "$dst"
	else
		ln -sfn "$src" "$dst"
	fi
}

say "1/5 nvim 配置（软链 ~/.config/nvim）"
link "$REPO/nvim" "$HOME/.config/nvim"

say "2/5 clangd 公共库兜底配置（软链 ~/.config/clangd/config.yaml）"
link "$REPO/clangd/config.yaml" "$HOME/.config/clangd/config.yaml"

say "3/5 blerc（ble.sh + fzf 集成，软链 ~/.blerc）"
# 注意：~/.blerc 只在装了 ble.sh 并在 bashrc 里加载它时才生效，没装也不影响
link "$REPO/ble/blerc" "$HOME/.blerc"

say "4/5 bashrc 跳转命令（workspace / dengprojects）"
MB='# >>> dotfiles:jump >>>'
ME='# <<< dotfiles:jump <<<'
# 先删旧标记块（幂等），再追加指向本仓库 jump.sh 的 source 行
sed -i "/^${MB}\$/,/^${ME}\$/d" "$HOME/.bashrc"
printf '\n%s\n[[ -f "%s/bash/jump.sh" ]] && source "%s/bash/jump.sh"\n%s\n' \
	"$MB" "$REPO" "$REPO" "$ME" >> "$HOME/.bashrc"

say "5/5 PATH 检查"
case ":${PATH}:" in
	*":${HOME}/.local/bin:"*) ;;
	*) warn "~/.local/bin 不在 PATH 中，请在 ~/.bashrc 加入：export PATH=\"\$HOME/.local/bin:\$PATH\" 并重开终端" ;;
esac

if [[ "$SKIP_WALLPAPER" -eq 0 ]]; then
	say "壁纸脚本（复制部署到 ~/.local/bin 与 ~/.config/systemd/user）"
	mkdir -p "$HOME/.local/bin" "$HOME/.config/systemd/user"
	install -m 755 "$REPO/wallpaper/bin/"* "$HOME/.local/bin/"
	install -m 644 "$REPO/wallpaper/systemd/"* "$HOME/.config/systemd/user/"
	# 脚本内部会自动选路：systemd user timer 可用则用之，否则退自启动并打印 cron 方案
	"$HOME/.local/bin/install-daily-wallpaper" install 10:00 \
		|| warn "壁纸调度安装未完全成功，可稍后运行 install-daily-wallpaper status 查看"
else
	say "已按 --skip-wallpaper 跳过壁纸脚本"
fi

cat <<'EOF'

部署完成。还差最后两步（本脚本不代跑 sudo）：

1) 系统依赖（含 Neovim 之外的 CLI、LSP 调试工具链等，详见 README）：
   sudo apt update && sudo apt install -y git curl unzip build-essential ripgrep fd-find \
     universal-ctags global python3 python3-venv python3-pip nodejs npm golang-go \
     g++ gdb cmake shellcheck wl-clipboard xclip
   另外需手动安装：Neovim 0.12+ 与 tree-sitter CLI 0.26.1+（见 README 安装步骤）。

2) 重开终端（让 bashrc 的跳转命令与 blerc 生效），然后 nvim 首次启动会自动装插件。

重新部署/更新配置：进入 ~/dotfiles 执行 git pull && ./install.sh 即可，脚本幂等。
EOF
