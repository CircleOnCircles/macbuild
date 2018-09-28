#!/usr/bin/env python3
from elite import Config, automate


def software_config(software, key):
    key = software.pop(key, [])
    return key if isinstance(key, list) else [key]


@automate()
def main(elite, printer):
    printer.heading('Preparation')

    printer.info('Homebrew Update')
    elite.brew_update()

    fonts_config = Config('config/fonts.yaml')

    # TODO: Improve this ugly thing
    printer.info('Fonts')
    for tap in software_config(fonts_config.config, 'tap'):
        elite.tap(name=tap)

    for cask in software_config(fonts_config.config, 'cask'):
        elite.cask(name=cask, state='latest')

    config = Config('config/software.yaml')

    printer.info('App License Directory')
    app_license_dir = config.globals['app_license_dir']
    app_license_dir_health = elite.file_info(app_license_dir)
    if app_license_dir_health.data['exists']:
        elite.info(message=f'using app license directory {app_license_dir}')
    else:
        elite.fail(message='unable to find the app license directory')

    printer.info('Music Software Source')
    music_software_source = config.globals['music_software_source']
    if music_software_source:
        env = {'HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR': music_software_source}
        elite.info(message=f'using music software source {music_software_source}')
    else:
        env = {}
        with elite.options(ignore_failed=True):
            elite.fail(message='unable to find any suitable music software source')

    printer.heading('macOS')

    printer.info('macOS System')
    timezone = config.macos_system['timezone']
    computer_sleep_time = config.macos_system['computer_sleep_time']
    display_sleep_time = config.macos_system['display_sleep_time']

    with elite.options(sudo=True):
        elite.system_setup(
            timezone=timezone,
            computer_sleep_time=computer_sleep_time,
            display_sleep_time=display_sleep_time
        )

    local_host_name = config.macos_system['local_host_name']
    computer_name = config.macos_system['computer_name']

    with elite.options(sudo=True):
        elite.hostname(local_host_name=local_host_name, computer_name=computer_name)

    for group, software_items in config.software.items():
        # Print the software group heading
        printer.heading(group)

        for software in software_items:
            # Avoid modifying the original config
            software = software.copy()

            # Obtain and print the software name
            try:
                name = software.pop('name')
                printer.info(name)
            except KeyError:
                elite.fail(message=f'the software item {software} has no name')

            # Obtain the app name (as found under /Applications)
            app = software.pop('app', name)

            # Taps
            for tap in software_config(software, 'tap'):
                elite.tap(name=tap)

            # App store apps
            for appstore in software_config(software, 'appstore'):
                app_file_health = elite.file_info(
                    path=f'/Applications/{appstore}.app/Contents/_MASReceipt/receipt'
                )
                if not app_file_health.data['exists']:
                    with elite.options(ignore_failed=True):
                        elite.fail(message=f'please install {appstore} from the App Store')

            # Cask packages
            cask_install_failed = False
            for cask in software_config(software, 'cask'):
                with elite.options(env=env, ignore_failed=True):
                    cask_install = elite.cask(name=cask, state='latest')
                    if not cask_install.ok:
                        cask_install_failed = True

            if cask_install_failed:
                continue

            # Brew packages
            for brew in software_config(software, 'brew'):
                elite.brew(name=brew, state='latest')

            # Python pip packages
            for pip in software_config(software, 'pip'):
                elite.pip(name=pip, state='latest', executable='pip3')

            # Ruby gem packages
            for gem in software_config(software, 'gem'):
                elite.gem(name=gem, state='latest')

            # Files
            for file in software_config(software, 'file'):
                with elite.options(sudo=file.get('sudo', False)):
                    elite.file(
                        path=file['path'],
                        source=file.get('source'),
                        state=file.get('state', 'file'),
                        mode=file.get('mode'),
                        owner=file.get('owner'),
                        group=file.get('group'),
                        flags=file.get('flags')
                    )

            # Dowlnoads
            for download in software_config(software, 'download'):
                elite.download(path=download['path'], url=download['url'])

            # Git repositories
            for git in software_config(software, 'git'):
                elite.git(path=git['path'], repo=git['repo'])

            # Symbolic links
            for symlink in software_config(software, 'symlink'):
                symlink_health = elite.file_info(path=symlink['path'])
                if symlink_health.data['exists'] and symlink_health.data['file_type'] != 'symlink':
                    elite.file(path=symlink['path'], state='absent')
                elite.file(path=symlink['path'], source=symlink['source'], state='symlink')

            # plist settings
            for plist in software_config(software, 'plist'):
                with elite.options(sudo=plist.get('sudo', False)):
                    elite.plist(
                        domain=plist.get('domain'),
                        container=plist.get('container'),
                        path=plist.get('path'),
                        source=plist.get('source'),
                        values=plist.get('values', {})
                    )

            # JSON settings
            for json in software_config(software, 'json'):
                elite.json(path=json.get('path'), values=json.get('values'))

            # TODO: Remove all application specific actions
            if name == 'Spotify':
                username = software.pop('username')
                global_settings = software.pop('global_settings', {})
                user_settings = software.pop('user_settings', {})

                elite.spotify(values=global_settings, mode='0644')
                elite.spotify(values=user_settings, username=username, mode='0644')

            elif name == 'Native Instruments Kontakt 5':
                library_order = software.pop('library_order')

                for index, library in enumerate(library_order):
                    elite.plist(
                        domain=f'com.native-instruments.{library}',
                        values={'UserListIndex': index},
                        mode='0600'
                    )

            # File handlers
            for handler in software_config(software, 'handler'):
                elite.handler(path=f'/Applications/{app}.app', content_type=handler)

            # Login items
            login_item = software.pop('login_item', None)
            # TODO: Determine what we will do about login items in Mojave
            # if login_item is not None:
            #     elite.login_item(
            #         path=f'/Applications/{app}.app', state='present' if login_item else 'absent'
            #     )

            # Verify that no extra keys remain after processing a piece of software
            if software:
                with elite.options(ignore_failed=True):
                    elite.fail(
                        message=(
                            f'the software item contained unsupported keys {list(software.keys())}'
                        )
                    )

    printer.info('cfprefsd Restart')
    with elite.options(ignore_failed=True, changed=False):
        elite.run(command=['killall', 'cfprefsd'])

    # Build the Dock and Launchpad layouts
    printer.heading('macOS Dock & Launchpad')

    printer.info('Dock')
    dock = elite.dock(
        app_layout=config.dock_layout['apps'],
        other_layout=config.dock_layout['other'],
        mode='0600'
    )

    printer.info('Launchpad')
    launchpad = elite.launchpad(
        widget_layout=config.launchpad_layout['widgets'],
        app_layout=config.launchpad_layout['apps']
    )

    if dock.changed or launchpad.changed:
        printer.info('Dock Restart')
        with elite.options(changed=False):
            elite.run(command=['killall', 'Dock'])


if __name__ == '__main__':
    # Disabling parameter checks as pylint has a bug with relation to decorators
    # https://github.com/PyCQA/pylint/issues/259
    main()  # pylint: disable=no-value-for-parameter
