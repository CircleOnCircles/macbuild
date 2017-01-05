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
sudo -v

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

# Install Ansible (using pip is the officially supported way)
if ! pip3 show ansible > /dev/null 2>&1
then
    echo -e "${BLUE}Installing Ansible${ENDC}"
    # TODO: switch back to pip when Ansible 2.2.1.0 is released
    # pip3 install ansible
    pip3 install https://releases.ansible.com/ansible/ansible-2.2.1.0-0.2.rc2.tar.gz
fi

# Setup the source of music production software from the backup drive attached
if [ -d "/Volumes/Backup Mac 1" ]
then
  export HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR='/Volumes/Backup Mac 1/Software/Music Production'
elif [ -d "/Volumes/Backup Mac 2" ]
then
  export HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR='/Volumes/Backup Mac 2/Software/Music Production'
fi

if [ ! -z "$HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR" ]
then
  echo -e "${GREEN}Using cask music software basedir of ${HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR}${ENDC}"
else
  echo -e "${RED}Unable to find the music software basedir${ENDC}"
fi

# Perform the build
./build.py

# Disable passwordless sudo after the macbuild is complete
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers
