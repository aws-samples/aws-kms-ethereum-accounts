#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import logging
import os

from lambda_helper import (assemble_tx,
                           get_params,
                           get_tx_params,
                           calc_eth_address,
                           get_kms_public_key)

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)


def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))

    try:
        params = get_params()
    except Exception as e:
        raise e

    operation = event.get('operation')
    if not operation:
        raise ValueError('operation needs to be specified in request and needs to be eigher "status" or "send"')

    # {"operation": "status"}
    if operation == 'status':
        key_id = os.getenv('KMS_KEY_ID')
        pub_key = get_kms_public_key(key_id)
        eth_checksum_address = calc_eth_address(pub_key)

        return {'eth_checksum_address': eth_checksum_address}

    # {"operation": "send",
    #  "amount": 123,
    #  "dst_address": "0x...",
    #  "nonce": 0}
    elif operation == 'sign':

        if not (event.get('dst_address') and event.get('amount', -1) >= 0 and event.get('nonce', -1) >= 0):
            return {'operation': 'sign',
                    'error': 'missing parameter - sign requires amount, dst_address and nonce to be specified'}

        # get key_id from environment varaible
        key_id = os.getenv('KMS_KEY_ID')

        # get destination address from send request
        dst_address = event.get('dst_address')

        # get amount from send request
        amount = event.get('amount')

        nonce = event.get('nonce')
        # get the call data
        data = event.get('data')

        # optional params
        chainid = event.get('chainid')
        type = event.get('type')
        max_fee_per_gas = event.get('max_fee_per_gas')
        max_priority_fee_per_gas = event.get('max_priority_fee_per_gas')

        # download public key from KMS
        pub_key = get_kms_public_key(key_id)

        # calculate the Ethereum public address from public key
        eth_checksum_addr = calc_eth_address(pub_key)

        # collect rawd parameters for Ethereum transaction
        tx_params = get_tx_params(dst_address=dst_address,
                                  amount=amount,
                                  nonce=nonce,
                                  chainid=chainid,
                                  type=type,
                                  max_fee_per_gas=max_fee_per_gas,
                                  max_priority_fee_per_gas=max_priority_fee_per_gas,
                                  data=data)

        # assemble Ethereum transaction and sign it offline
        raw_tx_signed_hash, raw_tx_signed_payload = assemble_tx(tx_params=tx_params,
                                                                params=params,
                                                                eth_checksum_addr=eth_checksum_addr,
                                                                chainid=chainid)

        return {"signed_tx_hash": raw_tx_signed_hash,
                "signed_tx_payload": raw_tx_signed_payload}
