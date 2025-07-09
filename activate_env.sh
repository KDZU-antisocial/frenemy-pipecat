#!/bin/zsh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "${SCRIPT_DIR}/.venv/bin/activate"

# Preserve existing Oh My Zsh prompt and just add virtual environment indicator
# Only override if not already set by Oh My Zsh
if [[ -z "$ZSH_THEME" ]]; then
    # Fallback prompt if Oh My Zsh is not detected
    autoload -Uz colors && colors
    export PROMPT=$'%F{green}(frenemy-pipecat)%f %1~ %# '
else
    # Oh My Zsh detected - just add virtual environment to existing prompt
    # The virtual environment name will be shown automatically by Oh My Zsh
    echo "Oh My Zsh detected - using existing prompt with virtual environment indicator"
fi

# Print confirmation
echo "Virtual environment activated: $(which python)" 