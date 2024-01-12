#!/usr/bin/env python3

"""
A script that will give you some stats about storage on a cluster.

The reason for this script to exist is that it is a little bit
difficult to get an overview of the storage situation when there
are many nodes.

This means it becomes harder to evaluate if we are ok or not and
what the chances are we hit the low/high/flood_stage watermarks
ref. https://opensearch.org/docs/2.2/api-reference/cluster-api/cluster-settings/
"""


# TODO: Create stats for datastreams as well.
# TODO: When there are unassigned shards, output that to screen as well.


import argparse
import getpass
import re
import requests
import sys


def convertToBytes(data):
    assert isinstance(data, str)
    # Normalize the data.
    data = data.lower().strip().replace(" ", "")

    if "tb" in data:
        data = data.replace("tb", "")
        data = float(data)*1024**4
    elif "gb" in data:
        data = data.replace("gb", "")
        data = float(data)*1024**3
    elif "mb" in data:
        data = data.replace("mb", "")
        data = float(data)*1024**2
    elif "kb" in data:
        data = data.replace("kb", "")
        data = float(data)*1024

    return data


def convertToString(data):
    """This function will convert data to strings with 2 decimal places."""
    assert isinstance(data, int)

    if data > 1024**4:
        return f"{data/1024**4:.2f}TB"
    elif data > 1024**3:
        return f"{data/1024**3:.2f}GB"
    elif data > 1024**2:
        return f"{data/1024**2:.2f}MB"
    elif data > 1024:
        return f"{data/1024:.2f}KB"
    else:
        return f"dataB"

def get(args, path, query=None):
    assert isinstance(path, str)
    assert path.startswith("/")
    if query:
        assert isinstance(query, str)
        assert query.startswith("?")

    if query:
        url = "{0}://{1}:{2}{3}{4}".format(args.schema, args.host, args.port, path, query)
    else:
        url = "{0}://{1}:{2}{3}".format(args.schema, args.host, args.port, path)
    headers = {"Content-Type": "application/json",}
    cert = (f"{args.certlocation}/{args.host}.crt.pem", f"{args.certlocation}/{args.host}.key.pem")

    response = requests.get(url, headers=headers, verify=f"{args.certlocation}/ca.pem", cert=cert, auth=(f"{args.username}", f"{args.password}"))
    response.raise_for_status()
    return response


def getAllocationStats(args):
    response = get(args, "/_cat/allocation").text.strip().split("\n")
    #[[shards,disk.indices,disk.used,disk.avail,disk.total,disk.percent,host,ip,node],]
    data = [Node(re.sub("\s+", ",", line.strip()).split(",")) for line in response]
    return data


def getArgs():
    """Function that will retrieve command line arguments and return them."""
    parser = argparse.ArgumentParser()
    # Required
    parser.add_argument("--host", type=str, required=True, help="The host to connect to.")
    # Has defaults.
    parser.add_argument("--port", type=int, required=False, default=9200, help="The port to connect to.")
    parser.add_argument("--schema", type=str, required=False, default="https", help="The schema to use with the request.")
    parser.add_argument("--certlocation", type=str, required=False, default="/etc/opensearch/private", help="The location to where CA, certificates and keys are stored.")
    parser.add_argument("--username", type=str, required=False, default="", help="The username for any requests.")
    return parser.parse_args()


def getWatermarkSettings(args):
    data = get(args, "/_cluster/settings", "?include_defaults").json()
    ret = {}
    for key in ["defaults", "persistent", "transient"]:
        try:
            ret[key] = data[key]["cluster"]["routing"]["allocation"]["disk"]["watermark"]
            for wm in ret[key]:
                ret[key][wm] = ret[key][wm].replace("%", "")
        except KeyError:
            ret[key] = None
    return ret


def printAllocationStats(nodes):

    print()
    print()
    print("----- General disk statistics -----")
    print()

    shards_total = sum([node.shards for node in nodes])
    space_used_indices = convertToString(sum([node.diskUsedByIndices for node in nodes]))
    space_used_total = convertToString(sum([node.diskUsedTotal for node in nodes]))
    space_available = convertToString(sum([node.diskAvailable for node in nodes]))
    space_total = convertToString(sum([node.diskTotal for node in nodes]))
    space_used_total_percent = sum([node.diskUsedPercent for node in nodes])/len(nodes)

    print("--- Total ---")
    print(f"Number of shards: {shards_total}")
    print(f"Space used by indices: {space_used_indices}")
    print(f"Space used by indices and other files: {space_used_total}")
    print(f"Space available: {space_available}")
    print(f"Space in cluster: {space_total}")
    print(f"Space used by indices and other files in percent: {space_used_total_percent:.2f}%")

    shards_total_hot = sum([node.shards for node in nodes if "hot" in node.host])
    space_used_indices_hot = convertToString(sum([node.diskUsedByIndices for node in nodes if "hot" in node.host]))
    space_used_total_hot = convertToString(sum([node.diskUsedTotal for node in nodes if "hot" in node.host]))
    space_available_hot = convertToString(sum([node.diskAvailable for node in nodes if "hot" in node.host]))
    space_total_hot = convertToString(sum([node.diskTotal for node in nodes if "hot" in node.host]))
    space_used_total_percent_hot = sum([node.diskUsedPercent for node in nodes if "hot" in node.host])/len([node for node in nodes if "hot" in node.host])

    print("--- Hot Nodes ---")
    print(f"Number of shards: {shards_total_hot}")
    print(f"Space used by indices: {space_used_indices_hot}")
    print(f"Space used by indices and other files: {space_used_total_hot}")
    print(f"Space available: {space_available_hot}")
    print(f"Space in cluster: {space_total_hot}")
    print(f"Space used by indices and other files in percent: {space_used_total_percent_hot:.2f}%")

    shards_total_warm = sum([node.shards for node in nodes if "hot" not in node.host])
    space_used_indices_warm = convertToString(sum([node.diskUsedByIndices for node in nodes if "hot" not in node.host]))
    space_used_total_warm = convertToString(sum([node.diskUsedTotal for node in nodes if "hot" not in node.host]))
    space_available_warm = convertToString(sum([node.diskAvailable for node in nodes if "hot" not in node.host]))
    space_total_warm = convertToString(sum([node.diskTotal for node in nodes if "hot" not in node.host]))
    space_used_total_percent_warm = sum([node.diskUsedPercent for node in nodes if "hot" not in node.host])/len([node for node in nodes if "hot" not in node.host])

    print("--- Warm Nodes ---")
    print(f"Number of shards: {shards_total_warm}")
    print(f"Space used by indices: {space_used_indices_warm}")
    print(f"Space used by indices and other files: {space_used_total_warm}")
    print(f"Space available: {space_available_warm}")
    print(f"Space in cluster: {space_total_warm}")
    print(f"Space used by indices and other files in percent: {space_used_total_percent_warm:.2f}%")


def printNodesWatermark(settings, nodes):

    print()
    print()
    print("----- Node Watermark info -----")
    print()
    print(" Information here will only be displayed if any of the nodes are above a watermark level.")
    print()
    print()

    # Since defaults are preceded by persistent settings and transient settings precedes these again,
    # we compare the fill percentage of each node with the setting that takes precedence.
    for skey in ["transient", "persistent", "defaults"]:
        if skey in settings and settings[skey]:
            key = skey
    for node in nodes:
        for wm in ["flood_stage", "high", "low"]:
            if node.diskUsedPercent >= int(settings[key][wm]):
                print("{0} -> Used storage percentage ({1}%) is above or equal to {2}:{3} watermark percentage ({4}%).".format(
                        node.host, node.diskUsedPercent, key, wm, settings[key][wm]))
                break


def printWatermarkSettings(settings):

    print()
    print()
    print("----- Watermark settings -----")
    print()

    for key in ["defaults", "persistent", "transient"]:
        print("--- {0} ---".format(key.title()))
        if key in settings and settings[key]:
            print("Low: {0}%".format(settings[key]["low"]))
            print("High: {0}%".format(settings[key]["high"]))
            print("Flood Stage: {0}%".format(settings[key]["flood_stage"]))
        else:
            print("No {0} settings set.".format(key))


class Node():

    """A class that represents a node in the cluster."""

    def __init__(self, data):
        assert isinstance(data, list)
        #[[shards,disk.indices,disk.used,disk.avail,disk.total,disk.percent,host,ip,node],]
        self.data = data
        if "UNASSIGNED" in data:
            return

        self.shards = int(data[0])
        self.diskUsedByIndices = int(convertToBytes(data[1]))
        self.diskUsedTotal = int(convertToBytes(data[2]))
        self.diskAvailable = int(convertToBytes(data[3]))
        self.diskTotal = int(convertToBytes(data[4]))
        self.diskUsedPercent = int(data[5])
        self.host = str(data[6])
        self.ip = str(data[7])
        self.node = str(data[8])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Node({self.data})"


if __name__ == "__main__":

    args = getArgs()
    if not args.username:
        args.username = input("Username: ")
    try:
        args.password = getpass.getpass("Password: ")
    except getpass.GetPassWarning as err:
        print("Cannot guarantee that the password is not echoed to screen. Forced exit!")
        print(f"ERROR: {err}")
        sys.exit(1)

    # Print warning about rounding errors.
    print()
    print()
    print("This script is not meant to be used for detailed disk usage information.")
    print("It was designed to help pin point storage issues in general and there")
    print("is for a fact, always rounding errors when calculating the sizes.")
    print("Keep this in mind when using it and confirm the numbers in OpenSearch.")

    # Getting general storage statistics and print them.
    nodes = getAllocationStats(args)
    printAllocationStats(nodes)

    # Getting watermark settings for comparison with each nodes storage usage and printing the conclusion.
    settings = getWatermarkSettings(args)
    printWatermarkSettings(settings)
    printNodesWatermark(settings, nodes)

    print()
    print()
    print("Fini!")
    print()
