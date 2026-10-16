#!/usr/bin/env bash
# ==============================================================================
# 安装 Ubuntu 24.04 官方 apt 源里【没有】的命令行工具
# ------------------------------------------------------------------------------
# 全部走各项目 GitHub Releases 的官方预编译二进制，不编译、不加第三方 PPA。
#
# 用法：
#   bash install-extra-cli-tools.sh --dry-run     # 只显示会装什么，不下载不安装
#   bash install-extra-cli-tools.sh               # 全部安装
#   bash install-extra-cli-tools.sh lazygit dust  # 只装指定几个
#   bash install-extra-cli-tools.sh --list        # 列出支持的工具
#
# 说明：
#   * .deb  → sudo apt install ./xxx.deb   （apt 会自动补依赖，比 dpkg -i 稳）
#   * tar.gz/zip → 解包后把可执行文件放到 ~/.local/bin
#   * 裸二进制 → 直接下到 ~/.local/bin
#   * 版本号在运行时从 GitHub API 动态取，不用手写、不会过期
# ==============================================================================

set -u

C_CYAN=$'\033[1;36m'; C_YEL=$'\033[1;33m'; C_RED=$'\033[1;31m'
C_GRN=$'\033[1;32m'; C_OFF=$'\033[0m'

DRY_RUN=0
FORCE=0
WANTED=()

usage() {
  cat <<'USAGE'
用法：
  bash install-extra-cli-tools.sh --dry-run     # 只显示会装什么，不下载不安装
  bash install-extra-cli-tools.sh               # 全部安装
  bash install-extra-cli-tools.sh lazygit dust  # 只装指定几个
  bash install-extra-cli-tools.sh --list        # 列出支持的工具
  bash install-extra-cli-tools.sh --force       # 已装的也强制重装
USAGE
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --force)   FORCE=1 ;;
    --list|-l) WANTED=("__LIST__") ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "未知参数：$1" >&2; usage; exit 1 ;;
    *) WANTED+=("$1") ;;
  esac
  shift
done

log()  { printf '\n%s==> %s%s\n' "$C_CYAN" "$*" "$C_OFF"; }
ok()   { printf '  %s✓%s %s\n' "$C_GRN" "$C_OFF" "$*"; }
warn() { printf '  %s[!]%s %s\n' "$C_YEL" "$C_OFF" "$*"; }
err()  { printf '  %s[x]%s %s\n' "$C_RED" "$C_OFF" "$*"; }

# ------------------------------------------------------------------------------
# 工具表： 名称 | 仓库 | 固定tag(空=取最新) | 方式 | 资源名正则 | 命令名
#   方式：deb=deb包  tar=压缩包  zip=压缩包  bin=裸二进制
#   命令名：装好之后真正的可执行文件名，用于「已安装检测 / 安装目标 / 版本校验」
#           （不能直接用名称！例如 git-extras 附带一个毫无关系的 /usr/bin/git-delta）
#   ※ 正则里不要用竖线 |，那会和字段分隔符冲突
# ------------------------------------------------------------------------------
TOOLS=(
  "lazygit|jesseduffield/lazygit||tar|lazygit_.*_linux_x86_64\.tar\.gz$|lazygit"
  "git-delta|dandavison/delta||deb|^git-delta_.*_amd64\.deb$|delta"
  "dust|bootandy/dust||deb|^du-dust_.*_amd64\.deb$|dust"
  "procs|dalance/procs||zip|procs-.*-x86_64-linux\.zip$|procs"
  "tokei|XAMPPRocky/tokei|v12.1.2|tar|tokei-x86_64-unknown-linux-musl\.tar\.gz$|tokei"
  "fastfetch|fastfetch-cli/fastfetch||deb|^fastfetch-linux-amd64\.deb$|fastfetch"
  "zellij|zellij-org/zellij||tar|^zellij-x86_64-unknown-linux-musl\.tar\.gz$|zellij"
  "broot|Canop/broot||zip|\.zip$|broot"
  "doggo|mr-karan/doggo||tar|^doggo-linux-x86_64\.tar\.gz$|doggo"
  "bandwhich|imsnif/bandwhich||tar|bandwhich-.*-x86_64-unknown-linux-musl\.tar\.gz$|bandwhich"
  "choose|theryangeary/choose||bin|^choose-x86_64-unknown-linux-musl$|choose"
)

