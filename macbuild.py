#!/usr/bin/env python3
from elite.decorators import elite_main


def set_macos_settings(elite, timezone, computer_sleep_time, display_sleep_time):
    current_timezone = elite.run(command='systemsetup -gettimezone', sudo=True, changed=False)
    if f'Time Zone: {timezone}' != current_timezone.stdout.rstrip():
        elite.run(command=f'systemsetup -settimezone {timezone}', sudo=True)

    computer_sleep = elite.run(command='systemsetup -getcomputersleep', sudo=True, changed=False)
    if (
        f'Computer Sleep: {computer_sleep_time}' !=
        computer_sleep.stdout.rstrip().replace('after ', '').replace('minutes', '')
    ):
        elite.run(
            command=f'systemsetup -setcomputersleep {computer_sleep_time}', sudo=True
        )

    display_sleep = elite.run(command='systemsetup -getdisplaysleep', sudo=True, changed=False)
    if (
        f'Display Sleep: {display_sleep_time}' !=
        display_sleep.stdout.rstrip().replace('after ', '').replace('minutes', '')
    ):
        elite.run(
            command=f'systemsetup -setdisplaysleep {display_sleep_time}', sudo=True
        )


def set_macos_hostname(elite, local_host_name, computer_name):
    current_local_host_name = elite.run(
        command='scutil --get LocalHostName', sudo=True, changed=False
    )
    if local_host_name != current_local_host_name.stdout.rstrip():
        elite.run(command=f'scutil --set LocalHostName "{local_host_name}"', sudo=True)

    current_computer_name = elite.run(
        command='scutil --get ComputerName', sudo=True, changed=False
    )
    if computer_name != current_computer_name.stdout.rstrip():
        elite.run(command=f'scutil --set ComputerName "{computer_name}"', sudo=True)


@elite_main(
    config_path='config',
    config_order=['global.yaml', 'software', 'software.yaml']
)
def main(elite, config, printer):
    printer.heading('Initialization')

    printer.info('Sudo')
    elite.run(command='sudo -nv', changed=False)

    printer.info('Music Software Source')
    for music_software_source in config.music_software_sources:
        source_dir = elite.file_info(path=music_software_source)
        if source_dir.file_type == 'directory':
            env = {'HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR': music_software_source}
            break
    else:
        env = {}
        elite.fail(
            message='unable to find any suitable music software source', ignore_failed=True
        )

    printer.info('Homebrew Update')
    elite.brew_update()

    restart_dock = False

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
            if cask:
                casks = cask if isinstance(cask, list) else [cask]
                for cask in casks:
                    cask_install = elite.cask(name=cask, env=env, ignore_failed=True)
                    if not cask_install.ok:
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
                        values=plist.get('values'),
                        sudo=plist.get('sudo', False)
                    )

            # JSON settings
            json = software.pop('json', None)
            if json:
                jsons = json if isinstance(json, list) else [json]
                for json in jsons:
                    elite.json(
                        path=json.get('path'),
                        values=json.get('values')
                    )

            # Application SpecificActions
            if name == 'macOS General':
                timezone = software.pop('timezone')
                computer_sleep_time = software.pop('computer_sleep_time')
                display_sleep_time = software.pop('display_sleep_time')

                set_macos_settings(elite, timezone, computer_sleep_time, display_sleep_time)

                local_host_name = software.pop('local_host_name')
                computer_name = software.pop('computer_name')

                set_macos_hostname(elite, local_host_name, computer_name)

            elif name == 'Finder':
                layout = software.pop('favourites')

                elite.favourites(layout=layout)

            elif name == 'Spotify':
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

            elif name == 'Dock':
                app_layout = software.pop('apps')
                other_layout = software.pop('other')

                dock = elite.dock(app_layout=app_layout, other_layout=other_layout, mode='0600')
                restart_dock = restart_dock or dock.changed

            elif name == 'Launchpad':
                widget_layout = software.pop('widgets')
                app_layout = software.pop('apps')

                launchpad = elite.launchpad(widget_layout=widget_layout, app_layout=app_layout)
                restart_dock = restart_dock or launchpad.changed

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
                    path=f'/Applications/{app}.app',
                    state='present' if login_item else 'absent'
                )

            # Verify that no extra keys remain after processing a piece of  software
            if software:
                elite.fail(
                    message=(
                        'the software item contained unsupported keys '
                        f'{list(software.keys())}'
                    ),
                    ignore_failed=True
                )

    printer.info('cfprefsd Restart')
    elite.run(command='killall cfprefsd', ignore_failed=True, changed=False)

    if restart_dock:
        printer.info('Dock Restart')
        elite.run(command='killall Dock', changed=False)


if __name__ == '__main__':
    main()
