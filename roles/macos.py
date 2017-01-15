def macos(elite, config, printer):
    printer.info('Set computer sleep time.')
    computer_sleep = elite.run(command='systemsetup -getcomputersleep', sudo=True, changed=False)

    if (
        f'Computer Sleep: {config.macos_computer_sleep_time}' !=
        computer_sleep.stdout.rstrip().replace('after ', '').replace('minutes', '')
    ):
        elite.run(
            command=f'systemsetup -setcomputersleep {config.macos_computer_sleep_time}', sudo=True
        )

    printer.info('Set disply sleep time.')
    display_sleep = elite.run(command='systemsetup -getdisplaysleep', sudo=True, changed=False)

    if (
        f'Display Sleep: {config.macos_display_sleep_time}' !=
        display_sleep.stdout.rstrip().replace('after ', '').replace('minutes', '')
    ):
        elite.run(
            command=f'systemsetup -setdisplaysleep {config.macos_display_sleep_time}', sudo=True
        )

    printer.info('Set the timezone.')
    current_timezone = elite.run(command='systemsetup -gettimezone', sudo=True, changed=False)

    if f'Time Zone: {config.macos_timezone}' != current_timezone.stdout.rstrip():
        elite.run(command=f'systemsetup -settimezone {config.macos_timezone}', sudo=True)

    printer.info("Unhide the user's Library directory.")
    library_flags = elite.run(command='ls -lOd ~/Library', changed=False)
    if 'hidden' in library_flags.stdout:
        elite.run(command='chflags nohidden ~/Library')

    printer.info('Create the development folder.')
    elite.file(path=config.development_dir, state='directory')

    printer.info('Create the screenshots folder.')
    elite.file(path='~/Pictures/Screenshots', state='directory')

    printer.info('Grant permission to audio plugin paths.')
    for path in [
        # Documentation
        '/Library/Documentation',
        # Presets
        '/Library/Audio/Presets',
        # AAX
        '/Library/Application Support/Avid/Audio/Plug-Ins',
        # RTAS
        '/Library/Application Support/Digidesign/Plug-Ins',
        # AU
        '/Library/Audio/Plug-Ins/Components',
        # VST
        '/Library/Audio/Plug-Ins/VST',
        # VST3
        '/Library/Audio/Plug-Ins/VST3',
    ]:
        elite.file(
            path=path, state='directory', owner='root', group='admin', mode='0775', sudo=True
        )

    printer.info('Set operating system defaults.')
    for defaults in config.macos_defaults:
        elite.plist(
            domain=defaults.get('domain'),
            values=defaults.get('values'),
            path=defaults.get('path'),
            container=defaults.get('container'),
            sudo=defaults.get('sudo', False)
        )


def default_apps(elite, config, printer):
    printer.info('Setup default app associations.')

    for bundle_id, utis in config.default_apps_associations.items():
        for uti in utis:
            association = elite.run(command=f'duti -d {uti}', changed=False)

            if association.stdout.rstrip() != bundle_id.lower():
                elite.run(command=f'duti -s {bundle_id} {uti} all')


def startup(elite, config, printer):
    printer.info('Add login items.')

    login_items = elite.run(command='loginitems -l', changed=False)
    login_items = login_items.stdout.rstrip().split(', ')

    for login_item in config.startup_login_items:
        if login_item not in login_items:
            elite.run(command=f"loginitems -a '{login_item}'")


def dock(elite, config, printer):
    printer.info('Remove all items from the dock.')
    elite.run(command='dockutil --remove all --no-restart')

    printer.info('Add apps to the dock.')
    for app in config.dock_apps:
        elite.run(command=f"dockutil --add '/Applications/{app}.app' --no-restart")

    printer.info('Add folders to the dock.')
    for folder in config.dock_other:
        if not isinstance(folder, dict):
            folder = {'dest': folder}

        elite.run(command=(
            f"dockutil --add '{folder['dest']}' "
            f"--view {folder.get('view', 'fan')} "
            f"--display {folder.get('display', 'stack')} "
            f"--sort {folder.get('sort', 'dateadded')} --no-restart"
        ))

    printer.info('Restart the dock.')
    elite.run(command='killall Dock', changed=False)
