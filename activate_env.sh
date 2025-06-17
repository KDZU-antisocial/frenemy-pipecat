#!/bin/zsh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "${SCRIPT_DIR}/.venv/bin/activate"

# Customize the prompt to show the virtual environment name
export PROMPT='%F{green}(frenemy-pipecat)%f %1~ %# '

# Print confirmation
echo "Virtual environment activated: $(which python)" 