# Enable colors
autoload -Uz colors && colors

# Disable the default virtualenv prompt
export VIRTUAL_ENV_DISABLE_PROMPT=1

# Set up virtual environment prompt
function virtualenv_prompt_info() {
    if [[ -n $VIRTUAL_ENV ]]; then
        echo "%F{green}(frenemy-pipecat)%f "
    fi
}

# Set the prompt
setopt PROMPT_SUBST
PROMPT='$(virtualenv_prompt_info)%1~ %# '

# Activate virtual environment if it exists
if [[ -d ".venv" ]]; then
    source .venv/bin/activate
fi 