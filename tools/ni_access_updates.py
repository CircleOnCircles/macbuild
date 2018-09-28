#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from collections import defaultdict
from glob import glob


ISO_BASE_DIRS = [
    '/Volumes/Backup Mac 1/Software',
    '/Volumes/Backup Mac 2/Software',
    '/Volumes/Software Archive',
]

ISO_SUBDIRS = [
    'Music Production/Native Instruments',
    'Sample Libraries/Native Instruments Battery',
    'Sample Libraries/Native Instruments Kontakt/Native Instruments',
]

IGNORED_NAMES = [
    # Superseeded by Scarbee Vintage Keys
    'Scarbee A-200',
    'Scarbee Clavinet Pianet',
    'Scarbee Mark I',
    # Superseeded by Session Strings Pro
    'Session Strings',
]


class Error(Exception):
    pass


def get_native_access_versions():
    native_access_log_path = os.path.expanduser(
        '~/Library/Caches/Native Instruments/Native Access/NativeAccess_1.log'
    )

    versions = defaultdict(str)

    try:
        with open(native_access_log_path) as fp:
            for line in fp:
                # pylint: disable=line-too-long
                # We are searching for lines like this:
                # [20180908 12:21:09.070 D] 932986 Download available  "36917e64-fdef-4fd6-b210-f0d004c70901 7aea8f0e-b5be-4394-8f23-8d04091890e8 West Africa 1.3.0 (1.3.0.3) Full Product 2015-04-29 "  # noqa: E501
                # pylint: enable=line-too-long
                match = re.match(r'^.* Download available  "\S+ \S+ (.*) ((?:\d|\.)+) .*$', line)
                if not match:
                    continue

                name, version = match.groups()

                if name in IGNORED_NAMES:
                    continue

                if version > versions[name]:
                    versions[name] = version
    except OSError:
        raise Error(f'unable to read the Native Access log path {native_access_log_path}')

    if not versions:
        raise Error(
            'unable to find versions in the Native Access log file, please start Native Access '
            'and sign in and try again'
        )

    return versions


def get_downloaded_versions():
    iso_base_dirs = filter(os.path.exists, ISO_BASE_DIRS)

    try:
        iso_base_dir = next(iso_base_dirs)
    except StopIteration:
        raise Error('none of te specified ISO base directories exist')

    isos = []
    for iso_subdir in ISO_SUBDIRS:
        iso_glob = os.path.join(iso_base_dir, iso_subdir, '*.iso')
        isos.extend(glob(iso_glob))

    if not isos:
        raise Error(f'no ISO images were found in {iso_base_dir}')

    versions = {}

    for iso in isos:
        try:
            output = subprocess.check_output(['7z', 'l', iso], encoding='utf-8')
        except OSError:
            raise Error(
                'you appear to be missing the 7z executable, install with "brew install p7zip"'
            )
        except subprocess.SubprocessError:
            raise Error(f'unable to obtain a listing of the ISO {iso}')

        output_files = filter(lambda l: 'Installer Mac' in l, output.split('\n'))
        try:
            mac_installer_line = next(output_files)
        except StopIteration:
            raise Error(f'unable to find any installers in the ISO {iso}')

        match = re.match(r'^.*  (.*) ((?:\d|\.)+) .*$', mac_installer_line)
        if not match:
            raise Error(f'unable to parse the name and version from line: {mac_installer_line}')

        name, version = match.groups()

        # Strip major versions from names (e.g. Reaktor 6, Battery 4 .etc)
        major_version = version.split('.')[0]
        if name.endswith(f' {major_version}'):
            name = name.rsplit(f' {major_version}', 1)[0]

        versions[name] = version

    return versions


def main():
    try:
        native_access_versions = get_native_access_versions()
        downloaded_versions = get_downloaded_versions()
    except Error as e:
        print(f'Error: {str(e)}')
        sys.exit(1)

    print()
    print('-= Updates Available in Native Access =-')
    print()
    for name, native_access_version in sorted(native_access_versions.items()):
        downloaded_version = downloaded_versions.pop(name, None)
        if native_access_version != downloaded_version:
            print('*', name, downloaded_version, '=>', native_access_version)

    if downloaded_versions:
        print()
        print('-= Downloaded Software Unavailable in Native Access =-')
        print()
        for name, downloaded_version in sorted(downloaded_versions.items()):
            print('*', name, downloaded_version)

    print()


if __name__ == '__main__':
    main()
