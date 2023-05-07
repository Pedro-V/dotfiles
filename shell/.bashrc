#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return
[[ -z "$FUNCNEST" ]] && export FUNCNEST=100    # limits recursive functions, see 'man bash'

# aliases

alias ls='ls --color=auto'
alias ll='ls -lav --ignore=..'   # show long listing of all except ".."
alias l='ls -lav --ignore=.?*'   # show long listing but no hidden dotfiles except "."

# PATH

export PATH="$HOME/.local/bin:$PATH"

## Use the up and down arrow keys for finding a command in history
## (you can write some initial letters of the command first).
bind '"\e[A":history-search-backward'
bind '"\e[B":history-search-forward'

parse_git_branch() {
	git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/ \(.*\)/ (\1)/'
}

pyactivate() {
	. ~/.virtualenvs/"$*"/bin/activate
}

export PS1="\[\033[01;32m\][\u@\h\[\033[01;37m\] \W\[\033[33m\]\$(parse_git_branch)\[\033[01;32m\]]\$\[\033[00m\] "
. "$HOME/.cargo/env"

[ -f "/home/pedrov/.ghcup/env" ] && source "/home/pedrov/.ghcup/env" # ghcup-env

xset b off
