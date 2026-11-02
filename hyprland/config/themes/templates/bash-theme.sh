# Tokyo Night prompt; sourced only by interactive Hyprland shells.
# Use Bash's built-in \w expansion instead of running a process for every prompt.
PS1='\[\e[38;2;122;162;247m\]╭─ \[\e[38;2;187;154;247m\]\w\[\e[38;2;86;95;137m\]  \u@\h\n\[\e[38;2;122;162;247m\]╰─\[\e[38;2;158;206;106m\] ❯\[\e[0m\] '
export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:-} --color=bg+:#24283b,bg:#1a1b26,spinner:#bb9af7,hl:#7aa2f7,fg:#c0caf5,header:#565f89,info:#7dcfff,pointer:#bb9af7,marker:#9ece6a,prompt:#7aa2f7,hl+:#7dcfff --border=rounded --prompt=❯\ "
export BAT_THEME='TwoDark'
