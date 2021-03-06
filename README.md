# Mac Build (using Elite)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/fgimian/macbuild/blob/master/LICENSE)

![Mac Build Logo](https://raw.githubusercontent.com/fgimian/macbuild/master/images/macbuild-logo.png)

Artwork courtesy of [Apple](http://www.apple.com)

## Quick Start

You may wish to perform the following steps to save time and ensure everything
works as expected:

1. Copy a Homebrew cache backup to `~/Library/Caches/Homebrew`
2. Copy App Store apps that you have previously downloaded to `/Applications`
3. Copy `System Automation` containing various settings and licenses to `~/Documents`
4. Ensure your SSH keys are present in `~/.ssh`

Now, run the following in your Terminal to use my configuration:

```bash
git clone git@github.com:fgimian/macbuild.git
git clone git@github.com:fgimian/elite.git
cd macbuild
ln -s ../elite/elite
./setup.sh
sudo ./macbuild.py
```

It is suggested that you reboot your Mac after the first run of this tool.

## Bugs & Issues

* The iLok update state will need to be verified and updated if necessary
* BetterSnapTool keyboard shortcut of Ctrl+Alt+Cmd+Up seems to mute conversations in Skype

## Manual Tasks

The following tasks must be performed manually.

### Installation & Configuration (macOS)

* **Screen Resolution & Layout**: Set your screen resolution and configure multi-monitor setup
* **Finder**: Configure favourites in the sidebar as follows:
    - Recents
    - AirDrop
    - Dropbox
    - Applications
    - fots
    - Desktop
    - Documents
    - Downloads
    - Movies
    - Music
    - Pictures
* **Wallpaper**: Choose your wallpaper
* **Screen Saver**: Set the screen saver to 'Flurry'
* **Audio Device**: Set the audio interface as the default Sound device
* **Spell Checking**: System Preferences / Keyboard / Text / Disable 'Correct spelling 
  automatically', 'Capitalize words automatically' and 'Add period with double-space'
* **Notification Centre**: Set the order of items and allow permission after starting iStat Mini and OTP Auth as follows:
    - Weather
    - iStat Mini
    - OTP Auth
    - Calendar
    - Tomorrow
* **Safari**: Install extension 1Password
* **Keyboard Shortcuts**: Under System Preferences / Keyboard / Shortcuts:
    - Set 'Show Launchpad' to F14 under 'Launchpad & Dock'
    - Set 'Show Notification Center' to F15 under 'Mission Control'
    - Set 'Show Desktop' to F13 under 'Mission Control'
    - Disable 'Show Dashboard' under 'Mission Control'
* **Time Machine**: Configure Time Machine backup drive ensuring that you add an exclusion for 
  ~/Documents/Virtual Machines.localized
* **Dictation**: You may need to disable this as holding down Fn suggests it

### Installation & Configuration (General)

* **Audio Hijack**: Start the app multiple times to dismiss welcome and mailing list alerts and
  install ACE
* **iTunes**; Start iTunes and set it up
* **Dropbox**: Disable camera uploads
* **Forklift**: Sidebar containing favourites and view settings
* **Cog & News**: Disable notifications
* **Textual**: Right click on freenode and select Server Properties; under Basic Settings / 
  General, enter your Server Password (NickServ password)
* **FaceTime**: Change the ringtone in Preferences / General to Radiate
* **Messages**: Disable spell checking under Edit / Spelling and Grammar, and change the message 
  receive sound under Preferences / General to Chord
* **LennarDigital Sylenth1**: Set the default skin to Apox and Size to 110%
* **DMG Audio EQuality**: Set defaults by switching knobs to input boxes
* **DMG Audio EQuilibrium**: Set the default Cubase preset to the default for the plugin too
* **Native Instruments Kontakt**: Configure Quickload if you like
* **Sonalksis**: Open Sonalksis Plugin Manager and sign in to register plugins

### Installation & Configuration (Music Production)

* **Steinberg Cubase Pro**: Preferences and key bindings

### Manual Licensing

* **Forklift**
* **Microsoft Office**
* **Cytomic The Drop & The Glue**
* **LennarDigital Sylenth1**
* **Modartt Pianoteq**
* **Native Instruments Komplete**
* **Native Instruments Kontakt Sample Libraries**

## Software Deactivation & Backups

The following software should be deactivated before re-installing macOS:

* **Celemony Melodyne Editor**
* **LennarDigital Sylenth1**

## License

Mac Build is released under the MIT license.  Please see the
[LICENSE](https://github.com/fgimian/macbuild/blob/master/LICENSE) file for more details.
