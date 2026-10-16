#!/usr/bin/env bash
# ==============================================================================
# Ubuntu 24.04 命令行工具箱 一键安装脚本
# ------------------------------------------------------------------------------
# 用法：   bash ubuntu24-cli-toolbox.sh
#         （需要 sudo 权限，脚本会自己调用 sudo，不用整脚本用 root 跑）
#
# 设计原则：
#   1. 只安装 Ubuntu 24.04 (noble) 官方源里【确认存在】的包，不会卡住报错；
#   2. 按功能分组安装，某一组失败不影响后面的组；
#   3. 不在官方源的工具单独列在文件末尾，附上游下载地址。
# ==============================================================================

set -u

C_CYAN=$'\033[1;36m'; C_YEL=$'\033[1;33m'; C_RED=$'\033[1;31m'; C_OFF=$'\033[0m'
log()  { printf '\n%s==> %s%s\n' "$C_CYAN" "$*" "$C_OFF"; }
warn() { printf '%s[!] %s%s\n'  "$C_YEL" "$*" "$C_OFF"; }
fail() { printf '%s[x] %s%s\n'  "$C_RED" "$*" "$C_OFF"; }

command -v apt >/dev/null 2>&1 || { fail "未检测到 apt，本脚本仅适用于 Debian/Ubuntu 系。"; exit 1; }

log "第 1 步：更新软件包索引"
sudo apt update || warn "apt update 失败，继续尝试安装（可能用的是旧索引）"

# ------------------------------------------------------------------------------
# 第 2 步：分组安装（每组 "名称|包名列表"）
# ------------------------------------------------------------------------------
# 注意：数组名【不能】叫 GROUPS —— 那是 bash 的内置特殊变量（存放当前用户所属组的 ID），
# 对它的赋值会被静默忽略，循环会变成去遍历用户组 ID，导致 apt 报「无法定位软件包 1000」。
TOOLBOX_GROUPS=(
  "现代 CLI 替代品（替代 ls/cat/grep/find/sed）|ripgrep fd-find bat fzf eza sd hexyl"
  "文本与数据处理|jq yq moreutils jc shellcheck shfmt yamllint"
  "系统与资源监控|htop btop glances ncdu duf lsof"
  "Git 与开发效率|tig git-extras just hyperfine ccache direnv entr git-delta"
  "终端与 Shell 增强|tmux zoxide autojump trash-cli thefuck xclip wl-clipboard"
  "文件与传输|rsync sshfs unison aria2 httpie pv progress atool rename"
  "网络诊断|nmap mtr-tiny traceroute iftop nethogs bmon socat netcat-openbsd bind9-dnsutils whois speedtest-cli iperf3 telnet"
  "压缩与解压|unzip zip p7zip-full zstd pigz"
  "趣味与展示|neofetch lolcat cowsay figlet"
)

