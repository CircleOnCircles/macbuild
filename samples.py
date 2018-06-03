#!/usr/bin/env python3
import os
import re
from collections import namedtuple

from elite.decorators import elite_main


def komplete_libraries(elite, config, printer, sample_library_source):
    printer.heading('Komplete Libraries')

    printer.info('Library Directories')
    for base_sample_dir in ['Native Instruments Kontakt', 'Native Instruments Battery']:
        elite.file(
            path=os.path.join(config.sample_library_dir, base_sample_dir), state='directory'
        )

    for library in config.komplete_libraries:
        printer.info(f'Native Instruments {library}')

        # Find the ISO for the library
        isos = elite.find(
            path=sample_library_source, min_depth=2, max_depth=3, types=['file'],
            patterns=[
                f"*/Native Instruments Kontakt/Native Instruments/{library.replace(' ', '_')}.iso",
                f"*/Native Instruments Battery/{library.replace(' ', '_')}.iso"
            ]
        )

        if len(isos.paths) != 1:
            elite.fail(message='unable to find sample library iso image')

        iso = isos.paths[0]

        # Build the destination base directory
        destination = os.path.join(
            config.sample_library_dir,
            os.path.dirname(os.path.relpath(iso, sample_library_source))
        )

        elite.file(path=destination, state='directory')

        mount = elite.run(command=f'hdiutil mount "{iso}"', changed=False)
        mountpoint = mount.stdout.rstrip().split('\t')[-1]

        packages = elite.find(path=mountpoint, patterns=['* Installer Mac.pkg'])

        if len(packages.paths) != 1:
            elite.fail(
                message='Unable to determine the installer package for this library, skipping'
            )

        package = packages.paths[0]

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
                'Unable to identify install location choice identifier for this library, skipping'
            ))

        elite.package(
            path=package,
            choices=[
                {
                    'choiceIdentifier': choice_library_identifier,
                    'choiceAttribute': 'customLocation',
                    'attributeSetting': destination
                }
            ],
            sudo=True
        )

        elite.run(command=f'hdiutil unmount "{mountpoint}"', changed=False, ignore_failed=True)

    elite.file(
        path=os.path.join(config.sample_library_dir, 'Library'),
        state='directory', flags=['hidden']
    )


def omnisphere_steam_library(elite, config, printer, music_software_source):
    printer.heading('Spectrasonics Omnisphere')

    printer.info('Spectrasonics STEAM Library')

    source = os.path.join(
        music_software_source, 'Spectrasonics/Spectrasonics Omnisphere v2/STEAM'
    )
    destination = os.path.join(config.sample_library_dir, 'Spectrasonics Omnisphere')
    steam_symlink = '~/Library/Application Support/Spectrasonics/STEAM'

    elite.file(path=destination, state='directory')
    elite.rsync(source=source, path=destination, options='--exclude=.DS_Store --no-perms')

    for path in elite.find(path=destination, types=['directory']).paths:
        elite.file(path=path, state='directory', mode='0755')

    for path in elite.find(path=destination, types=['file']).paths:
        elite.file(path=path, mode='0644')

    elite.file(path=os.path.dirname(steam_symlink), state='directory')

    file_info = elite.file_info(path=steam_symlink)
    if file_info.file_type == 'directory':
        elite.file(path=steam_symlink, state='absent')

    elite.file(path=steam_symlink, source=os.path.join(destination, 'STEAM'), state='symlink')


