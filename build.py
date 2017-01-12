#!/usr/bin/env python3
from elite.decorators import elite_main

from roles.macos import macos, default_apps, startup, dock
from roles.unix import unix, vim, docker, sshfs, node_js, python
from roles.software import sublime_text, spotify, software, native_instruments


@elite_main(config_path='config')
def main(elite, config, printer):
    # Pre-tasks
    printer.heading('Preparation')

    printer.info('Checking sudo rights are available.')
    elite.run(command='sudo -nv', changed=False)

    # printer.info('Update homebrew to the latest version.')
    # elite.homebrew(update_homebrew=True)

    printer.info('Install Homebrew Cask.')
    elite.tap(name='caskroom/cask', state='present')

    printer.info('Setup Homebrew taps.')
    for tap in config.software_brew_taps:
        elite.tap(name=tap, state='present')

    printer.info('Installing additional fonts.')
    for cask in config.software_brew_cask_fonts:
        elite.cask(name=cask, state='present')

    # TODO
    # printer.info('Configuring the Terminal.')
    # elite.run(command='./library/terminal.js')

    # Roles
    printer.heading('macOS Configuration')
    macos(elite, config, printer)

    printer.heading('Sublime Text')
    sublime_text(elite, config, printer)

    printer.heading('Spotify')
    spotify(elite, config, printer)

    printer.heading('Unix Software')
    unix(elite, config, printer)

    printer.heading('Desktop Software')
    software(elite, config, printer)

    printer.heading('Native Instruments Software')
    native_instruments(elite, config, printer)

    printer.heading('VIM')
    vim(elite, config, printer)

    printer.heading('Docker')
    docker(elite, config, printer)

    printer.heading('SSHFS')
    sshfs(elite, config, printer)

    printer.heading('Node.js')
    node_js(elite, config, printer)

    printer.heading('Python')
    python(elite, config, printer)

    printer.heading('Default Applications')
    default_apps(elite, config, printer)

    printer.heading('Startup Items')
    startup(elite, config, printer)

    printer.heading('Dock')
    dock(elite, config, printer)

    # # Post-tasks
    # printer.heading('Launchpad')
    # printer.info('Configuring Launchpad and Dashboard apps and widgets.')
    # elite.run(command='./library/launchpad.py build config/launchpad.yaml')

    # Summary
    printer.heading('Summary')
    elite.summary()


if __name__ == '__main__':
    main()