# 自检：分组表如果读不到（例如又踩了保留变量），立刻中止而不是空跑
if (( ${#TOOLBOX_GROUPS[@]} == 0 )); then
  fail "工具分组表为空——脚本内部错误，已中止。"
  exit 1
fi
printf '共 %d 个功能分组待安装。\n' "${#TOOLBOX_GROUPS[@]}"

OK_LIST=(); FAIL_LIST=()

for entry in "${TOOLBOX_GROUPS[@]}"; do
  gname="${entry%%|*}"
  pkgs="${entry#*|}"
  log "安装：$gname"

  # 先逐个过滤出官方源里真实存在的包，避免一个包缺失导致整组 install 失败
  avail=()
  for p in $pkgs; do
    if apt-cache show "$p" >/dev/null 2>&1; then
      avail+=("$p")
    else
      warn "  跳过（官方源中不存在）：$p"
    fi
  done
  if (( ${#avail[@]} == 0 )); then
    warn "  该组没有可安装的包，跳过。"
    continue
  fi

  if sudo apt install -y --no-install-recommends "${avail[@]}"; then
    OK_LIST+=("$gname")
  else
    fail "该组安装未全部成功：$gname"
    FAIL_LIST+=("$gname")
  fi
done

# ------------------------------------------------------------------------------
# 第 3 步：~/.local/bin 里补软链接
#   Debian/Ubuntu 因为命令名冲突把 bat 改成了 batcat、fd 改成了 fdfind
# ------------------------------------------------------------------------------
log "第 3 步：创建 batcat -> bat、fdfind -> fd 的软链接"
mkdir -p "$HOME/.local/bin"
[ -x /usr/bin/batcat ] && ln -sf /usr/bin/batcat "$HOME/.local/bin/bat" && echo "  ✓ ~/.local/bin/bat"
[ -x /usr/bin/fdfind ] && ln -sf /usr/bin/fdfind "$HOME/.local/bin/fd"  && echo "  ✓ ~/.local/bin/fd"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) : ;;
  *) warn "~/.local/bin 不在 PATH 里，请确认 ~/.profile 已加载（重新登录一次即可）" ;;
esac

# ------------------------------------------------------------------------------
# 第 4 步：往 ~/.bashrc 追加配置块（带标记，可重复执行不会重复写）
# ------------------------------------------------------------------------------
log "第 4 步：配置 ~/.bashrc"
BASHRC="$HOME/.bashrc"
touch "$BASHRC" 2>/dev/null || true
if grep -q '>>> cli-toolbox >>>' "$BASHRC"; then
  warn "已存在 cli-toolbox 配置块，跳过（如需重写请手动删除该块）"
else
  cp -a "$BASHRC" "$BASHRC.bak.$(date +%Y%m%d%H%M%S)"
  cat >> "$BASHRC" <<'EOF'

# >>> cli-toolbox >>>
# ---- 现代替代品别名 ----
if command -v eza >/dev/null 2>&1; then
  alias ls='eza --group-directories-first'
  alias ll='eza -alh --group-directories-first --git --time-style=long-iso'
  alias la='eza -A --group-directories-first'
  alias lt='eza --tree --level=2 --group-directories-first'
fi
command -v batcat >/dev/null 2>&1 && alias bat='batcat'
command -v fdfind >/dev/null 2>&1 && alias fd='fdfind'
# 注意：rg 不完全兼容 grep 的参数，别名请谨慎启用
# alias grep='rg'

# ---- 交互增强 ----
command -v zoxide  >/dev/null 2>&1 && eval "$(zoxide init bash)"
command -v direnv  >/dev/null 2>&1 && eval "$(direnv hook bash)"
command -v thefuck >/dev/null 2>&1 && eval "$(thefuck --alias)"   # 启动约 +100ms，嫌慢就注释掉
[ -s /usr/share/autojump/autojump.sh ] && . /usr/share/autojump/autojump.sh

# ---- fzf 快捷键 (Ctrl+R / Ctrl+T / Alt+C) ----
[ -f /usr/share/doc/fzf/examples/key-bindings.bash ] && . /usr/share/doc/fzf/examples/key-bindings.bash
[ -f /usr/share/doc/fzf/examples/completion.bash ]   && . /usr/share/doc/fzf/examples/completion.bash

# ---- 彩色手册 & 更好用的 less ----
export LESS='-R -F -X'
export MANPAGER='less -R'
# <<< cli-toolbox <<<
EOF
  echo "  ✓ 已写入（原文件已备份为 $BASHRC.bak.*）"
  echo "  → 执行 source ~/.bashrc 或重开终端生效"
fi

# ------------------------------------------------------------------------------
# 第 5 步：结果汇总
# ------------------------------------------------------------------------------
log "安装完成汇总"
printf '成功分组：%d/%d\n' "${#OK_LIST[@]}" "${#TOOLBOX_GROUPS[@]}"
((${#FAIL_LIST[@]})) && warn "失败分组：${FAIL_LIST[*]}（多半是网络或索引问题，可重跑）"

cat <<'EOF'

==============================================================================
以下工具 Ubuntu 24.04 官方源没有，需要额外途径：
（一键安装脚本见同目录的 install-extra-cli-tools.sh）

  lazygit    https://github.com/jesseduffield/lazygit/releases   (tar.gz)
  dust       https://github.com/bootandy/dust/releases           (磁盘占用，du 替代)
  procs      https://github.com/dalance/procs/releases            (ps 替代)
  tokei      https://github.com/XAMPPRocky/tokei/releases         (代码行数统计)
  fastfetch  https://github.com/fastfetch-cli/fastfetch/releases  (neofetch 替代)
  zellij     https://github.com/zellij-org/zellij/releases        (tmux 替代)
  broot      https://github.com/Canop/broot/releases              (交互式目录树)
  doggo      https://github.com/mr-karan/doggo/releases           (dig 现代替代)
  bandwhich  https://github.com/imsnif/bandwhich/releases         (按进程看流量)
  choose     https://github.com/theryangeary/choose/releases      (cut 替代)

  ⚠ 三个同名坑，务必分清：
    1) delta       —— apt 里的 delta 是 GNU patch 的 diff 后处理器(2006.08.03)，
                      千万别为了 Git 高亮去装它。
    2) git-delta   —— 这个【源里有】(0.16.5)，已包含在上面的安装组里，
                      命令名是 delta。想要更新的 0.20.1 见 install-extra-cli-tools.sh。
    3) /usr/bin/git-delta —— git-extras 附带的 shell 包装脚本，跟 delta 毫无关系，
                      别被 `which git-delta` 骗了。

  通用三条路：
    1) 直接下上游的 .deb，然后  sudo dpkg -i xxx.deb
    2) 装 Rust 后  sudo apt install cargo && cargo install --locked <名字>
       （cargo install 装到 ~/.cargo/bin，注意 PATH）
    3) snap install <名字>   —— 本机 snap 可用
==============================================================================
EOF
