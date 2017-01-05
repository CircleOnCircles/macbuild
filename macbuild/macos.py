def macos(ansible, config):
    ansible.info('Set computer sleep time.')
    with ansible.settings(sudo=True, quiet=True):
        computer_sleep = ansible.command('systemsetup -getcomputersleep')

    if f'Computer Sleep: {config.macos_computer_sleep_time}' != \
       computer_sleep.stdout.replace('after ', '').replace('minutes', ''):
        with ansible.settings(sudo=True):
            ansible.command(f'systemsetup -setcomputersleep {config.macos_computer_sleep_time}')

    ansible.info('Set disply sleep time.')
    with ansible.settings(sudo=True, quiet=True):
        display_sleep = ansible.command('systemsetup -getdisplaysleep')

    if f'Display Sleep: {config.macos_display_sleep_time}' != \
       display_sleep.stdout.replace('after ', '').replace('minutes', ''):
        with ansible.settings(sudo=True):
            ansible.command(f'systemsetup -setdisplaysleep {config.macos_display_sleep_time}')

    ansible.info('Set the timezone.')
    with ansible.settings(sudo=True, quiet=True):
        current_timezone = ansible.command('systemsetup -gettimezone')

    if f'Time Zone: {config.macos_timezone}' != current_timezone.stdout:
        with ansible.settings(sudo=True):
            ansible.command(f'systemsetup -settimezone {config.macos_timezone}')

    ansible.info("Unhide the user's Library directory.")
    with ansible.settings(quiet=True):
        library_flags = ansible.command('ls -lOd ~/Library')

    if 'hidden' in library_flags.stdout:
        ansible.command('chflags nohidden ~/Library')

    ansible.info('Create the development folder.')
    ansible.file(path=config.development_dir, state='directory')

    ansible.info('Create the screenshots folder.')
    ansible.file(path='~/Pictures/Screenshots', state='directory')

    ansible.info('Grant permission to audio plugin paths.')
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
        with ansible.settings(sudo=True):
            ansible.file(path=path, state='directory', owner='root', group='admin', mode='0775')

    ansible.info('Set operating system defaults.')
    for defaults in config.macos_defaults:
        with ansible.settings(sudo=defaults.get('become', False)):
            ansible.plist(
                dest=defaults['domain'],
                values=defaults,
                container=defaults.get('container')
            )


def default_apps(ansible, config):
    ansible.info('Setup default app associations.')

    for bundle_id, utis in config.default_apps_associations.items():
        for uti in utis:
            with ansible.settings(quiet=True):
                association = ansible.command(f'duti -d {uti}')

            if association.stdout != bundle_id.lower():
                ansible.command(f'duti -s {bundle_id} {uti} all')


def startup(ansible, config):
    ansible.info('Add login items.')
    for login_item in config.startup_login_items:
        ansible.command(f"loginitems -a '{login_item}'")


def dock(ansible, config):
    ansible.info('Remove all items from the dock.')
    ansible.command('dockutil --remove all --no-restart')

    ansible.info('Add apps to the dock.')
    for app in config.dock_apps:
        ansible.command(f"dockutil --add '/Applications/{app}.app' --no-restart")

    ansible.info('Add folders to the dock.')
    for folder in config.dock_folders:
        if not isinstance(folder, dict):
            folder = {'dest': folder}
        ansible.command(
            f"dockutil --add '{folder['dest']}' "
            f"--view {folder.get('view', 'fan')} "
            f"--display {folder.get('display', 'stack')} "
            f"--sort {folder.get('sort', 'dateadded')} --no-restart"
        )

    ansible.info('Restart the dock.')
    ansible.command('killall Dock')
