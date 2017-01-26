#!/usr/bin/env python3
import os
import re
import tempfile
import yaml

from elite.decorators import elite_main


def logic_pro_x_content(elite, config, printer, sample_library_source):
    printer.heading('Logic Pro X Content')

    source = os.path.join(sample_library_source, 'Apple', 'Apple Logic Pro X Sound Library')
    destination = os.path.join(config.sample_library_dir, 'Apple', 'Logic Pro X Sound Library')

    printer.info(f'Building directory structure and symlinks for content.')
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

    printer.info(f'Installing Logic Pro X content packages.')
    packages = elite.find(path=source, types=['file'], patterns=['*.pkg'])
    for package in packages.paths:
        elite.package(path=package, sudo=True)


def komplete_libraries(elite, config, printer, sample_library_source):
    printer.heading('Komplete Libraries')

    source = os.path.join(sample_library_source, 'Native Instruments')
    destination = os.path.join(config.sample_library_dir, 'Native Instruments')

    printer.info(f'Building directory structure for content.')
    elite.file(path=destination, state='directory')

    isos = elite.find(path=source, types=['file'], patterns=['*.iso'])
    for iso in isos.paths:
        package_name = os.path.splitext(os.path.basename(iso))[0].replace('_', ' ')
        printer.info(f'Installing Native Instruments {package_name}.')

        mount_proc = elite.run(command=f'hdiutil mount "{iso}"')
        mountpoint = mount_proc.stdout.rstrip().split('\t')[-1]

        packages = elite.find(path=mountpoint, patterns=['* Installer Mac.pkg'])

        if len(packages.paths) != 1:
            elite.fail(
                message=f'Unable to determine the installer package for this library, skipping'
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
                f'Unable to identify install location choice identifier '
                f'for this library, skipping'
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

    elite.run(command=f'chflags hidden "{config.sample_library_dir}/Library"')


def omnisphere_steam_library(elite, config, printer, music_software_source):
    printer.heading('Spectrasonics STEAM Library')

    source = os.path.join(
        music_software_source, 'Spectrasonics/Spectrasonics Omnisphere v2/STEAM/'
    )
    destination = os.path.join(config.sample_library_dir, 'Spectrasonics')
    steam_symlink = f'~/Library/Application Support/Spectrasonics/STEAM'

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


def kontakt_libraries_and_drum_samples(elite, config, printer, sample_libraries_source):
    library_paths = elite.find(
        path=sample_libraries_source, min_depth=2, max_depth=2, types=['directory']
    )

    for library_path in library_paths.paths:
        # Find all ZIP and RAR files present in the downloaded library
        archives = elite.find(path=library_path, types=['file'], patterns=['*.zip', '*.rar'])

        if not archives.paths:
            continue

        # Determine the vendor of the library
        vendor = os.path.basename(os.path.dirname(library_path))

        # Determine the library name and remove the vendor name to remove redundancy
        library = os.path.basename(library_path)
        if library.startswith(f'{vendor} '):
            library = library[len(f'{vendor} '):]

        # Build the destination base directory
        destination = os.path.join(config.sample_library_dir, vendor, library)

        printer.info(f'Processing {vendor} {library}')

        # If present, read the library config to override library variables
        library_config_path = os.path.join(library_path, '.library.yaml')
        library_config = {}

        if os.path.isfile(library_config_path):
            printer.info(f'Loading the library YAML config file')
            with open(library_config_path) as f:
                try:
                    library_config = yaml.load(f)
                except yaml.scanner.ScannerError:
                    printer.info(
                        f'Unable to load the library config file due to a syntax error'
                    )

        base_dir = library_config.get('base_dir', '')
        installer = library_config.get('installer', None)
        extract_subdirs = library_config.get('extract_subdirs', [])

        if base_dir and os.path.isdir(destination) and os.listdir(destination):
            printer.info(f'Moving contents from base directory of {base_dir}')

            tempdir = tempfile.mkdtemp(prefix='samplelibs.', dir=config.sample_library_dir)
            elite.run(command=f'mv "{destination}/"* "{tempdir}"', shell=True)
            elite.file(path=os.path.join(destination, base_dir), state='directory')
            elite.run(command=f'mv "{tempdir}/"* "{destination}/{base_dir}/"', shell=True)
            elite.run(command=f'rmdir "{tempdir}"')

        printer.info(f'Extracting library archives')

        for archive in archives.paths:
            # Check for multipart archives and only extract part 1
            if (
                re.search('\.part[0-9]+\.rar$', archive) and
                not re.search('\.part0*1\.rar$', archive)
            ):
                continue

            # Determine the destination (also taking into account sub-directories)
            archive_relative = archive.replace(f'{library_path}/', '')
            subdir = os.path.dirname(archive_relative)
            if subdir == '.':
                subdir = ''

            if archive_relative in extract_subdirs:
                subdir = os.path.join(subdir, base_dir, extract_subdirs[archive_relative])

            destination_subdir = os.path.join(destination, subdir) if subdir else destination

            elite.file(path=destination_subdir, state='directory')

            if os.path.splitext(archive)[1] == '.rar':
                elite.run(command=(
                    f'unrar x -o+ -x"__MACOSX" -x"*.DS_Store" "{archive}" "{destination_subdir}"'
                ))
            else:
                elite.run(command=(
                    f'unzip -q -o "{archive}" -x "__MACOSX/*" "*.DS_Store" '
                    f'-d "{destination_subdir}"'
                ))

        if base_dir:
            if os.path.isdir(os.path.join(destination, base_dir)):
                elite.run(command=f'mv "{destination}/{base_dir}/"* "{destination}/"', shell=True)
                elite.run(command=f'rmdir "{destination}/{base_dir}/"')

        if installer:
            elite.package(path=os.path.join(destination, installer), sudo=True)


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
    # komplete_libraries(elite, config, printer, sample_library_source)
    omnisphere_steam_library(elite, config, printer, music_software_source)


if __name__ == '__main__':
    main()
