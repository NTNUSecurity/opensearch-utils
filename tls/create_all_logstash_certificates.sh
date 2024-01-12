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
mkdir -v -p LOGSTASH

# Create the node certificates
for host in $HOSTS
do
    echo "Creating certificate and key for host -> $host."
    openssl genrsa \
        -out ./LOGSTASH/$host.key.pem $CERTIFICATE_KEY_SIZE
    openssl pkcs8 \
        -inform PEM \
        -outform PEM \
        -in ./LOGSTASH/$host.key.pem \
        -topk8 \
        -nocrypt \
        -v1 PBE-SHA1-3DES \
        -out ./LOGSTASH/$host.key.pkcs8
    openssl req \
        -new \
        -key ./LOGSTASH/$host.key.pkcs8 \
        -subj "$SUBJECT_PREFIX/CN=$host" \
        -out ./LOGSTASH/$host.csr.pem
    echo "subjectAltName=DNS:$host" > ./LOGSTASH/$host.ext
    openssl x509 \
        -req \
        -in ./LOGSTASH/$host.csr.pem \
        -CA ./CA/opensearch-root-ca.crt.pem \
        -CAkey ./CA/opensearch-root-ca.key.pem \
        -CAcreateserial \
        -sha256 \
        -out ./LOGSTASH/$host.crt.pem \
        -days $CERTIFICATE_EXPIRE_IN \
        -extfile ./LOGSTASH/$host.ext
done
echo "Fini!"
