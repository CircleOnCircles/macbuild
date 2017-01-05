from elite.decorators import elite

from macbuild.macos import macos, default_apps, startup, dock
from macbuild.unix import unix, vim, docker, sshfs, node_js, python
from macbuild.software import sublime_text, spotify, software, native_instruments


@elite(config_path='config', module_search_paths=['library'])
def main(ansible, config):
    # Pre-tasks
    ansible.heading('Preparation')

    ansible.info('Checking sudo rights are available.')
    ansible.command('sudo -nv')

    ansible.info('Update homebrew to the latest version.')
    ansible.homebrew(update_homebrew=True)

    ansible.info('Install Homebrew Cask.')
    ansible.homebrew_tap(tap='caskroom/cask', state='present')

    ansible.info('Setup Homebrew taps.')
    for tap in config.software_brew_taps:
        ansible.homebrew_tap(tap=tap, state='present')

    # Grouped tasks
    ansible.heading('macOS Configuration')
    macos(ansible, config)

    ansible.heading('Sublime Text')
    sublime_text(ansible, config)

    ansible.heading('Spotify')
    spotify(ansible, config)

    ansible.heading('Unix Software')
    unix(ansible, config)

    ansible.heading('Desktop Software')
    software(ansible, config)

    ansible.heading('Native Instruments Software')
    native_instruments(ansible, config)

    ansible.heading('VIM')
    vim(ansible, config)

    ansible.heading('Docker')
    docker(ansible, config)

    ansible.heading('SSHFS')
    sshfs(ansible, config)

    ansible.heading('Node.js')
    node_js(ansible, config)

    ansible.heading('Python')
    python(ansible, config)

    ansible.heading('Default Applications')
    default_apps(ansible, config)

    ansible.heading('Startup Items')
    startup(ansible, config)

    ansible.heading('Dock')
    dock(ansible, config)

    ansible.heading('Summary')
    ansible.summary()


if __name__ == '__main__':
    main()
