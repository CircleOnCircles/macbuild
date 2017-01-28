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
    elite.file(path='~/Library', state='directory', flags=['hidden'])

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

    printer.info('Refresh cfprefsd.')
    elite.run(command='killall cfprefsd', ignore_failed=True, changed=False)


def default_apps(elite, config, printer):
    printer.info('Setup default app associations.')
    for app, content_types in config.default_apps_associations.items():
        for content_type in content_types:
            elite.handler(
                path=f'/Applications/{app}.app',
                content_type=content_type
            )


def login_items(elite, config, printer):
    printer.info('Add login items.')
    for login_item in config.startup_login_items:
        elite.login_item(path=f'/Applications/{login_item}.app')
