from elite.print import heading
from elite.decorators import elite

from macbuild.macos import macos, default_apps, startup, dock
from macbuild.unix import unix, vim, docker, sshfs, node_js, python
from macbuild.software import sublime_text, spotify, software, native_instruments


@elite(config_path='config', module_search_paths=['library'])
def main(ansible, config):
    # Pre-tasks
    heading('Update homebrew to the latest version.')
    ansible.homebrew(update_homebrew=True)

    heading('Install Homebrew Cask.')
    ansible.homebrew_tap(tap='caskroom/cask', state='present')

    heading('Setup Homebrew taps')
    for tap in config.software_brew_taps:
        ansible.homebrew_tap(tap=tap, state='present')

    # Grouped tasks
    heading('macOS Configuration')
    macos(ansible, config)

    heading('Install important desktop applications.')
    sublime_text(ansible, config)
    spotify(ansible, config)

    heading('Unix software installation and configuration.')
    unix(ansible, config)

    heading('Desktop software installation and configuration.')
    software(ansible, config)

    heading('Configure Native Instruments software.')
    native_instruments(ansible, config)

    heading('Install and configure Unix software.')
    vim(ansible, config)
    docker(ansible, config)
    sshfs(ansible, config)

    heading('Install and configure programming languages.')
    node_js(ansible, config)
    python(ansible, config)

    heading('Configure default applications.')
    default_apps(ansible, config)

    heading('Configure startup items.')
    startup(ansible, config)

    heading('Configure the Dock.')
    dock(ansible, config)


if __name__ == '__main__':
    main()
