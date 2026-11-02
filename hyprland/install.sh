#!/usr/bin/env bash
# Ubuntu 24.04 + Hyprland 0.57; keep GDM and the GNOME session.
set -euo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles-hyprland"
FINGERPRINT=A54D23B62FF3FCC76EFF71E8FDBAAA1CF0CCF48E
HYPRLAND_VERSION=0.57.0-1ppa2
PACKAGES=(
    "hyprland=$HYPRLAND_VERSION" xdg-desktop-portal-hyprland
    hyprland-guiutils hyprlock hypridle waybar wofi mako-notifier swaybg
    grim slurp wl-clipboard fd-find kitty polkit-kde-agent-1 network-manager-gnome
    xdg-desktop-portal-gtk pavucontrol playerctl brightnessctl
    python3-gi python3-cairo python3-gi-cairo python3-pil gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1
    gir1.2-gtk-4.0 poppler-utils ffmpeg libgtk-4-media-gstreamer gstreamer1.0-libav
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good
    tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim tesseract-ocr-osd
)

usage() {
    cat <<'EOF'
用法：
  bash hyprland/install.sh --check      检查系统，不修改软件源或配置
  bash hyprland/install.sh --configure  仅部署用户配置，不需要 sudo
  bash hyprland/install.sh --install    加入第三方 PPA、安装软件并部署配置

--install 需要在本机终端输入 sudo 密码。它会升级共享的音频/输入库；
保留 GDM 和 GNOME，不注销、不重启、不改显卡驱动。
PPA：https://launchpad.net/~cppiber/+archive/ubuntu/hyprland
EOF
}

check_os() {
    # shellcheck disable=SC1091
    source /etc/os-release
    if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 || "$(dpkg --print-architecture)" != amd64 ]]; then
        echo '此安装脚本只针对 Ubuntu 24.04 amd64 验证过。' >&2
        exit 1
    fi
}

configure() {
    local target="$CONFIG_DIR/hypr" backup
    mkdir -p "$CONFIG_DIR" "$STATE_DIR"
    if [[ "$(readlink -f -- "$target" 2>/dev/null || true)" == "$REPO_DIR/config" ]]; then
        echo "配置已连接：$target"
    else
        if [[ -e "$target" || -L "$target" ]]; then
            backup="$STATE_DIR/hypr-$(date +%Y%m%d-%H%M%S)-$$"
            mv -- "$target" "$backup"
            printf '原有配置备份：%s\n' "$backup"
        fi
        ln -s -- "$REPO_DIR/config" "$target"
        printf '已连接：%s -> %s\n' "$target" "$REPO_DIR/config"
    fi
    if command -v Hyprland >/dev/null; then
        Hyprland --verify-config --config "$target/hyprland.lua"
    else
        echo '尚未安装 Hyprland；安装后会用 --verify-config 校验配置。'
    fi
}

install_packages() {
    local stage key_info actual backup
    check_os
    if (( EUID == 0 )); then
        echo '请以日常用户运行；脚本会在必要时调用 sudo。' >&2
        exit 1
    fi
    for cmd in curl gpg apt-get dpkg-query; do
        command -v "$cmd" >/dev/null || { echo "缺少命令：$cmd" >&2; exit 1; }
    done
    stage="$(mktemp -d)"
    # Expand now so the EXIT trap also works after this function returns.
    # shellcheck disable=SC2064
    trap "rm -rf -- '$stage'" EXIT
    mkdir -m 700 "$stage/gnupg"
    curl --fail --silent --show-error --location --retry 2 --max-time 60 \
        "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x$FINGERPRINT" \
        --output "$stage/key.asc"
    key_info="$(gpg --homedir "$stage/gnupg" --batch --show-keys --with-colons "$stage/key.asc")"
    actual="$(awk -F: '$1 == "fpr" { print $10; exit }' <<< "$key_info")"
    [[ "$actual" == "$FINGERPRINT" ]] || { echo 'PPA 签名指纹不匹配。' >&2; exit 1; }
    gpg --homedir "$stage/gnupg" --batch --dearmor --output "$stage/key.gpg" "$stage/key.asc"
    cat > "$stage/hyprland.sources" <<'EOF'
Types: deb
URIs: https://ppa.launchpadcontent.net/cppiber/hyprland/ubuntu/
Suites: noble
Components: main
Architectures: amd64
Signed-By: /etc/apt/keyrings/dotfiles-hyprland.gpg
EOF
    # Allow the reviewed Hyprland stack; block unrelated packages from this PPA.
    cat > "$stage/hyprland.pref" <<'EOF'
Package: hyprland hyprland-* hypridle hyprlock xdg-desktop-portal-hyprland libhypr* libaquamarine* libsdbus-c++2 libdisplay-info3 libinput10 libinput-bin libxkbcommon* libxkbregistry* wayland-protocols libudis86.1 libxcb-errors1 pipewire* libpipewire-* libspa-* gstreamer1.0-pipewire waybar libgtk-layer-shell0
Pin: release o=LP-PPA-cppiber-hyprland
Pin-Priority: 500

Package: *
Pin: release o=LP-PPA-cppiber-hyprland
Pin-Priority: -1
EOF
    mkdir -p "$STATE_DIR"
    backup="$STATE_DIR/before-install-$(date +%Y%m%d-%H%M%S)-$$"
    mkdir "$backup"
    dpkg-query -W -f='${binary:Package}\t${Version}\n' > "$backup/packages.tsv"
    for target in /etc/apt/sources.list.d/dotfiles-hyprland.sources \
        /etc/apt/preferences.d/dotfiles-hyprland /etc/apt/keyrings/dotfiles-hyprland.gpg; do
        if [[ -f "$target" ]]; then cp -- "$target" "$backup/$(basename "$target")"; fi
    done
    printf '安装前软件包及源配置记录：%s\n' "$backup"
    echo '将安装 Hyprland，并更新其所需的 PipeWire、libinput、libxkbcommon 等共享组件。'
    sudo -v
    sudo install -d -m 755 /etc/apt/keyrings
    sudo install -m 644 "$stage/key.gpg" /etc/apt/keyrings/dotfiles-hyprland.gpg
    sudo install -m 644 "$stage/hyprland.sources" /etc/apt/sources.list.d/dotfiles-hyprland.sources
    sudo install -m 644 "$stage/hyprland.pref" /etc/apt/preferences.d/dotfiles-hyprland
    sudo apt-get update
    sudo apt-get --simulate --no-remove --no-install-recommends install "${PACKAGES[@]}" \
        | tee "$backup/apt-plan.txt"
    sudo apt-get --yes --no-remove --no-install-recommends install "${PACKAGES[@]}"
    # Package presets enable these for every graphical session, including GNOME.
    # Our Hyprland start hook runs them with this profile's explicit config paths.
    systemctl --user mask --now waybar.service mako.service hypridle.service
    configure
    cat <<'EOF'

安装完成。保存工作后自行注销，在 GDM 登录界面的齿轮菜单选择 Hyprland。
Super+Enter 打开终端；Super+Space 搜索应用、文件和计算；Super+N 打开 Neovide。
Super+Shift+E 注销 Hyprland。也可以在登录界面重新选择 Ubuntu。
EOF
}

case "${1:---check}" in
    --help|-h) usage ;;
    --check)
        check_os
        apt-cache policy hyprland xdg-desktop-portal-hyprland waybar
        if command -v nvidia-smi >/dev/null; then
            nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
        fi
        usage
        ;;
    --configure) configure ;;
    --install) install_packages ;;
    *) usage >&2; exit 2 ;;
esac
