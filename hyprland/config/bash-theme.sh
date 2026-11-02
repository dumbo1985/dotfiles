# Tokyo Night prompt; sourced only by interactive Hyprland shells.
# Use Bash's built-in \w expansion instead of running a process for every prompt.
PS1='\[\e[38;2;130;170;255m\]╭─ \[\e[38;2;199;146;234m\]\w\[\e[38;2;70;75;93m\]  \u@\h\n\[\e[38;2;130;170;255m\]╰─\[\e[38;2;195;232;141m\] ❯\[\e[0m\] '
export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:-} --color=bg+:#1a1c25,bg:#0f111a,spinner:#c792ea,hl:#82aaff,fg:#a6accd,header:#464b5d,info:#89ddff,pointer:#c792ea,marker:#c3e88d,prompt:#82aaff,hl+:#89ddff --border=rounded --prompt=❯\ "
export BAT_THEME='TwoDark'
