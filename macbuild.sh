#!/bin/bash

# Colours
BOLD='\033[1m'
RED='\033[91m'
GREEN='\033[92m'
BLUE='\033[94m'
ENDC='\033[0m'

# Display a pretty header
echo
echo -e "${BOLD}Mac Build Elite${ENDC}"
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
    echo -e "${BLUE}Installing Homebrew${ENDC}"
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null
fi

# Install Python
if ! brew list python3 > /dev/null 2>&1
then
    echo -e "${BLUE}Installing Python 3.x${ENDC}"
    brew install python3
fi

# Install Python dependencies
for package in \
    PyYAML \
    pyobjc-framework-Cocoa \
    pyobjc-framework-LaunchServices \
    pyobjc-framework-ScriptingBridge \
    rarfile
do
    if ! pip3 show "$package" > /dev/null 2>&1
    then
        echo -e "${BLUE}Installing ${package}${ENDC}"
        pip3 install "$package"
    fi
done

# Perform the build
./build.py

# Disable passwordless sudo after the macbuild is complete
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers
