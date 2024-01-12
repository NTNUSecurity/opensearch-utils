#!/usr/bin/env python3

"""
Script that will push a template to OpenSearch. This script assumes
that it is run on the same host it sends the template to.
"""


import argparse
import getpass
import requests
import sys


def get_args():
    """Function that will parse command line arguments and pass them to the script."""
    parser = argparse.ArgumentParser()

    # The template needs to be a component or composable template, not a legacy template.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--composable", default=False, action="store_true", help="Upload as a composable index template")
    group.add_argument("--component", default=False, action="store_true", help="Upload as a component template")

    parser.add_argument("-t", "--template", type=str, required=True, help="FQPN to the template file to push to OpenSearch")
    parser.add_argument("--host", type=str, default="lm-osmastertest01.it.ntnu.no", help="FQHN to the host which to send the template to")
    parser.add_argument("--port", type=int, default=9200, help="The port which to send data to OpenSearch on")
    parser.add_argument("--ca", type=str, default="/etc/opensearch/private/ca.pem", help="FQPN to CA certificate")
    return parser.parse_args()


if __name__ == "__main__":

    ARGS = get_args()
    try:
        fp = open(ARGS.template, "r")
    except IOError:
        print("Template file not found or is not readable.")
        sys.exit(1)

    template_name = ARGS.template.split("/")[-1:][0].split(".template.json")[0]

    username = input("Username: ")
    try:
        password = getpass.getpass("Password: ")
    except getpass.GetPassWarning:
        print("Cannot guarantee that the password is not echoed to screen. Forced exit!")
        sys.exit(1)

    print("The following will be done:")
    print(f"\tTemplate file to send:                             {ARGS.template}")
    print(f"\tName of template on OpenSearch:                    {template_name}")
    print(f"\tOpenSearch host to send template to:               {ARGS.host}")
    print(f"\tUsername to authorize creation/update of template: {username}")
    print
    answer = input("Continue? (y/n): ")
    if answer.lower() != "y" and answer.lower() != "yes":
        print("Aborting!")
        sys.exit(0)

    if ARGS.composable:
        URL = f"https://{ARGS.host}:{ARGS.port}/_index_template/{template_name}"
    else:
        URL = f"https://{ARGS.host}:{ARGS.port}/_component_template/{template_name}"
    headers = {"Content-Type": "application/json",}
    cert = (f"/etc/opensearch/private/{ARGS.host}.crt.pem", f"/etc/opensearch/private/{ARGS.host}.key.pem")
    response = requests.put(URL, headers=headers, data=fp, verify=ARGS.ca, cert=cert, auth=(username, password))
    fp.close()

    if response.status_code == 200:
      print("Success!")
      sys.exit(0)

    # If the response returns anything else than 200. Print the status code and error message.
    print(f"Response status code: {response.status_code}")
    print(f"Response text: \n\n{response.text}")
    print
