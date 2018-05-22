#!/usr/bin/env bash

# Avoid duplicates in history
export HISTCONTROL=ignoredups

# Set a more reasonable bash history limit
export HISTSIZE=50000

# Source all scripts from bash_profile.d
if [[ -d ~/.bash_profile.d ]]
then
  for i in ~/.bash_profile.d/*.sh
  do
    # shellcheck source=/dev/null
    source "$i"
  done
fi
