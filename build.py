#!/usr/bin/env python3
import os

from elite.decorators import elite_main


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
            message='Unable to find any suitable music software source.', ignore_failed=True
        )

    printer.info('Homebrew Update')
    elite.brew_update()

    restart_dock = False

    for group, software_items in config.software.items():
        printer.heading(group)

        for software in software_items:
            software = software.copy()

            if 'appstore' in software and 'name' not in software:
                software['name'] = software['appstore']

            if 'name' not in software:
                elite.fail(message=f'the software item {software} has no name')

            name = software.pop('name')
            tap = software.pop('tap', None)
            appstore = software.pop('appstore', None)
            cask = software.pop('cask', None)
            brew = software.pop('brew', None)
            pip = software.pop('pip', None)
            npm = software.pop('npm', None)
            files = software.pop('files', None)
            download = software.pop('download', None)
            git = software.pop('git', None)
            rsync = software.pop('rsync', None)
            symlinks = software.pop('symlinks', None)
            defaults = software.pop('defaults', None)
            json = software.pop('json', None)
            handlers = software.pop('handlers', None)
            login_item = software.pop('login_item', False)

            printer.info(name)

            if tap:
                taps = tap if isinstance(tap, list) else [tap]
                for tap in taps:
                    elite.tap(name=tap)

            if appstore:
                app_file = elite.file_info(
                    path=f'/Applications/{appstore}.app/Contents/_MASReceipt/receipt'
                )
                if not app_file.exists:
                    elite.fail(
                        message=f'Please install {appstore} from the App Store',
                        ignore_failed=True
                    )

            if cask:
                casks = cask if isinstance(cask, list) else [cask]
                for cask in casks:
                    elite.cask(name=cask, env=env)

            if brew:
                brews = brew if isinstance(brew, list) else [brew]
                for brew in brews:
                    elite.brew(name=brew, state='latest')

            if pip:
                pips = pip if isinstance(pip, list) else [pip]
                for pip in pips:
                    elite.pip(name=pip, state='latest', executable='pip3')

            if npm:
                npms = npm if isinstance(npm, list) else [npm]
                for npm in npms:
                    elite.npm(name=npm, mode='global')

            if files:
                for file in files:
                    if (
                        file.get('state', 'file') == 'file' and
                        file['path'] != '/' and file['path'] != '~'
                    ):
                        elite.file(
                            path=os.path.dirname(file['path']),
                            state='directory',
                            sudo=file.get('sudo', False)
                        )

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

            if download:
                downloads = download if isinstance(download, list) else [download]
                for download in downloads:
                    elite.download(path=download['path'], url=download['url'])

            if git:
                gits = git if isinstance(git, list) else [git]
                for git in gits:
                    elite.git(path=git['path'], repo=git['repo'])

            if rsync:
                rsyncs = rsync if isinstance(rsync, list) else [rsync]
                for rsync in rsyncs:
                    elite.rsync(path=rsync['path'], source=rsync['source'])

            if symlinks:
                for symlink in symlinks:
                    if symlink['path'] != '/' and symlink['path'] != '~':
                        elite.file(
                            path=os.path.dirname(symlink['path']),
                            state='directory',
                            sudo=symlink.get('sudo', False)
                        )

                    symlink_health = elite.file_info(path=symlink['path'])
                    if symlink_health.exists and symlink_health.file_type != 'symlink':
                        elite.file(path=symlink['path'], state='absent')

                    elite.file(path=symlink['path'], source=symlink['source'], state='symlink')

            if defaults:
                for default in defaults:
                    elite.plist(
                        domain=default.get('domain'),
                        values=default.get('values'),
                        path=default.get('path'),
                        container=default.get('container'),
                        sudo=default.get('sudo', False)
                    )

            if json:
                jsons = json if isinstance(json, list) else [json]
                for json in jsons:
                    elite.json(
                        path=json.get('path'),
                        values=json.get('values')
                    )

            if name == 'Finder':
                layout = software.pop('favourites')
                elite.favourites(layout=layout)
            elif name == 'Dock':
                app_layout = software.pop('apps')
                other_layout = software.pop('other')
                dock = elite.dock(app_layout=app_layout, other_layout=other_layout)
                restart_dock = restart_dock or dock.changed
            elif name == 'Launchpad':
                widget_layout = software.pop('widgets')
                app_layout = software.pop('apps')
                launchpad = elite.launchpad(widget_layout=widget_layout, app_layout=app_layout)
                restart_dock = restart_dock or launchpad.changed
            elif name == 'Docker':
                docker_create = elite.run(
                    command='docker-machine create --driver virtualbox default',
                    creates='~/.docker/machine/machines/default'
                )
                if docker_create.changed:
                    elite.run(command='docker-machine stop default')
            elif name == 'VIM':
                vimrc_path = software.pop('vimrc_path')
                elite.brew(name='vim', options='--with-lua', state='latest')
                vimrc = elite.file(path='~', source=vimrc_path)
                if vimrc.changed:
                    elite.run(command='vim +PluginInstall +qall')
            elif name == 'Spotify':
                global_settings = software.pop('global_settings')
                user_settings = software.pop('user_settings')
                username = software.pop('username')

                for pref, value in global_settings.items():
                    elite.spotify_pref(pref=pref, value=value)

                for pref, value in user_settings.items():
                    elite.spotify_pref(pref=pref, value=value, username=username)

                elite.login_item(path='/Applications/Spotify.app', state='absent')
            elif name == 'Native Instruments Kontakt 5':
                library_order = software.pop('library_order')
                for index, library in enumerate(library_order):
                    elite.plist(
                        domain=f'com.native-instruments.{library}',
                        values={'UserListIndex': index}
                    )

            if handlers:
                for handler in handlers:
                    elite.handler(
                        path=f'/Applications/{name}.app',
                        content_type=handler
                    )

            if login_item:
                elite.login_item(path=f'/Applications/{name}.app')

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