if [[ "${WANTED[*]:-}" == *"__LIST__"* ]]; then
  printf '支持的工具：\n'
  for t in "${TOOLS[@]}"; do printf '  %-11s  %s\n' "${t%%|*}" "$(echo "$t" | cut -d'|' -f2)"; done
  exit 0
fi

# ------------------------------------------------------------------------------
# 依赖检查
# ------------------------------------------------------------------------------
for c in curl python3; do
  command -v "$c" >/dev/null 2>&1 || { err "缺少依赖：$c，请先安装"; exit 1; }
done
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# ------------------------------------------------------------------------------
# 从 GitHub API 取匹配资源的下载地址
# ------------------------------------------------------------------------------
asset_url() { # $1=repo $2=tag $3=regex
  local api
  if [[ -n "$2" ]]; then
    api="https://api.github.com/repos/$1/releases/tags/$2"
  else
    api="https://api.github.com/repos/$1/releases/latest"
  fi
  curl -fsSL --retry 2 \
       -H 'Accept: application/vnd.github+json' \
       -H 'User-Agent: cli-toolbox' \
       "$api" 2>/dev/null | python3 -c '
import json, re, sys
pat = sys.argv[1]
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(3)
for a in data.get("assets", []):
    if re.search(pat, a["name"]):
        print(a["browser_download_url"])
        sys.exit(0)
sys.exit(4)
' "$3"
}

is_elf() { [[ "$(head -c 4 "$1" 2>/dev/null | od -An -tx1 | tr -d ' \n')" == "7f454c46" ]]; }

# 从解包目录里挑出目标可执行文件（必须真的是 ELF，避免误抓同名 shell 脚本）
pick_binary() { # $1=目录 $2=期望名字
  local dir="$1" want="$2" f
  if [[ -n "$want" ]]; then
    while IFS= read -r f; do
      if is_elf "$f"; then printf '%s' "$f"; return 0; fi
    done < <(find "$dir" -type f -name "$want")
  fi
  # 兜底：随便找一个 ELF 可执行文件
  while IFS= read -r f; do
    if is_elf "$f"; then printf '%s' "$f"; return 0; fi
  done < <(find "$dir" -type f)
  return 1
}

# 由工具名反查真正的命令名（版本校验时用，避免误跑 git-extras 的 git-delta）
cmd_for() {
  local t
  for t in "${TOOLS[@]}"; do
    IFS='|' read -r _n _r _g _m _re _c <<<"$t"
    [[ "$_n" == "$1" ]] && { printf '%s' "$_c"; return 0; }
  done
  printf '%s' "$1"
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

INSTALLED=(); SKIPPED=(); FAILED=()

# ------------------------------------------------------------------------------
# 主循环
# ------------------------------------------------------------------------------
for spec in "${TOOLS[@]}"; do
  IFS='|' read -r name repo tag mode re cmdname <<<"$spec"

  if ((${#WANTED[@]})) && [[ " ${WANTED[*]} " != *" $name "* ]]; then continue; fi

  log "$name   ($repo)"

  if command -v "$cmdname" >/dev/null 2>&1 && ((!FORCE)); then
    warn "已安装：$(command -v "$cmdname")  —— 用 --force 可强制重装"
    SKIPPED+=("$name"); continue
  fi

  url="$(asset_url "$repo" "$tag" "$re")" || {
    err "没能从 GitHub 找到匹配 '$re' 的资源（可能是限流或资源改名了）"
    FAILED+=("$name"); continue
  }
  printf '  下载地址：%s\n' "$url"

  if ((DRY_RUN)); then
    ok "[dry-run] 跳过实际安装"
    INSTALLED+=("$name"); continue
  fi

  fname="${url##*/}"
  fpath="$TMP/$fname"
  printf '  下载中…\n'
  if ! curl -fL --retry 3 --progress-bar -o "$fpath" "$url"; then
    err "下载失败"; FAILED+=("$name"); continue
  fi

  case "$mode" in
    deb)
      if sudo apt install -y "$fpath"; then ok "deb 安装完成"; INSTALLED+=("$name")
      else err "deb 安装失败"; FAILED+=("$name"); fi
      ;;
    tar|zip)
      exdir="$TMP/x_$name"; mkdir -p "$exdir"
      if [[ "$mode" == zip ]]; then
        unzip -q -o "$fpath" -d "$exdir" || { err "解压失败"; FAILED+=("$name"); continue; }
      else
        tar -xzf "$fpath" -C "$exdir" || { err "解压失败"; FAILED+=("$name"); continue; }
      fi
      src="$(pick_binary "$exdir" "$cmdname")" || {
        err "解包后没找到可执行文件，内容如下："; find "$exdir" -type f | head -20
        FAILED+=("$name"); continue
      }
      install -m 0755 "$src" "$BIN_DIR/$cmdname" \
        && ok "已安装到 $BIN_DIR/$cmdname" && INSTALLED+=("$name")
      ;;
    bin)
      install -m 0755 "$fpath" "$BIN_DIR/$cmdname" \
        && ok "已安装到 $BIN_DIR/$cmdname" && INSTALLED+=("$name")
      ;;
    *) err "未知安装方式：$mode"; FAILED+=("$name") ;;
  esac
done

# ------------------------------------------------------------------------------
# 汇总与校验
# ------------------------------------------------------------------------------
log "结果汇总"
printf '  新装 %d 个 / 跳过 %d 个 / 失败 %d 个\n' "${#INSTALLED[@]}" "${#SKIPPED[@]}" "${#FAILED[@]}"
((${#FAILED[@]})) && err "失败：${FAILED[*]}"
((${#SKIPPED[@]})) && warn "跳过：${SKIPPED[*]}"

if ((!DRY_RUN)) && ((${#INSTALLED[@]})); then
  printf '\n  版本校验：\n'
  for t in "${INSTALLED[@]}"; do
    c="$(cmd_for "$t")"
    v="$("$c" --version 2>&1 | head -n1)" || true
    printf '    %-11s %s\n' "$c" "${v:-（无 --version 输出，属正常）}"
  done
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) : ;;
  *) printf '\n  %s[!]%s %s 不在 PATH 中，请重新登录或执行：\n' "$C_YEL" "$C_OFF" "$BIN_DIR"
     printf '      export PATH="%s:$PATH"\n' "$BIN_DIR" ;;
esac

cat <<'EOF'

  装完的小提示：
    broot     首次使用执行一次  broot --install   （写入 shell 函数 br）
    zellij    首次使用执行一次  zellij setup --check
    delta     在 ~/.gitconfig 里启用：
                [core]  pager = delta
                [interactive]  diffFilter = delta --color-only
    bandwhich 需要读网络接口，非 root 运行要：
                sudo setcap cap_net_raw,cap_net_admin+eip ~/.local/bin/bandwhich
    doggo     需要读 DNS，个别系统要 sudo 才能做 @udp:// 之类查询

  两个容易踩的坑：
    * git-delta —— Ubuntu 源里其实【有】git-delta（0.16.5，比上游 0.20.1 旧）。
      不追求新版本的话，sudo apt install git-delta 一句话就够了，不必用本脚本。
      另外 git-extras 会附带一个同名的 /usr/bin/git-delta，那只是个 shell 包装脚本，
      跟 dandavison/delta 毫无关系 —— 别被 `which git-delta` 骗了。
      真正要调用的命令名是 **delta**。
    * tokei —— 上游从 v13 起就不再发布预编译二进制了，本脚本只能退回 2021 年的 v12.1.2。
      想要新版本：sudo apt install cargo && cargo install --locked tokei
      或者直接用 apt 里的 cloc 做代码行数统计。
EOF
