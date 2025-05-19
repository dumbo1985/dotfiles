# dotfiles

Dotfiles on my mac. I'll create a branch for Ubuntu.

## 一、Install

Open a terminal window on your mac. Recommend Item2 and oh-my-zsh.

1. Install Homebrew

2. Install Item2  
   You will need a true color terminal for the colorscheme to work properly.
   ```shell
   brew install --cask iterm2
   ```
3. Install A Nerd Font

4. Install Nvim

5. Install Neovide

6. Install Ripgrep

7. Install Node

8. Install lazygit
   ```shell
   # 通过二进制安装
   LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v*([^"]+)".*/\1/')
   curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
   tar xf lazygit.tar.gz
   sudo install lazygit /usr/local/bin
   ```
9. Install ruby

   ```shell
   sudo apt install ruby-full
   ```

10. Install im-select
    a. 打开它的 GitHub 项目：https://github.com/daipeihust/im-select
    b. 下载最新的 macOS 版本（例如 im-select-mac，通常在 Releases 页面）
    c. 解压后放入 /usr/local/bin 或者其他你的 PATH 中

## 二、Usage

```shell
cd dotfiles
```

Create a soft link for nvim

```shell
ln -s dotfiles/nvim ~/.config/nvim
```
