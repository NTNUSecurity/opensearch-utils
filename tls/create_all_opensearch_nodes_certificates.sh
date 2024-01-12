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
mkdir -v -p NODES

# Create the node certificates
for host in $HOSTS
do
    echo "Creating certificate and key for host -> $host."
    openssl genrsa \
        -out ./NODES/$host.key.pem $CERTIFICATE_KEY_SIZE
    openssl pkcs8 \
        -inform PEM \
        -outform PEM \
        -in ./NODES/$host.key.pem \
        -topk8 \
        -nocrypt \
        -v1 PBE-SHA1-3DES \
        -out ./NODES/$host.key.pkcs8
    openssl req \
        -new \
        -key ./NODES/$host.key.pkcs8 \
        -subj "$SUBJECT_PREFIX/CN=$host" \
        -out ./NODES/$host.csr.pem
    echo "subjectAltName=DNS:$host" > ./NODES/$host.ext
    openssl x509 \
        -req \
        -in ./NODES/$host.csr.pem \
        -CA ./CA/opensearch-root-ca.crt.pem \
        -CAkey ./CA/opensearch-root-ca.key.pem \
        -CAcreateserial \
        -sha256 \
        -out ./NODES/$host.crt.pem \
        -days $CERTIFICATE_EXPIRE_IN \
        -extfile ./NODES/$host.ext
done

# When done creating all the needed certificates, we list the subjects of each certificate so that it can be put in the OpenSearch configuration.
echo
echo
echo "plugins.security.nodes_dn:"
for host in $HOSTS
do
    echo "  - '$(openssl x509 -noout -in ./NODES/$host.crt.pem -subject -nameopt RFC2253 | cut -d "=" -f 2-)'"
done
echo
echo "plugins.security.authcz.admin_dn:"
echo "  - '$(openssl x509 -noout -in ./ADMIN/opensearch-admin.crt.pem -subject -nameopt RFC2253 | cut -d "=" -f 2-)'"
echo
echo
echo "Fini!"
