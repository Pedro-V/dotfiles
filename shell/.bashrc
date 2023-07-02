#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return
[[ -z "$FUNCNEST" ]] && export FUNCNEST=100    # limits recursive functions, see 'man bash'

# if using X, beep is off
if type xset &> /dev/null; then
    xset b off
fi

# aliases
alias ls='ls --color=auto'
alias ll='ls -lav --ignore=..'   # show long listing of all except ".."
alias l='ls -lav --ignore=.*'   # show long listing but no hidden dotfiles
alias gcc='gcc -Wall'            # I'm a perfectionist

# PATH extensions
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.config/emacs/bin:$PATH"
export PATH="$HOME/.pyenv/bin:$PATH"

# environment variables
# fzf by default uses ripgrep (respects VCSs ignores) and shows dotfiles
export FZF_DEFAULT_COMMAND='rg --files --hidden'    

############################# useful functions #############################
# show git branch at prompt, if git exists
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/ \(.*\)/ (\1)/'
}

export PS1="\[\033[01;32m\][\u@\h\[\033[01;37m\] \W\[\033[33m\]\$(parse_git_branch)\[\033[01;32m\]]\$\[\033[00m\] "

# activate pyenv by name
pyactivate() {
    # TODO: FIND A MORE ROBUST WAY OF DOING THIS
    [ -f "$HOME/.virtualenvs/$*" ] && . ~/.virtualenvs/"$*"/bin/activate
}

# env configs
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
[ -f "$HOME/.ghcup/env" ] && . "$HOME/.ghcup/env"

