# Enable colors and git support
autoload -Uz colors && colors
autoload -Uz vcs_info

# Disable the default virtualenv prompt
export VIRTUAL_ENV_DISABLE_PROMPT=1

# Set up git information
precmd() {
    vcs_info
}

# Configure git format
zstyle ':vcs_info:git:*' formats ' %F{blue}(%b)%f'
zstyle ':vcs_info:*' enable git

# Set up virtual environment prompt
function virtualenv_prompt_info() {
    if [[ -n $VIRTUAL_ENV ]]; then
        echo "%F{green}(frenemy-pipecat)%f "
    fi
}

# Set the prompt with git info
setopt PROMPT_SUBST
PROMPT='$(virtualenv_prompt_info)%F{cyan}%1~%f${vcs_info_msg_0_} %F{yellow}%#%f '

# Activate virtual environment if it exists
if [[ -d ".venv" ]]; then
    source .venv/bin/activate
fi 