#!/usr/bin/env bash
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

set -e
set +x

raw_key=$1

ASN1_PRIV_KEY_HEADER="302e0201010420"
ASN1_SECP256K1_OID="a00706052b8104000a"
OUT_FILE="priv_key.pem"

if [ -z "${raw_key}" ]; then
  echo "Usage: $1 $0 <private_key>"
  exit 1
fi

openssl ec -inform DER -out "${OUT_FILE}" -in <(echo "${ASN1_PRIV_KEY_HEADER} ${raw_key} ${ASN1_SECP256K1_OID}" | xxd -r -p) &>/dev/null
printf "private key successfully written to: %s\n" "${OUT_FILE}"

#printf "asn1parse output:\n"
#openssl asn1parse -in "${OUT_FILE}"
