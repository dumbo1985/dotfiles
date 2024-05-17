# dotfiles

Dotfiles on my mac. Please checkout the branch named forUbuntu on ubuntu.

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
10. Install python3.10-venv on Ubuntu (NO NEED ON MAC)
    ```shell
    sudo apt update
    sudo apt install python3.10
    sudo apt install python3.10-venv
    ```

## 二、Usage

```shell
cd dotfiles
```

Create a soft link for nvim

```shell
ln -s dotfiles/nvim ~/.config/nvim
```
