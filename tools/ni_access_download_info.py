#!/usr/bin/env python3
import glob
import sys
from collections import namedtuple
from xml.etree import ElementTree


NIDownload = namedtuple(
    'NIDownload', ('metadata_path', 'filename', 'size', 'md5', 'sha256', 'url')
)


def main():
    md5sums = False
    if len(sys.argv) > 1 and sys.argv[1] == '-m':
        md5sums = True

    shasums = set()
    namespaces = {'meta': 'urn:ietf:params:xml:ns:metalink'}

    if not md5sums:
        print()

    downloads = []

    for metadata_path in glob.glob('/var/folders/*/*/*/*.meta4'):
        with open(metadata_path) as f:
            metadata_xml = ElementTree.parse(f)

            # Obtain required data
            filename = metadata_xml.find('./meta:file', namespaces=namespaces).attrib['name']
            size = metadata_xml.find('./meta:file/meta:size', namespaces=namespaces).text
            md5 = metadata_xml.find(
                './meta:file/meta:hash[@type="md5"]', namespaces=namespaces).text
            sha256 = metadata_xml.find(
                './meta:file/meta:hash[@type="sha-256"]', namespaces=namespaces).text
            url = metadata_xml.find('./meta:file/meta:url', namespaces=namespaces).text

            # Skip duplicates based on checksum
            if sha256 in shasums:
                continue
            shasums.add(sha256)

            # Add the dowload to our list
            downloads.append(NIDownload(metadata_path, filename, size, md5, sha256, url))

    for metadata_path, filename, size, md5, sha256, url in sorted(
        downloads, key=lambda i: i.filename
    ):
        # Print download information
        if md5sums:
            print('{}  {}'.format(md5, filename))
        else:
            print('{:8} : {}'.format('Metadata', metadata_path))
            print('{:8} : {}'.format('Filename', filename))
            print('{:8} : {:,d} bytes'.format('Size', int(size)))
            print('{:8} : {}'.format('MD5', md5))
            print('{:8} : {}'.format('SHA-256', sha256))
            print('{:8} : {}'.format('URL', url))
            print()


if __name__ == '__main__':
    main()
