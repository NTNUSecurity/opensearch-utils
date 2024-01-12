# OpenSearch TLS dummy certificate scripts
These script will create a certificate authority and use that CA to
create certificates and keys for the admin user and any nodes that
belong to the cluster.

The script does not create a certificate authority which is password
protected, which is not a good thing. So do not use the script directly
in anything that goes in production. Instead, use the scripts as
inspiration for creating a CA, admin certificates and node certificates.

## Dependencies
OpenSSL has to be installed on the computer for this to work.

## Copy, paste

Before running the commands below, in the order they are listen. Edit
each file so that subject prefix, expire data, key size and hosts are correct.

See the comments in the script for how to write the subject prefix.

``` verbatim
SUBJECT_PREFIX=""
CERTIFICATE_EXPIRE_IN=
CERTIFICATE_KEY_SIZE=
HOSTS=""
```

After edit of the script, run it and directories/files will be created.

``` bash
sh create_ca_and_admin_certificates.sh 
sh create_all_opensearch_nodes_certificates.sh
sh create_all_dashboards_certificates.sh
sh create_all_logstash_certificates.sh
```
