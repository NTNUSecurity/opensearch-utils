#!/bin/bash

# Subject prefix example: "/C=<2 CHARACATER COUNTRY CODE>/ST=<STATE>/O=<COMPANY NAME WITH SPACES>/OU=<ORGANIZATIONAL UNIT>"
SUBJECT_PREFIX=""
# Certificate expiration in days from today.
CERTIFICATE_EXPIRE_IN=
# Certificate key size
CERTIFICATE_KEY_SIZE=

# A space separated list of FQDN for each host (node) in the cluster.
# Example: HOSTS="node1.foo.bar.baz node2.foo.bar.baz"
HOSTS=""

# Create the needed directories
mkdir -v -p DASHBOARDS

# Create the node certificates
for host in $HOSTS
do
    echo "Creating certificate and key for host -> $host."
    openssl genrsa \
        -out ./DASHBOARDS/$host.key.pem $CERTIFICATE_KEY_SIZE
    openssl pkcs8 \
        -inform PEM \
        -outform PEM \
        -in ./DASHBOARDS/$host.key.pem \
        -topk8 \
        -nocrypt \
        -v1 PBE-SHA1-3DES \
        -out ./DASHBOARDS/$host.key.pkcs8
    openssl req \
        -new \
        -key ./DASHBOARDS/$host.key.pkcs8 \
        -subj "$SUBJECT_PREFIX/CN=$host" \
        -out ./DASHBOARDS/$host.csr.pem
    echo "subjectAltName=DNS:$host" > ./DASHBOARDS/$host.ext
    openssl x509 \
        -req \
        -in ./DASHBOARDS/$host.csr.pem \
        -CA ./CA/opensearch-root-ca.crt.pem \
        -CAkey ./CA/opensearch-root-ca.key.pem \
        -CAcreateserial \
        -sha256 \
        -out ./DASHBOARDS/$host.crt.pem \
        -days $CERTIFICATE_EXPIRE_IN \
        -extfile ./DASHBOARDS/$host.ext
done
echo "Fini!"
