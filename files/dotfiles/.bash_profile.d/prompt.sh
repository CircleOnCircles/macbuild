#!/usr/bin/env bash
# shellcheck disable=SC2034

# Colours
BOLD="\[\e[1m\]"

BLACK="\[\e[0;30m\]"
RED="\[\e[0;31m\]"
GREEN="\[\e[0;32m\]"
BROWN="\[\e[0;33m\]"
BLUE="\[\e[0;34m\]"
PURPLE="\[\e[0;35m\]"
CYAN="\[\e[0;36m\]"

BRIGHT_RED="\[\e[1;31m\]"
BRIGHT_GREEN="\[\e[1;32m\]"
BRIGHT_BROWN="\[\e[1;33m\]"
BRIGHT_BLUE="\[\e[1;34m\]"
BRIGHT_PURPLE="\[\e[1;35m\]"
BRIGHT_CYAN="\[\e[1;36m\]"

ENDC="\[\e[m\]"

_prompt_parent_dir()
{
  local working_dir
  local parent_dir

  # Obtain the working directory
  working_dir=$1

  # If we are in the user's home directory or /, there's no parent directory
  # that needs to be displayed
  if [[ $working_dir == "~" || $working_dir == "/" ]]
  then
    return
  fi

  # Obtain the parent directory
  parent_dir=$(dirname "$1")

  # Substitute the home directory with ~
  parent_dir="${parent_dir/#$HOME\//~/}"

  # Replace ellipsis with a shorter unicode representation
  parent_dir="${parent_dir/\/...\///…/}"

  # Remove the leading / if necessary as it is not required for display
  parent_dir="${parent_dir/#\//}"

  # Display the parent directory in a pretty format
  if [[ $parent_dir != "" ]]
  then
    echo "${parent_dir//\// > } > "
  fi
}

_prompt_virtualenv()
{
  if [[ ! -z $VIRTUAL_ENV ]]
  then
    virtualenv=$(basename "$VIRTUAL_ENV")
    echo "@${virtualenv} "
  fi
}

# User
PS1="${GREEN}\u ${ENDC}"

# Virtualenv
PS1+="${BOLD}\$(_prompt_virtualenv)${ENDC}"

# Parent directory
PS1+="${BRIGHT_BLUE}\$(_prompt_parent_dir '\w')${ENDC}"

# Current directory
PS1+="${YELLOW}\W${ENDC} "

# Prompt
PS1+="\$ "

# Export our prompt
export PS1

# Disable virtualenv prompt manipulation
export VIRTUAL_ENV_DISABLE_PROMPT=1

# Display ellipsis when deeper than 3 directories
export PROMPT_DIRTRIM=3
