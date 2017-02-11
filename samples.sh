#!/bin/bash

# Colours
BOLD='\033[1m'
RED='\033[91m'
GREEN='\033[92m'
BLUE='\033[94m'
ENDC='\033[0m'

# Display a pretty header
echo
echo -e "${BOLD}Sample Library Installation${ENDC}"
echo

# Prompt the user for their sudo password
if sudo -nv 2> /dev/null
then
    echo -e "${GREEN}Using existing sudo session.${ENDC}"
else
    sudo -v -p "Enter your sudo password: "
fi

# Enable passwordless sudo for the macbuild run
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) NOPASSWD: ALL/" /etc/sudoers

# Install Homebrew
if ! which brew > /dev/null 2>&1
then
    echo -e "${RED}Please run Mac Build before installing sample libraries${ENDC}"
    exit 1
fi

# Perform the build
python3 samples.py

# Disable passwordless sudo after the macbuild is complete
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers
