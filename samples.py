#!/usr/bin/env python3
import os
import re
from collections import namedtuple

from elite.decorators import elite_main


def logic_pro_x_content(elite, config, printer, sample_library_source):
    printer.heading('Logic Pro X Content')

    source = os.path.join(sample_library_source, 'Apple', 'Apple Logic Pro X Sound Library')
    destination = os.path.join(config.sample_library_dir, 'Apple', 'Logic Pro X Sound Library')

    printer.info('Building directory structure and symlinks for content.')
    for src, dest in [
        (os.path.join(destination, 'GarageBand'), '/Library/Application Support/GarageBand'),
        (os.path.join(destination, 'Logic'), '/Library/Application Support/Logic'),
        (os.path.join(destination, 'Apple Loops'), '/Library/Audio/Apple Loops'),
        (os.path.join(destination, 'Impulse Responses'), '/Library/Audio/Impulse Responses')
    ]:
        elite.file(path=src, state='directory')

        file_info = elite.file_info(path=dest)
        if file_info.file_type != 'symlink':
            elite.file(path=dest, state='absent', sudo=True)
            elite.file(path=dest, source=src, state='symlink', sudo=True)

    printer.info('Installing Logic Pro X content packages.')
    packages = elite.find(path=source, types=['file'], patterns=['*.pkg'])
    for package in packages.paths:
        elite.package(path=package, sudo=True)


def komplete_libraries(elite, config, printer, sample_library_source):
    printer.heading('Komplete Libraries')

    source = os.path.join(sample_library_source, 'Native Instruments')
    destination = os.path.join(config.sample_library_dir, 'Native Instruments')

    printer.info('Building directory structure for content.')
    elite.file(path=destination, state='directory')

    isos = elite.find(path=source, types=['file'], patterns=['*.iso'])
    for iso in isos.paths:
        package_name = os.path.splitext(os.path.basename(iso))[0].replace('_', ' ')
        printer.info(f'Installing Native Instruments {package_name}.')

        mount = elite.run(command=f'hdiutil mount "{iso}"')
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

        elite.run(command=f'hdiutil unmount "{mountpoint}"')

    elite.file(
        path=os.path.join(config.sample_library_dir, 'Library'),
        ensure='directory', flags=['hidden']
    )


def omnisphere_steam_library(elite, config, printer, music_software_source):
    printer.heading('Spectrasonics STEAM Library')

    source = os.path.join(
        music_software_source, 'Spectrasonics/Spectrasonics Omnisphere v2/STEAM/'
    )
    destination = os.path.join(config.sample_library_dir, 'Spectrasonics')
    steam_symlink = '~/Library/Application Support/Spectrasonics/STEAM'

    elite.file(path=destination, state='directory')
    elite.rsync(source=source, path=destination, options='--exclude=.DS_Store')

    for path in elite.find(path=destination, types=['directory']).paths:
        elite.file(path=path, state='directory', mode='0755')

    for path in elite.find(path=destination, types=['file']).paths:
        elite.file(path=path, mode='0644')

    elite.file(path=os.path.dirname(steam_symlink), state='directory')
    file_info = elite.file_info(path=steam_symlink)
    if file_info.file_type != 'symlink':
        elite.file(path=steam_symlink, state='absent')
        elite.file(source=destination, path=steam_symlink, state='symlink')


def kontakt_libraries_and_drum_samples(elite, config, printer, sample_library_source):
    # Build a data structure which we may use to determine sample library properties
    sample_libraries_config = {}
    for sample_library_config in config.sample_libraries:
        SampleLibraryConfig = namedtuple(
            'SampleLibraryConfig', ['base_dir', 'installer', 'extract_subdirs']
        )

        if isinstance(sample_library_config, str):
            name = sample_library_config
            base_dir = None
            installer = None
            extract_subdirs = {}
        else:
            name = sample_library_config['name']
            base_dir = sample_library_config.get('base_dir')
            installer = sample_library_config.get('installer')
            extract_subdirs = sample_library_config.get('extract_subdirs', {})

        sample_libraries_config[name] = SampleLibraryConfig(base_dir, installer, extract_subdirs)

    for library in sample_libraries_config:
        printer.info(f'Processing {library}')

        # Find the source directory for the library
        library_paths = elite.find(
            path=sample_library_source, min_depth=2, max_depth=2, types=['directory'],
            patterns=[f'*/{library}']
        )

        if len(library_paths.paths) != 1:
            elite.fail('unable to find sample library source directory')

        library_path = library_paths.paths[0]

        # Find all ZIP and RAR files present in the downloaded library
        archives = elite.find(path=library_path, types=['file'], patterns=['*.zip', '*.rar'])
        if not archives.paths:
            elite.fail('no archives were found in the sample library source directory')

        # Obtain the config for the current library
        library_config = sample_libraries_config[library]

        # Build the destination base directory
        destination_base_dir = os.path.join(
            config.sample_library_dir, os.path.relpath(library_path, sample_library_source)
        )

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

            # Extract the archive
            elite.file(path=destination, state='directory')
            elite.archive(
                path=destination,
                source=archive,
                ignore_files=['__MACOSX', '.DS_Store'],
                base_dir=library_config.base_dir,
                preserve_mode=False
            )

        # Run the installer package if required
        if library_config.installer:
            elite.package(path=os.path.join(destination, library_config.installer), sudo=True)


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

    logic_pro_x_content(elite, config, printer, sample_library_source)
    komplete_libraries(elite, config, printer, sample_library_source)
    omnisphere_steam_library(elite, config, printer, music_software_source)
    kontakt_libraries_and_drum_samples(elite, config, printer, sample_library_source)


if __name__ == '__main__':
    main()
