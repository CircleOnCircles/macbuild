import os


def sublime_text(elite, config, printer):
    printer.info('Install sublime text.')
    elite.cask(name='sublime-text')

    printer.info('Ensure the sublime text settings directories exist.')
    for path in [
        '~/Library/Application Support/Sublime Text 3/Installed Packages',
        '~/Library/Application Support/Sublime Text 3/Packages/User',
    ]:
        elite.file(path=path, state='directory')

    printer.info('Install sublime text package control.')
    elite.download(
        url='http://packagecontrol.io/Package Control.sublime-package',
        path='~/Library/Application Support/Sublime Text 3/Installed Packages',
        mode='0644'
    )

    printer.info('Install sublime text settings.')
    elite.rsync(
        source='files/sublime_text/',
        path='~/Library/Application Support/Sublime Text 3/Packages/User'
    )


def spotify(elite, config, printer):
    def spotify_value(value):
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        else:
            return str(value)

    printer.info('Install spotify.')
    elite.cask(name='spotify')

    printer.info('Ensure the spotify global settings directories exist.')
    elite.file(path='~/Library/Application Support/Spotify', state='directory')

    printer.info('Check if global spotify prefs file exists.')
    global_spotify_prefs = elite.file_info(path='~/Library/Application Support/Spotify/prefs')

    if not global_spotify_prefs.exists:
        printer.info('Creating the global spotify prefs file.')
        elite.file(
            path='~/Library/Application Support/Spotify/prefs', mode='0644'
        )

    printer.info('Set global settings.')
    for pref, value in config.spotify_global_settings.items():
        elite.spotify_pref(pref=pref, value=value)

    printer.info('Set user settings.')
    for pref, value in config.spotify_user_settings.items():
        elite.spotify_pref(pref=pref, value=value, username=config.spotify_username)

    printer.info('Ensure that Spotify is not in login items.')
    elite.login_item(path='/Applications/Spotify.app', state='absent')


def software(elite, config, printer):
    printer.info('Homebrew Cask desktop applications.')
    for cask in config.software_brew_casks:
        elite.cask(name=cask)

    printer.info('Check app store applications.')
    for app in config.software_appstore_apps:
        app_file = elite.file_info(path=f'/Applications/{app}.app/Contents/_MASReceipt/receipt')
        if not app_file.exists:
            elite.fail(message=f'Please install {app} from the App Store')

    printer.info('Set application defaults.')
    for defaults in config.software_app_defaults:
        elite.plist(
            domain=defaults.get('domain'),
            values=defaults.get('values'),
            path=defaults.get('path'),
            container=defaults.get('container'),
            sudo=defaults.get('sudo', False)
        )

    printer.info('Refresh cfprefsd.')
    elite.run(command='killall cfprefsd', ignore_failed=True, changed=False)

    printer.info('Install the app files requested.')
    for app_file in config.software_app_files:
            if app_file['path'] != '/' and app_file['path'] != '~':
                elite.file(
                    path=os.path.dirname(app_file['path']),
                    state='directory',
                    sudo=app_file.get('sudo', False)
                )

            elite.file(
                source=app_file['source'], path=app_file['path'],
                mode=app_file.get('mode', '0644'), sudo=app_file.get('sudo', False)
            )

    printer.info('Symlink file to requested destination.')
    for app_symlink in config.software_app_symlinks:
        if app_symlink['path'] != '/' and app_symlink['path'] != '~':
            elite.file(path=os.path.dirname(app_symlink['path']), state='directory')

        symlink_health = elite.file_info(path=app_symlink['path'])
        if symlink_health.exists and symlink_health.file_type != 'symlink':
            elite.file(path=app_symlink['path'], state='absent')

        elite.file(path=app_symlink['path'], source=app_symlink['source'], state='symlink')


def native_instruments(elite, config, printer):
    printer.info('Place Kontakt libraries in the requested order.')
    for index, library in enumerate(config.native_instruments_kontakt_library_order):
        elite.plist(
            domain=f'com.native-instruments.{library}',
            values={'UserListIndex': index}
        )
