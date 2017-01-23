#!/usr/bin/env python3
import os

from elite.decorators import elite_main


def logic_pro_x_content(elite, config, printer, sample_library_source):
    printer.heading('Logic Pro X Content')

    source = f'{sample_library_source}/Apple/Apple Logic Pro X Sound Library'
    destination = f'{config.sample_library_dir}/Apple/Logic Pro X Sound Library'

    printer.info(f'Building directory structure and symlinks for content.')
    for src, dest in [
        (f'{destination}/GarageBand', '/Library/Application Support/GarageBand'),
        (f'{destination}/Logic', '/Library/Application Support/Logic'),
        (f'{destination}/Apple Loops', '/Library/Audio/Apple Loops'),
        (f'{destination}/Impulse Responses', '/Library/Audio/Impulse Responses')
    ]:
        elite.file(path=src, state='directory')

        file_info = elite.file_info(path=dest)
        if file_info.file_type != 'symlink':
            elite.file(path=dest, state='absent', sude=True)
            elite.file(path=dest, source=src, state='symlink', sudo=True)

    printer.info(f'Installing Logic Pro X content packages.')
    packages_proc = elite.run(command=f'find "{source}" -type f -name "*.pkg"')
    for package in packages_proc.stdout.rstrip().split('\n'):
        elite.run(
            command=f'installer -package "{package}" -target /', sudo=True
        )


def komplete_libraries(elite, config, printer, sample_library_source):
    printer.heading('Komplete Libraries')

    source = f'{sample_library_source}/Native Instruments'
    destination = f'{config.sample_library_dir}/Native Instruments'

    printer.info(f'Building directory structure for content.')
    elite.file(path=destination, state='directory')

    isos_proc = elite.run(command=f'find "{source}" -type f -name "*.iso"')
    for iso in isos_proc.stdout.rstrip().split('\n'):
        package_name = os.path.splitext(os.path.basename(iso))[0].replace('_', ' ')
        printer.info(f'Installing Native Instruments {package_name}.')

        mount_proc = elite.run(command=f'hdiutil mount "{iso}"')
        mountpoint = mount_proc.stdout.rstrip().split('\t')[-1]

        package_proc = elite.run(command=f'find "{mountpoint}" -name "* Installer Mac.pkg"')
        packages = package_proc.stdout.rstrip().split('\n')

        if len(packages) != 1:
            elite.fail(
                message=f'Unable to determine the installer package for this library, skipping'
            )
        package = packages[0]

        # Obtain all installer choices
        choices = elite.package_choices(path=package)
        for choice in choices.choices:
            if (
                choice['choiceAttribute'] == 'customLocation' and
                choice['attributeSetting'] == '/Users/Shared'
            ):
                choice_library_identifier = choice['choiceIdentifier']

        if not choice_library_identifier:
            elite.fail(message=(
                f'Unable to identify install location choice identifier '
                f'for this library, skipping'
            ))

        # TODO: implement a package action
        # elite.package(path=package, choices=[
        #     {
        #         'choiceIdentifier': choice_library_identifier,
        #         'choiceAttribute': 'customLocation',
        #         'attributeSetting': destination
        #     }
        # ], sudo=True)

        elite.run(command=f'hdiutil unmount "{mountpoint}"')

    elite.run(command=f'chflags hidden "{config.sample_library_dir}/Library"')


def omnisphere_steam_library(elite, config, printer, music_software_source):
    printer.heading('Spectrasonics STEAM Library')

    source = f'{music_software_source}/Spectrasonics/Spectrasonics Omnisphere v2/STEAM/'
    destination = f'{config.sample_library_dir}/Spectrasonics'
    steam_symlink = f'~/Library/Application Support/Spectrasonics/STEAM'

    elite.file(path=destination, state='directory')
    elite.rsync(source=source, path=destination, options='--exclude=.DS_Store')
    elite.run(command=f'find "{destination}" -type d -exec chmod 755 "{{}}" \;')
    elite.run(command=f'find "{destination}" -type f -exec chmod 644 "{{}}" \;')

    elite.file(path=os.path.dirname(steam_symlink), state='directory')
    file_info = elite.file_info(path=steam_symlink)
    if file_info.file_type != 'symlink':
        elite.file(path=steam_symlink, state='absent')
        elite.file(source=destination, path=steam_symlink, state='symlink')


@elite_main(config_path='config')
def main(elite, config, printer):
    printer.info('Determining sample library and music software sources.')
    for sample_library_source in config.sample_library_sources:
        source_dir = elite.file_info(path=sample_library_source)
        if source_dir.file_type == 'directory':
            break
    else:
        elite.fail(message='Unable to find any suitable sample library source.')

    # Determine the music software source path
    for music_software_source in config.music_software_sources:
        source_dir = elite.file_info(path=music_software_source)
        if source_dir.file_type == 'directory':
            break
    else:
        elite.fail(message='Unable to find any suitable music software source.')

    # logic_pro_x_content(elite, config, printer, sample_library_source)
    komplete_libraries(elite, config, printer, sample_library_source)
    omnisphere_steam_library(elite, config, printer, music_software_source)


if __name__ == '__main__':
    main()
