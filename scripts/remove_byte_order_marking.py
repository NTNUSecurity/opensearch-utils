#!/usr/bin/env python3

"""
This script will remove the BOM at the 3 first bytes in a file, if it
exist. The reason for doing this on templates if it has a BOM is that
the OpenSearch REST API errors out. Why, I do not know.
"""

import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
            description='Remove byte order marking (BOM) from a file.')
    parser.add_argument('input_file', help='FQPN to the input file.')
    parser.add_argument('output_file', help='FQPN to the output file.')
    return parser.parse_args()


def remove_bom(input_file, output_file):
    with open(input_file, 'rb') as ifp:
        # Read the first 3 bytes to check for BOM.
        bom = ifp.read(3)
        if bom != b'\xef\xbb\xbf':
            print('No BOM found.')
        else:
            print('BOM (UTF-8) found. Removing…')
            with open(output_file, 'wb') as ofp:
                # Write the content of the file (excluding the BOM) to
                # the output file.
                ifp.seek(3)
                ofp.write(ifp.read())


if __name__ == '__main__':
    args = get_arguments()
    remove_bom(args.input_file, args.output_file)
