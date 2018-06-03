#!/usr/bin/env python3
from elite.decorators import elite_main


@elite_main(config_path='config', config_order=['global.yaml', 'software', 'software.yaml'])
def main(elite, config, printer):
    printer.heading('Initialization')

    printer.info('Sudo')
    elite.run(command='sudo -nv', changed=False)

    printer.info('Music Software Source')
    music_software_source = config.music_software_source
    if music_software_source:
        env = {'HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR': music_software_source}
        elite.info(message=f'using music software software {music_software_source}')
    else:
        env = {}
        elite.fail(message='unable to find any suitable music software source', ignore_failed=True)

    printer.info('Homebrew Update')
    elite.brew_update()

    printer.info('macOS System')
    timezone = config.macos_system['timezone']
    computer_sleep_time = config.macos_system['computer_sleep_time']
    display_sleep_time = config.macos_system['display_sleep_time']

    elite.system_setup(
        timezone=timezone,
        computer_sleep_time=computer_sleep_time,
        display_sleep_time=display_sleep_time,
        sudo=True
    )

    local_host_name = config.macos_system['local_host_name']
    computer_name = config.macos_system['computer_name']

    elite.hostname(
        local_host_name=local_host_name, computer_name=computer_name, sudo=True
    )

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
            tap = software.pop('tap', None)
            if tap:
                taps = tap if isinstance(tap, list) else [tap]
                for tap in taps:
                    elite.tap(name=tap)

            # App store apps
            appstore = software.pop('appstore', None)
            if appstore:
                appstores = appstore if isinstance(appstore, list) else [appstore]
                for appstore in appstores:
                    app_file = elite.file_info(
                        path=f'/Applications/{appstore}.app/Contents/_MASReceipt/receipt'
                    )
                    if not app_file.exists:
                        elite.fail(
                            message=f'Please install {appstore} from the App Store',
                            ignore_failed=True
                        )

            # Cask packages
            cask = software.pop('cask', None)
            cask_install_failed = False
            if cask:
                casks = cask if isinstance(cask, list) else [cask]
                for cask in casks:
                    cask_install = elite.cask(
                        name=cask, env=env, ignore_failed=True, state='latest'
                    )
                    if not cask_install.ok:
                        cask_install_failed = True
                        break

            if cask_install_failed:
                continue

            # Brew packages
            brew = software.pop('brew', None)
            if brew:
                brews = brew if isinstance(brew, list) else [brew]
                for brew in brews:
                    elite.brew(name=brew, state='latest')

            # Python pip packages
            pip = software.pop('pip', None)
            if pip:
                pips = pip if isinstance(pip, list) else [pip]
                for pip in pips:
                    elite.pip(name=pip, state='latest', executable='pip3')

            # Ruby gem packages
            gem = software.pop('gem', None)
            if gem:
                gems = gem if isinstance(gem, list) else [gem]
                for gem in gems:
                    elite.gem(name=gem, state='latest')

            # Files
            file = software.pop('file', None)
            if file:
                files = file if isinstance(file, list) else [file]
                for file in files:
                    elite.file(
                        path=file['path'],
                        source=file.get('source'),
                        state=file.get('state', 'file'),
                        mode=file.get('mode'),
                        owner=file.get('owner'),
                        group=file.get('group'),
                        flags=file.get('flags'),
                        sudo=file.get('sudo', False)
                    )

            # Dowlnoads
            download = software.pop('download', None)
            if download:
                downloads = download if isinstance(download, list) else [download]
                for download in downloads:
                    elite.download(path=download['path'], url=download['url'])

            # Git repositories
            git = software.pop('git', None)
            if git:
                gits = git if isinstance(git, list) else [git]
                for git in gits:
                    elite.git(path=git['path'], repo=git['repo'])

            # Symbolic links
            symlink = software.pop('symlink', None)
            if symlink:
                symlinks = symlink if isinstance(symlink, list) else [symlink]

                for symlink in symlinks:
                    symlink_health = elite.file_info(path=symlink['path'])
                    if symlink_health.exists and symlink_health.file_type != 'symlink':
                        elite.file(path=symlink['path'], state='absent')
                    elite.file(path=symlink['path'], source=symlink['source'], state='symlink')

            # plist settings
            plist = software.pop('plist', None)
            if plist:
                plists = plist if isinstance(plist, list) else [plist]
                for plist in plists:
                    elite.plist(
                        domain=plist.get('domain'),
                        container=plist.get('container'),
                        path=plist.get('path'),
                        source=plist.get('source'),
                        values=plist.get('values', {}),
                        sudo=plist.get('sudo', False)
                    )

            # JSON settings
            json = software.pop('json', None)
            if json:
                jsons = json if isinstance(json, list) else [json]
                for json in jsons:
                    elite.json(path=json.get('path'), values=json.get('values'))

            # Application Specific Actions
            if name == 'Spotify':
                global_settings = software.pop('global_settings')
                username = software.pop('username')
                user_settings = software.pop('user_settings')

                for pref, value in global_settings.items():
                    elite.spotify_pref(pref=pref, value=value, mode='0644')

                for pref, value in user_settings.items():
                    elite.spotify_pref(pref=pref, value=value, username=username, mode='0644')

            elif name == 'Native Instruments Kontakt 5':
                library_order = software.pop('library_order')

                for index, library in enumerate(library_order):
                    elite.plist(
                        domain=f'com.native-instruments.{library}',
                        values={'UserListIndex': index},
                        mode='0600'
                    )

            # File handlers
            handler = software.pop('handler', None)
            if handler:
                handlers = handler if isinstance(handler, list) else [handler]
                for handler in handlers:
                    elite.handler(path=f'/Applications/{app}.app', content_type=handler)

            # Login items
            login_item = software.pop('login_item', None)
            if login_item is not None:
                elite.login_item(
                    path=f'/Applications/{app}.app', state='present' if login_item else 'absent'
                )

            # Verify that no extra keys remain after processing a piece of software
            if software:
                elite.fail(
                    message=(
                        'the software item contained unsupported keys {list(software.keys())}'
                    ),
                    ignore_failed=True
                )

    printer.info('cfprefsd Restart')
    elite.run(command='killall cfprefsd', ignore_failed=True, changed=False)

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
        elite.run(command='killall Dock', changed=False)


if __name__ == '__main__':
    main()
