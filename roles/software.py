import os
import re


def sublime_text(ansible, config, printer):
    printer.info('Install sublime text.')
    ansible.homebrew_cask(name='sublime-text', state='present')

    printer.info('Ensure the sublime text settings directories exist.')
    for path in [
        '~/Library/Application Support/Sublime Text 3/Installed Packages',
        '~/Library/Application Support/Sublime Text 3/Packages/User',
    ]:
        ansible.file(path=path, state='directory')

    printer.info('Install sublime text package control.')
    ansible.get_url(
        url='http://packagecontrol.io/Package Control.sublime-package',
        dest='~/Library/Application Support/Sublime Text 3/Installed Packages',
        mode='0644'
    )

    printer.info('Install sublime text settings.')
    ansible.synchronize(
        src='files/sublime_text/',
        dest='~/Library/Application Support/Sublime Text 3/Packages/User'
    )


def spotify(ansible, config, printer):
    def spotify_value(value):
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        else:
            return str(value)

    printer.info('Install spotify.')
    ansible.homebrew_cask(name='spotify', state='present')

    printer.info('Ensure the spotify global settings directories exist.')
    ansible.file(path='~/Library/Application Support/Spotify', state='directory')

    printer.info('Check if global spotify prefs file exists.')
    global_spotify_prefs = ansible.stat(path='~/Library/Application Support/Spotify/prefs')

    if not global_spotify_prefs.stat['exists']:
        printer.info('Creating the global spotify prefs file.')
        ansible.file(
            path='~/Library/Application Support/Spotify/prefs', state='touch', mode='0644'
        )

    printer.info('Set global settings.')
    for key, value in config.spotify_global_settings.items():
        ansible.lineinfile(
            dest='~/Library/Application Support/Spotify/prefs',
            regexp=f'^{re.escape(key)}=',
            line=f'{key}={spotify_value(value)}'
        )

    spotify_user_config_path = (
        f'~/Library/Application Support/Spotify/Users/{config.spotify_username}-user'
    )

    printer.info('Ensure the spotify user settings directory exists.')
    ansible.file(path=spotify_user_config_path, state='directory')

    printer.info('Check if user spotify prefs file exists.')
    user_spotify_prefs = ansible.stat(path=f'{spotify_user_config_path}/prefs')

    if not user_spotify_prefs.stat['exists']:
        printer.info('Creating the user spotify prefs file.')
        ansible.file(path=f'{spotify_user_config_path}/prefs', state='touch', mode='0644')

    printer.info('Set user settings.')
    for key, value in config.spotify_user_settings.items():
        ansible.lineinfile(
            dest=f'{spotify_user_config_path}/prefs',
            regexp=f'^{re.escape(key)}=',
            line=f'{key}={spotify_value(value)}'
        )

    printer.info('Check if Spotify is in login items.')
    with ansible.settings(ignore_errors=True):
        spotify_login = ansible.command(
            'osascript -l JavaScript -e '
            '"Application(\'System Events\').loginItems.byName(\'Spotify\').name()"'
        )

    if spotify_login.rc == 0:
        printer.info('Remove Spotify from login items.')
        ansible.command(
            'osascript -l JavaScript -e '
            '"Application(\'System Events\').loginItems.byName(\'Spotify\').delete()"'
        )


def software(ansible, config, printer):
    printer.info('Homebrew Cask desktop applications.')
    for cask in config.software_brew_casks:
        ansible.homebrew_cask(name=cask, state='present')

    printer.info('Check app store applications.')
    for app in config.software_appstore_apps:
        app_file = ansible.stat(path=f'/Applications/{app}.app/Contents/_MASReceipt/receipt')
        if not app_file.stat['exists']:
            ansible.fail(msg=f'Please install {app} from the App Store')

    printer.info('Set application defaults.')
    for default in config.software_app_defaults:
        ansible.plist(
            dest=default['domain'],
            values=default['values'],
            container=default.get('container')
        )

    printer.info('Refresh cfprefsd.')
    with ansible.settings(ignore_errors=True):
        ansible.command('killall cfprefsd')

    printer.info('Install the app files requested.')
    for app_file in config.software_app_files:
        with ansible.settings(sudo=app_file.get('sudo', False)):
            if app_file['dest'] != '/' and app_file['dest'] != '~':
                ansible.file(path=os.path.dirname(app_file['dest']), state='directory')

            ansible.copy(
                src=app_file['src'], dest=app_file['dest'], mode=app_file.get('mode', '0644')
            )

    printer.info('Symlink file to requested destination.')
    for app_symlink in config.software_app_symlinks:
        if app_symlink['dest'] != '/' and app_symlink['dest'] != '~':
            ansible.file(path=os.path.dirname(app_symlink['dest']), state='directory')

        symlink_health = ansible.stat(path=app_symlink['dest'])
        if symlink_health.stat['exists'] and not symlink_health.stat['islnk']:
            ansible.file(path=app_symlink['dest'], state='absent')

        ansible.file(dest=app_symlink['dest'], src=app_symlink['src'], state='link')


def native_instruments(ansible, config, printer):
    printer.info('Place Kontakt libraries in the requested order.')
    for index, library in enumerate(config.native_instruments_kontakt_library_order):
        ansible.plist(
            dest=f'com.native-instruments.{library}',
            values={'UserListIndex': index}
        )
