#!/bin/bash
CERTDIR=certs
CFGDIR=`pwd`

CACFG=$CFGDIR/ca.cfg
CERTCFG=$CFGDIR/cert.cfg

mkdir -p $CERTDIR
cd $CERTDIR

# create two Certificate Authorities
NAME=CA1
openssl req -config $CACFG -new -x509 -keyout ${NAME}.ca.rsa -out ${NAME}.ca.crt -days 1825
NAME=CA2
openssl req -config $CACFG -new -x509 -keyout ${NAME}.ca.rsa -out ${NAME}.ca.crt -days 1825

# create three Certificates
NAME=CERT1A
openssl req -config $CERTCFG -new -keyout ${NAME}.rsa -out ${NAME}.req
NAME=CERT1B
openssl req -config $CERTCFG -new -keyout ${NAME}.rsa -out ${NAME}.req
NAME=CERT2
openssl req -config $CERTCFG -new -keyout ${NAME}.rsa -out ${NAME}.req

# sign three Certificates by CAs
NAME=CERT1A
CA=CA1
openssl x509 -req -in ${NAME}.req -CA ${CA}.ca.crt -CAkey ${CA}.ca.rsa -CAcreateserial -out ${NAME}.crt
NAME=CERT1B
openssl x509 -req -in ${NAME}.req -CA ${CA}.ca.crt -CAkey ${CA}.ca.rsa -CAcreateserial -out ${NAME}.crt
NAME=CERT2
CA=CA2
openssl x509 -req -in ${NAME}.req -CA ${CA}.ca.crt -CAkey ${CA}.ca.rsa -CAcreateserial -out ${NAME}.crt