def kontakt_libraries_and_drum_samples(elite, config, printer, sample_library_source):
    printer.heading('Kontakt Libraries and Drum & Vocal Samples')

    # Build a data structure which we may use to determine sample library properties
    sample_libraries_config = {}
    for sample_library_config in config.sample_libraries:
        SampleLibraryConfig = namedtuple(
            'SampleLibraryConfig', ['base_dir', 'base_dirs', 'installer', 'extract_subdirs']
        )

        if isinstance(sample_library_config, str):
            name = sample_library_config
            base_dir = None
            base_dirs = {}
            installer = None
            extract_subdirs = {}
        else:
            name = sample_library_config['name']
            base_dir = sample_library_config.get('base_dir')
            base_dirs = sample_library_config.get('base_dirs', {})
            installer = sample_library_config.get('installer')
            extract_subdirs = sample_library_config.get('extract_subdirs', {})

        sample_libraries_config[name] = SampleLibraryConfig(
            base_dir, base_dirs, installer, extract_subdirs
        )

    printer.info('Base Directories')
    for base_sample_dir in ['Native Instruments Kontakt', 'Drum & Vocal Samples']:
        elite.file(
            path=os.path.join(config.sample_library_dir, base_sample_dir), state='directory'
        )

    for library, library_config in sample_libraries_config.items():
        printer.info(library)

        # Find the source directory for the library
        library_paths = elite.find(
            path=sample_library_source, min_depth=3, max_depth=3, types=['directory'],
            patterns=[
                f'*/Native Instruments Kontakt/*/{library}',
                f'*/Drum & Vocal Samples/*/{library}'
            ]
        )

        if len(library_paths.paths) != 1:
            elite.fail(message='unable to find sample library source directory')

        library_path = library_paths.paths[0]

        # Find all ZIP and RAR files present in the downloaded library
        archives = elite.find(path=library_path, types=['file'], patterns=['*.zip', '*.rar'])
        if not archives.paths:
            elite.fail(message='no archives were found in the sample library source directory')

        # Build the destination base directory
        destination_base_dir = os.path.join(
            config.sample_library_dir, os.path.relpath(library_path, sample_library_source)
        )

        # Ensure that the parent / vendor directory exists
        elite.file(path=os.path.dirname(destination_base_dir), state='directory')

        for archive in archives.paths:
            # Check for multipart RAR archives and only extract part 1
            if (
                re.search('\.part[0-9]+\.rar$', archive) and
                not re.search('\.part0*1\.rar$', archive)
            ):
                continue

            # Determine the relative location of the archive being extracted
            archive_relative = os.path.relpath(archive, library_path)
            archive_sub_dir = os.path.dirname(archive_relative)

            # Determine the destination to extract into
            if archive_relative in library_config.extract_subdirs:
                destination = os.path.join(
                    destination_base_dir, library_config.extract_subdirs[archive_relative]
                )
            elif archive_sub_dir:
                destination = os.path.join(destination_base_dir, archive_sub_dir)
            else:
                destination = destination_base_dir

            # Determine the base directory of the archive
            if archive_relative in library_config.base_dirs:
                base_dir = library_config.base_dirs[archive_relative]
            else:
                base_dir = library_config.base_dir

            # Extract the archive
            elite.archive(
                path=destination,
                source=archive,
                ignore_files=['__MACOSX', '.DS_Store'],
                base_dir=base_dir,
                preserve_mode=False
            )

        # Run the installer package if required
        if library_config.installer:
            elite.package(path=os.path.join(destination, library_config.installer), sudo=True)


@elite_main(config_path='config', config_order=['global.yaml', 'samples.yaml'])
def main(elite, config, printer):
    printer.info('Determining sample library and music software sources.')

    sample_library_source = config.sample_library_source
    if sample_library_source:
        elite.info(message=f'using sample library source {sample_library_source}')
    else:
        elite.fail(message='unable to find any suitable sample library software source')

    music_software_source = config.music_software_source
    if music_software_source:
        elite.info(message=f'using music software software {music_software_source}')
    else:
        elite.fail(message='unable to find any suitable music software source')

    komplete_libraries(elite, config, printer, sample_library_source)
    omnisphere_steam_library(elite, config, printer, music_software_source)
    kontakt_libraries_and_drum_samples(elite, config, printer, sample_library_source)


if __name__ == '__main__':
    main()
