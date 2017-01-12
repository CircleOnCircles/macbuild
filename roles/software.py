import os
import re


def sublime_text(elite, config, printer):
    printer.info('Install sublime text.')
    elite.cask(name='sublime-text', state='present')

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
    # elite.file(
    #     source='files/sublime_text/',
    #     path='~/Library/Application Support/Sublime Text 3/Packages/User'
    # )


def spotify(elite, config, printer):
    def spotify_value(value):
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        else:
            return str(value)

    printer.info('Install spotify.')
    elite.cask(name='spotify', state='present')

    printer.info('Ensure the spotify global settings directories exist.')
    elite.file(path='~/Library/Application Support/Spotify', state='directory')

    printer.info('Check if global spotify prefs file exists.')
    global_spotify_prefs = elite.file_info(path='~/Library/Application Support/Spotify/prefs')

    if not global_spotify_prefs.exists:
        printer.info('Creating the global spotify prefs file.')
        elite.file(
            path='~/Library/Application Support/Spotify/prefs', state='touch', mode='0644'
        )

    printer.info('Set global settings.')
    # for key, value in config.spotify_global_settings.items():
    #     elite.lineinfile(
    #         dest='~/Library/Application Support/Spotify/prefs',
    #         regexp=f'^{re.escape(key)}=',
    #         line=f'{key}={spotify_value(value)}'
    #     )

    spotify_user_config_path = (
        f'~/Library/Application Support/Spotify/Users/{config.spotify_username}-user'
    )

    printer.info('Ensure the spotify user settings directory exists.')
    elite.file(path=spotify_user_config_path, state='directory')

    printer.info('Check if user spotify prefs file exists.')
    user_spotify_prefs = elite.file_info(path=f'{spotify_user_config_path}/prefs')

    if not user_spotify_prefs.exists:
        printer.info('Creating the user spotify prefs file.')
        elite.file(path=f'{spotify_user_config_path}/prefs', state='touch', mode='0644')

    printer.info('Set user settings.')
    # for key, value in config.spotify_user_settings.items():
    #     elite.lineinfile(
    #         dest=f'{spotify_user_config_path}/prefs',
    #         regexp=f'^{re.escape(key)}=',
    #         line=f'{key}={spotify_value(value)}'
    #     )

    printer.info('Check if Spotify is in login items.')
    spotify_login = elite.run(
        command=(
            'osascript -l JavaScript -e "'
            "Application('System Events').loginItems.byName('Spotify').name()"
            '"'
        ),
        ignore_failed=True
    )

    if spotify_login.ok:
        printer.info('Remove Spotify from login items.')
        elite.run(
            command=(
                'osascript -l JavaScript -e "'
                "Application('System Events').loginItems.byName('Spotify').delete()"
                '"'
            )
        )


def software(elite, config, printer):
    printer.info('Homebrew Cask desktop applications.')
    for cask in config.software_brew_casks:
        elite.cask(name=cask, state='present')

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
    elite.run(command='killall cfprefsd', ignore_failed=True)

    printer.info('Install the app files requested.')
    for app_file in config.software_app_files:
            if app_file['path'] != '/' and app_file['path'] != '~':
                elite.file(
                    path=os.path.dirname(app_file['path']),
                    state='directory', sudo=app_file.get('sudo', False)
                )

            elite.file(
                source=app_file['source'], path=app_file['path'], mode=app_file.get('mode', '0644'),
                sudo=app_file.get('sudo', False)
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
