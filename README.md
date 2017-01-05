# Mac Build Elite

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

## Manual Tasks

The following tasks must be performed manually.

### Installation & Configuration (macOS)

* **Finder**: Setup sidebar containing favourites
* **Services**: In System Preferences / Keyboard / Services, enable 'New Terminal at Folder' and 'New Terminal Tab at Folder'
* **Screen Saver**: Set the screen saver to 'Flurry'
* **Notification Centre**: Set the order of items and allow permission
* **Safari**: Install extensions (1Password and Adblock Plus)
* **App Store Login Items**: Start App Store menubar apps and set them to start
  at login (AppCleaner and OneDrive)
* **Keyboard Shortcuts**: Under System Preferences / Keyboard:
    - Set 'Show Launchpad' to F14 under 'Launchpad & Dock'
    - Set 'Show Notification Center' to F15 under 'Mission Control'
    - Set 'Show Desktop' to F13 under 'Mission Control'
    - Disable 'Show Dashboard' under 'Mission Control'

### Installation & Configuration (General)

* **Audio Hijack**: Start the app multiple times to dismiss welcome and mailing
  list alerts.  You must also install Instant On to ensure the app works.
* **Clear**: Enable iCloud
* **Focus**: Start Focus manually as it won't initialise successfully with
  launchd starting it for the first time.
* **Dropbox**: Disable camera uploads
* **Forklift**: Sidebar containing favourites and view settings
* **World Clock**: Country selection settings

### Installation & Configuration (Music Production)

* **Ableton Live Suite**: Preferences including skin selection
* **Ableton Sample Packs**: Installation of Ableton Live sounds
* **Apple Logic Pro X**: Preferences and key bindings
* **Steinberg Cubase Pro**: Preferences and key bindings
* **Default Plug-in Presets**: Setup default presets for your most used VST
  effects and instruments

### Manual Licensing

* **Microsoft Office**
* **Cytomic The Drop & The Glue**
* **LennarDigital Sylenth1**
* **Native Instruments Komplete**
* **Novation Bass Station**

## Software Deactivation

The following software should be deactivated before re-installing macOS:

* **Celemony Melodyne Editor**
* **LennarDigital Sylenth1**
