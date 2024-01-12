# OpenSearch scripts/utils

This repository contains misc. python scripts to help get information
from OpenSearch or administrate/make changes to OpenSearch.

## Dependencies
Dependencies can be installed with the following command from the root
directory.

``` bash
pip3 install -r requirements.txt
```

## Scripts

### scripts/get_stats.py
Gets information about the OpenSearch cluster and prints it to screen.

You need a privileged account to run this. It is possible to run this
script without a privileged account. The user will then need to be in a
role, where the role has been given the correct permissions. What those
permissions are, is unknown to me at this moment.

``` bash
:~/opensearch-utils# ./scripts/get_stats.py --help
usage: get_stats.py [-h] --host HOST [--port PORT] [--schema SCHEMA] [--certlocation CERTLOCATION] [--username USERNAME]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           The host to connect to.
  --port PORT           The port to connect to.
  --schema SCHEMA       The schema to use with the request.
  --certlocation CERTLOCATION
                        The location to where CA, certificates and keys are stored.
  --username USERNAME   The username for any requests.
```
  
### scripts/push_template.py
Pushes component or composable templates to OpenSearch.

``` bash
~/opensearch-utils# ./scripts/push_template.py --help
usage: push_template.py [-h] (--composable | --component) -t TEMPLATE [--host HOST] [--port PORT] [--ca CA]

optional arguments:
  -h, --help            show this help message and exit
  --composable          Upload as a composable index template
  --component           Upload as a component template
  -t TEMPLATE, --template TEMPLATE
                        FQPN to the template file to push to OpenSearch
  --host HOST           FQHN to the host which to send the template to
  --port PORT           The port which to send data to OpenSearch on
  --ca CA               FQPN to CA certificate
```

### scripts/remove_byte_order_marking.py
This script simply removes the UTF BOM from the beginning of a file
providing there is one in the file. I had an issue once, where I was
getting errors when trying to upload a template to OpenSearch. The
solution was to remove the BOM from the template file.

I never understood the reason for why removing the BOM worked and I
have not used it since.

``` bash
:~/opensearch-utils# scripts/remove_byte_order_marking.py --help
usage: remove_byte_order_marking.py [-h] input_file output_file

Remove byte order marking (BOM) from a file.

positional arguments:
  input_file   FQPN to the input file.
  output_file  FQPN to the output file.

optional arguments:
  -h, --help   show this help message and exit
```

### scripts/try_to_identify_json_error_location.py
The script tries to load a file containing JSON, if it fails, it prints
the error on screen.

I was having problems when trying to execute REST API commands against
OpenSearch and I was speculating that my JSON was erronous, but the
error message did not tell me that.

So I created this script, so that I could try to load the JSON in
something that was not OpenSearch to see if I got an error message which
was more informative. It was, at the time I wrote this.

``` bash
:~/opensearch-utils# scripts/try_to_identify_json_error_location.py --help
usage: try_to_identify_json_error_location.py [-h] input_file

Tries to identify if there is a problem with a JSON file and if there is, the location of that error.

positional arguments:
  input_file  FQPN to the input file.

optional arguments:
  -h, --help  show this help message and exit
```
