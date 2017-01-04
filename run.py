import os
from pprint import pprint

from elite.ansible import Ansible
from elite.print import header, footer, heading, progress
from elite.config import Config


def main():
    try:
        # Setup Ansible and our configuration
        ansible = Ansible(callback=progress)
        config = Config(os.path.join(os.path.dirname(__file__), 'config'))

        # Main header
        header()

        heading('Installing Homebrew casks')

        for cask in config.software_brew_casks:
            ansible.homebrew_cask(name=cask, state='present')

        heading('Setting up the world through grapevines.')

        ansible.command('ls -l /')
        ansible.command('id')
        with ansible.settings(sudo=True):
            ansible.command('id')
        ansible.command('sleep 2')

        heading('Creating required filepaths.')

        for path in ['/etc/foo.conf', '/Users/fots/foo.conf']:
            ansible.file(path=path, state='touch')

    except KeyboardInterrupt:
        print()

    finally:
        # Main footer
        footer()


if __name__ == '__main__':
    main()
