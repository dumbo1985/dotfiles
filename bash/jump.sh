# 快速跳转：任意位置敲命令名即进入对应目录，带子目录参数则直达，Tab 补全实时生效。
# 本文件由 ~/dotfiles/install.sh 以标记块方式 source 进 ~/.bashrc，可独立 source 测试。
# 新增常用目录只需在下面加一行 _def_jump。目录下新建的子目录自动可达、自动补全，无需维护。
_def_jump() {
	local name="$1" dir="$2"
	eval "${name}() {
		local d=\"${dir}\${1:+/\$1}\"
		if [[ -d \"\$d\" ]]; then
			cd \"\$d\"
		else
			echo \"${name}: 目录不存在: \$d\" >&2
			return 1
		fi
	}"
	eval "_${name}() {
		local cur=\"\${COMP_WORDS[COMP_CWORD]}\"
		COMPREPLY=( \$(compgen -d -- \"${dir}/\${cur}\" 2>/dev/null | sed \"s|^${dir}/||\") )
	}"
	complete -o nospace -F "_${name}" "${name}"
}

_def_jump workspace    "$HOME/Documents/workspace"
_def_jump dengprojects "$HOME/Documents/dengprojects"
