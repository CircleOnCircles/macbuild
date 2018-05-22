#!/usr/bin/env bash

# Shortcut to listing files in long format
alias ll='ls -l'

# macOS long file listing including all special attributes
# @ shows extended attributes which can be cleared via `xattr -d`
# e shows ACLs which can be cleared via `chmod -N`
alias lo='ls -l@Oe'
