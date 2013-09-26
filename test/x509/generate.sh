#!/bin/bash
CERTDIR=certs
CFGDIR=`pwd`

CACFG=$CFGDIR/ca.cfg
CERTCFG=$CFGDIR/cert.cfg

mkdir -p $CERTDIR
cd $CERTDIR

# create two Certificate Authorities
NAME=CA1
openssl req -config $CACFG -new -x509 -keyout ${NAME}.rsa -out ${NAME}.crt -days 1825
NAME=CA2
openssl req -config $CACFG -new -x509 -keyout ${NAME}.rsa -out ${NAME}.crt -days 1825

# create three Certificates with signature requests
NAME=CERT1A
openssl req -config $CERTCFG -new -keyout ${NAME}.rsa -out ${NAME}.csr
NAME=CERT1B
openssl req -config $CERTCFG -new -keyout ${NAME}.rsa -out ${NAME}.csr
NAME=CERT2
openssl req -config $CERTCFG -new -keyout ${NAME}.rsa -out ${NAME}.csr

# sign three Certificates by CAs
NAME=CERT1A
CA=CA1
openssl x509 -req -extfile ../v3ext.cfg -extensions v3e -in ${NAME}.csr -CA ${CA}.crt -CAkey ${CA}.rsa -CAcreateserial -out ${NAME}.crt
NAME=CERT1B
openssl x509 -req -extfile ../v3ext.cfg -extensions v3e -in ${NAME}.csr -CA ${CA}.crt -CAkey ${CA}.rsa -CAcreateserial -out ${NAME}.crt
NAME=CERT2
CA=CA2
openssl x509 -req -extfile ../v3ext.cfg -extensions v3e -in ${NAME}.csr -CA ${CA}.crt -CAkey ${CA}.rsa -CAcreateserial -out ${NAME}.crt
