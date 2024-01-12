#!/usr/bin/env python3


import argparse
import json


def get_arguments():
    parser = argparse.ArgumentParser(
            description='Tries to identify if there is a problem with a'
                        ' JSON file and if there is, the location of'
                        ' that error.')
    parser.add_argument('input_file', help='FQPN to the input file.')
    return parser.parse_args()


if __name__ == '__main__':

    args = get_arguments()
    with open(args.input_file, 'r') as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError as err:
            print(f'JSONDecodeError: {err}')
