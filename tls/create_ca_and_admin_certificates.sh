#!/bin/bash

# Subject prefix example: "/C=<2 CHARACATER COUNTRY CODE>/ST=<STATE>/O=<COMPANY NAME WITH SPACES>/OU=<ORGANIZATIONAL UNIT>"
SUBJECT_PREFIX="/C=NO/ST=Innlandet/O=NTNU/OU=DS"
# Certificate expiration in days from today.
CERTIFICATE_EXPIRE_IN=3650
# Certificate key size
CERTIFICATE_KEY_SIZE=4096

# Create the needed directories
mkdir -v -p ADMIN CA

# Create the ROOT CA
echo "Creating root CA."
openssl genrsa \
    -out ./CA/opensearch-root-ca.key.pem $CERTIFICATE_KEY_SIZE
openssl req \
    -new \
    -x509 \
    -sha256 \
    -key ./CA/opensearch-root-ca.key.pem \
    -subj "$SUBJECT_PREFIX/CN=ROOT" \
    -out ./CA/opensearch-root-ca.crt.pem \
    -days $CERTIFICATE_EXPIRE_IN

# Create the admin certificate
echo "Creating admin certificate and key."
openssl genrsa \
    -out ./ADMIN/opensearch-admin.key.pem $CERTIFICATE_KEY_SIZE
openssl pkcs8 \
    -inform PEM \
    -outform PEM \
    -in ./ADMIN/opensearch-admin.key.pem \
    -topk8 \
    -nocrypt \
    -v1 PBE-SHA1-3DES \
    -out ./ADMIN/opensearch-admin.key.pkcs8
openssl req \
    -new \
    -key ./ADMIN/opensearch-admin.key.pem \
    -subj "$SUBJECT_PREFIX/CN=OpenSearch Admin" \
    -out ./ADMIN/opensearch-admin.csr.pem
openssl x509 \
    -req \
    -in ./ADMIN/opensearch-admin.csr.pem \
    -CA ./CA/opensearch-root-ca.crt.pem \
    -CAkey ./CA/opensearch-root-ca.key.pem \
    -CAcreateserial \
    -sha256 \
    -out ./ADMIN/opensearch-admin.crt.pem \
    -days $CERTIFICATE_EXPIRE_IN
openssl x509 \
    -req \
    -in ADMIN/opensearch-admin.csr.pem \
    -CA CA/opensearch-root-ca.crt.pem \
    -CAkey CA/opensearch-root-ca.key.pem \
    -CAcreateserial \
    -sha256 \
    -out ./ADMIN/opensearch-admin.crt.pem \
    -days $CERTIFICATE_EXPIRE_IN

echo "Fini!"
