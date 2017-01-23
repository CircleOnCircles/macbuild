#!/usr/bin/env python3
from elite.decorators import elite_main

from roles.macos import macos, default_apps, login_items
from roles.unix import unix, vim, docker, sshfs, node_js, python
from roles.software import sublime_text, spotify, software, native_instruments


@elite_main(config_path='config')
def main(elite, config, printer):
    # Pre-tasks
    printer.heading('Preparation')

    printer.info('Checking sudo rights are available.')
    elite.run(command='sudo -nv', changed=False)

    printer.info('Update homebrew to the latest version.')
    elite.brew_update()

    printer.info('Install Homebrew Cask.')
    elite.tap(name='caskroom/cask')

    printer.info('Setup Homebrew taps.')
    for tap in config.software_brew_taps:
        elite.tap(name=tap)

    printer.info('Installing additional fonts.')
    for cask in config.software_brew_cask_fonts:
        elite.cask(name=cask)

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

    printer.heading('Login Items')
    login_items(elite, config, printer)

    # Post-tasks
    printer.heading('Finder Favourites')
    printer.info('Build Finder Favourites layout.')
    elite.favourites(layout=config.favourites_layout)

    printer.heading('Dock')
    printer.info('Build Dock layout.')
    dock = elite.dock(app_layout=config.dock_app_layout, other_layout=config.dock_other_layout)
    if dock.changed:
        elite.run(command='killall Dock', changed=False)

    printer.heading('Launchpad')
    printer.info('Build Launchpad layout.')
    launchpad = elite.launchpad(
        widget_layout=config.launchpad_widget_layout, app_layout=config.launchpad_app_layout
    )
    if launchpad.changed:
        elite.run(command='killall Dock', changed=False)


if __name__ == '__main__':
    main()
