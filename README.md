# Mac Build Elite

![License](https://img.shields.io/badge/license-Proprietary-blue.svg)

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
cd macbuild
./macbuild.sh
```

It is suggested that you reboot your Mac after the first run of this tool.

## Bugs & Issues

* The Source Code Pro Terminal font is not available when first referenced
* Spell check appears to still be enabled in Safari
* The iLok update state will need to be verified and updated if necessary
* BetterSnapTool keyboard shortcut of Ctrl+Alt+Cmd+Up seems to mute conversations in Skype
* Spotify settings should be improved to be like plist and JSON
* Homebrew update is very slow (could performing a full tap help this?)
* Native Instruments Kontakt permissions appear to be boned for Service Center activations

    ```bash
    sudo chown root:admin "/Library/Application Support/Native Instruments/Service Center"
    sudo chmod 775 "/Library/Application Support/Native Instruments/Service Center"
    ```

## Manual Tasks

The following tasks must be performed manually.

### Installation & Configuration (macOS)

* **Screen Resolution & Layout**: Set your screen resolution and configure multi-monitor setup
* **Wallpaper**: Choose your wallpaper
* **Screen Saver**: Set the screen saver to 'Flurry'
* **Notification Centre**: Set the order of items and allow permission after starting iStat Mini
* **Safari**: Install extensions (1Password and Adblock Plus)
* **App Store Login Items**: Start App Store menubar apps and set them to start
  at login (OneDrive)
* **Keyboard Shortcuts**: Under System Preferences / Keyboard:
    - Set 'Show Launchpad' to F14 under 'Launchpad & Dock'
    - Set 'Show Notification Center' to F15 under 'Mission Control'
    - Set 'Show Desktop' to F13 under 'Mission Control'
    - Disable 'Show Dashboard' under 'Mission Control'
* **Menu Bar**: Add Sound and Time Machine icons to the menu bar
* **Time Machine**: Configure Time Machine backup drive
* **Dictation**: You may need to disable this as holding down Fn suggests it

### Installation & Configuration (General)

* **Apple iWork**: Launch Pages, Keynote and Numbers and dismiss the welcome
  screen
* **Audio Hijack**: Start the app multiple times to dismiss welcome and mailing
  list alerts and install Instant On
* **Clear**: Enable iCloud in Preferences
* **iTunes**; Start iTunes and set it up
* **Dropbox**: Disable camera uploads and disable email integration
* **Forklift**: Sidebar containing favourites and view settings
* **Cog**: Disable notifications
* **LennarDigital Sylenth1**: Set the default skin
* **DMG Audio EQuality**: Set defaults by switching knobs to input boxes
* **DMG Audio EQuilibrium**: Set the default Cubase preset to the default for the plugin too
* **Klanghelm VUMT**: Set the default skin and interface size
* **Native Instruments Kontakt**: Configure Quickload if you like

### Installation & Configuration (Music Production)

* **Steinberg Cubase Pro**: Preferences and key bindings

### Manual Licensing

* **Forklift**
* **Microsoft Office**
* **Cytomic The Drop & The Glue**
* **LennarDigital Sylenth1**
* **Native Instruments Komplete**
* **Native Instruments Kontakt Sample Libraries**
* **Novation Bass Station**

## Software Deactivation

The following software should be deactivated before re-installing macOS:

* **Celemony Melodyne Editor**
* **LennarDigital Sylenth1**

## License

Mac Build is proprietary software and may not be copied and/or distributed
without the express written permission of Fotis Gimian.
