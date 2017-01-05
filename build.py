#!/usr/bin/env python3
from elite.decorators import elite

from roles.macos import macos, default_apps, startup, dock
from roles.unix import unix, vim, docker, sshfs, node_js, python
from roles.software import sublime_text, spotify, software, native_instruments


@elite(config_path='config', module_search_paths=['library'])
def main(ansible, config, printer):
    # Pre-tasks
    printer.heading('Preparation')

    printer.info('Checking sudo rights are available.')
    ansible.command('sudo -nv')

    printer.info('Update homebrew to the latest version.')
    ansible.homebrew(update_homebrew=True)

    printer.info('Install Homebrew Cask.')
    ansible.homebrew_tap(tap='caskroom/cask', state='present')

    printer.info('Setup Homebrew taps.')
    for tap in config.software_brew_taps:
        ansible.homebrew_tap(tap=tap, state='present')

    printer.info('Installing additional fonts.')
    for cask in config.software_brew_cask_fonts:
        ansible.homebrew_cask(name=cask, state='present')

    printer.info('Configuring the Terminal.')
    ansible.command('./library/terminal.js')

    # Roles
    printer.heading('macOS Configuration')
    macos(ansible, config, printer)

    printer.heading('Sublime Text')
    sublime_text(ansible, config, printer)

    printer.heading('Spotify')
    spotify(ansible, config, printer)

    printer.heading('Unix Software')
    unix(ansible, config, printer)

    printer.heading('Desktop Software')
    software(ansible, config, printer)

    printer.heading('Native Instruments Software')
    native_instruments(ansible, config, printer)

    printer.heading('VIM')
    vim(ansible, config, printer)

    printer.heading('Docker')
    docker(ansible, config, printer)

    printer.heading('SSHFS')
    sshfs(ansible, config, printer)

    printer.heading('Node.js')
    node_js(ansible, config, printer)

    printer.heading('Python')
    python(ansible, config, printer)

    printer.heading('Default Applications')
    default_apps(ansible, config, printer)

    printer.heading('Startup Items')
    startup(ansible, config, printer)

    printer.heading('Dock')
    dock(ansible, config, printer)

    # Post-tasks
    printer.heading('Launchpad')
    printer.info('Configuring Launchpad and Dashboard apps and widgets.')
    ansible.command('./library/launchpad.py build config/launchpad.yaml')

    # Summary
    printer.heading('Summary')
    ansible.summary()


if __name__ == '__main__':
    main()
