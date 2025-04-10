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
4. Install A Nerd Font
5. Install Nvim
6. Install Neovide
7. Install Ripgrep
8. Install Node
9. Install lazygit
   ```shell
   # 通过二进制安装
   LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v*([^"]+)".*/\1/')
   curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
   tar xf lazygit.tar.gz
   sudo install lazygit /usr/local/bin
   ```

## 二、Usage

```shell
cd dotfiles
```

Create a soft link for nvim

```shell
ln -s dotfiles/nvim ~/.config/nvim
```
