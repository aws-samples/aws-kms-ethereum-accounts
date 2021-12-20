# AWS-KMS-Ethereum-Accounts

This project represents an example implementation of an AWS customer master key (CMK) based Ethereum account.  
It's implemented in AWS Cloud Development Kit (CDK) and Python.

This repository contains all code artifacts for the following three blog posts:

1. [Use Key Management Service (AWS KMS) to securely manage Ethereum accounts: Part 1](https://aws.amazon.com/blogs/database/part1-use-aws-kms-to-securely-manage-ethereum-accounts/)
2. [Use Key Management Service (AWS KMS) to securely manage Ethereum accounts: Part 2](https://aws.amazon.com/blogs/database/part2-use-aws-kms-to-securely-manage-ethereum-accounts/)
3. [How to sign Ethereum EIP-1559 transactions using AWS KMS](https://aws.amazon.com/blogs/database/how-to-sign-ethereum-eip-1559-transactions-using-aws-kms/)

For a detailed explanation of how AWS Cloud Development Kit (CDK) can be used to create an AWS Key Management Service (KMS)
based Ethereum account please have a look at  the [first blog post](https://aws.amazon.com/blogs/database/part1-use-aws-kms-to-securely-manage-ethereum-accounts/).

For a detailed explanation of the inner workings of Ethereum and how Ethereum signatures can be created using AWS KMS please have a look ath
the [second blog post](https://aws.amazon.com/blogs/database/part2-use-aws-kms-to-securely-manage-ethereum-accounts/).

For a detailed explanation of how EIP-1559 transactions can be created and signed using AWS KMS have a
look at [How to sign Ethereum EIP-1559 transactions using AWS KMS](https://aws.amazon.com/blogs/database/how-to-sign-ethereum-eip-1559-transactions-using-aws-kms/).

## Deploying the solution with AWS CDK

Deploying the solution with the AWS CDK The AWS CDK is an open-source framework for defining and provisioning cloud
application resources. It uses common programming languages such as JavaScript, C#, and Python.
The [AWS CDK command line interface](https://docs.aws.amazon.com/cdk/latest/guide/cli.html) (CLI) allows you to interact
with CDK applications. It provides features like synthesizing AWS CloudFormation templates, confirming the security
changes, and deploying applications.

This section shows how to prepare the environment for running CDK and the sample code. For this walkthrough, you must
have the following prerequisites:

* An [AWS account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup).
* An IAM user with administrator access
* [Configured AWS credentials](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_prerequisites)
* Installed Node.js, Python 3, and pip. To install the example application:

When working with Python, it’s good practice to use [venv](https://docs.python.org/3/library/venv.html#module-venv) to
create project-specific virtual environments. The use of `venv` also reflects AWS CDK standard behavior. You can find
out more in the
workshop [Activating the virtualenv](https://cdkworkshop.com/30-python/20-create-project/200-virtualenv.html).

1. Install the CDK and test the CDK CLI:
    ```bash
    npm install -g aws-cdk && cdk --version
    ```

2. Download the code from the GitHub repo and switch in the new directory:
    ```bash
    git clone https://github.com/aws-samples/aws-kms-ethereum-accounts.git && cd aws-kms-ethereum-accounts
    ```

3. Install the dependencies using the Python package manager:
   ```bash
   pip install -r requirements.txt
   ```
4. Deploy the example code with the CDK CLI:
    ```bash
    cdk deploy
    ```

## Cleaning up

Once you have completed the deployment and tested the application, clean up the environment to avoid incurring extra
cost. This command removes all resources in this stack provisioned by the CDK:

```bash
cdk destroy
```

---------------------

### Appendinx

# Running Ethereum Accounts on AWS CMK
The explanation below just covers the inner workings of Ethereum legacy transactions (pre. EIP-155/EIP1559).
For an explanation of how EIP-155 or EIP-1559 transactions can be signed using AWS KMS please have a look at [How to sign Ethereum EIP-1559 transactions using AWS KMS](https://aws.amazon.com/blogs/database/how-to-sign-ethereum-eip-1559-transactions-using-aws-kms/).

## What is this about

This repository represents a PoC of how Ethereum accounts (private/public key) can be hosted on AWS KMS-CMK and how AWS
KMS can be used to create valid offline signatures on Ethereum transactions.

In this simple example, a transaction is created to send some Ether from one Ethereum account to another. For testing
purposes it is recommended to use Ethereum Rinkeby (`https://www.rinkeby.io`) network for example and to create an
account via Metamask.

To bootstrap the AWS KMS-CMK based Ethereum account, the Rinkeby crypto faucet can be
used (https://www.rinkeby.io/#faucet).

---------------------

## How does it work

1. The public key is being calculated and turned into an Ethereum checksum address.
    ```python
    pub_key = get_kms_public_key(params.get_kms_key_id())
    _logger.info('pub_key encoded: {}'.format(pub_key))

    eth_addr = calc_eth_address(pub_key)
    eth_checksum_addr = w3.toChecksumAddress(eth_addr)
    ```
2. A raw transaction is being assembled and the raw hash value is taken.
    ```python
    tx_params = get_tx_params(eth_checksum_addr, params.get_eth_dst_addr())
    _logger.debug('tx params: {}'.format(tx_params))

    tx_unsigned = serializable_unsigned_transaction_from_dict(tx_params)
    tx_hash = tx_unsigned.hash()
    _logger.debug('tx serialized: {}\n tx hash: {}'.format(tx_unsigned, tx_hash))
    ```
3. The signature is calculated over the raw hash value and the missing parameter `v` is being determined.
    ```python
    tx_sig = find_eth_signature(params=params,
                                plaintext=tx_hash)
    _logger.info('tx signature: \n\tr(x): {} \n\ts(proof):{}'.format(tx_sig['r'], tx_sig['s']))

    tx_eth_recovered_pub_addr = get_recovery_id(tx_hash, tx_sig['r'], tx_sig['s'], eth_checksum_addr)
    _logger.info('tx eth recovered addr: {}'.format(tx_eth_recovered_pub_addr))
    ```

4. The final transaction is being assembled and sent of as a raw transaction.
    ```python
    tx_encoded = encode_transaction(tx_unsigned,
                                    vrs=(tx_eth_recovered_pub_addr['v'], tx_sig['r'], tx_sig['s']))
    _logger.debug('tx encoded: {}'.format(tx_encoded))

    eth_balance = w3.eth.get_balance(eth_checksum_addr) / 10 ** 18
    _logger.info('eth balance: {}'.format(eth_balance))

    tx_id = w3.eth.sendRawTransaction(tx_encoded)
    print('tx id: {}'.format(w3.toHex(tx_id)))
   ````

-------------------

## What are the Ethereum Foundations

* Ethereum using ECDSA (Elliptic Curve Digital Signing Algorithm) standard `secp256k1`
* `secp256k1` is supported by AWS KMS `ECC_SECG_P256K1`

---------

* https://cryptobook.nakov.com/asymmetric-key-ciphers/elliptic-curve-cryptography-ecc
* https://en.bitcoin.it/wiki/Secp256k1

## Ethereum Public Key Address

* Per default KMS public key is DER encoded

  https://tools.ietf.org/html/rfc5280 (Page 16)
    ```
        SubjectPublicKeyInfo  ::=  SEQUENCE  {
                algorithm            AlgorithmIdentifier,
                subjectPublicKey     BIT STRING  }
    ```

* We need to ignore the first OCTET string since that it is just an indicator.
  https://tools.ietf.org/html/rfc5280 (Page 16)
    ```
        The first octet of the OCTET STRING indicates whether the key is
        compressed or uncompressed.  The uncompressed form is indicated
        by 0x04 and the compressed form is indicated by either 0x02 or
        0x03
    ```

* The address is defined by KECCAK / (SHA3) hash of raw public key.

  https://www.oreilly.com/library/view/mastering-ethereum/9781491971932/ch04.html
    ```
        Ethereum addresses are hexadecimal numbers, identifiers derived from the last 20 bytes of the Keccak-256 hash of the public key.
        Most often you will see Ethereum addresses with the prefix 0x that indicates they are hexadecimal-encoded [..].
    ```

* Address needs to be converted to checksum address otherwise tools/libs will complain.

  https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md
    ```
        In English, convert the address to hex, but if the ith digit is a letter (ie. it's one of abcdef) print it in uppercase if the 4*ith bit of the hash 
        of the lowercase hexadecimal address is 1 otherwise print it in lowercase.
    ```

## Signing

* Ethereum ECDSA signatures consist of:
    ```
    {r, s, v}
    ```

* The signature needs to be taken over a SHA3 hash of the payload. To avoid re-hashing `MessageType='DIGEST'`
  needs to be specified.

  Due to random value `k` signatures of the same value are different all the time.

  [Deterministic Usage of the Digital Signature Algorithm (DSA) and Elliptic Curve Digital Signature Algorithm (ECDSA/RFC6979)](https://tools.ietf.org/html/rfc6979#section-3.2)

  AWS KMS does not make use of DDSG (Deterministic Digital Signature Generation) in the signing operation right now.

  Even differences in bitcoin library implementations: https://bitcoin.stackexchange.com/a/83785


* AWS KMS Signature is DER encoded.

  r (x), s (proof) can be extracted from DER signature returned by AWS KMS.

  https://tools.ietf.org/html/rfc3279#section-2.2.3
    ```
    Ecdsa-Sig-Value  ::=  SEQUENCE  {
               r     INTEGER,
               s     INTEGER  }
    ```


* S needs to be flipped if `>secp256k1n / 2`

  https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2.md
    ```
    All transaction signatures whose s-value is greater than secp256k1n/2 are now considered invalid. 
    The ECDSA recover precompiled contract remains unchanged and will keep accepting high s-values; this is useful e.g. if a contract recovers old Bitcoin signatures.
    ```

  https://www.secg.org/sec2-v2.pdf (n = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141)

  https://ethereum.stackexchange.com/a/55728
    ```
    This is why a signature with a value of s > secp256k1n / 2 (greater than half of the curve) is invalid.
    ```
* v needs to be recovered separately v is determined during ethereum signing process based on `CHAIN_ID`.

  https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md#specification
    ```
    [...] {0,1} + CHAIN_ID * 2 + 35 where {0,1} is the parity of the y value of the curve point for which r is the x-value in the secp256k1 signing process.
    ```

  `v` is usually created along during the `Ethereum` signing process. Since that KMS is used, `v` needs to be recovered
  e.g. via lib or solidity function like `ecrecover()`
    ```python
    pub_key = Account.recoverHash(msg_hash, vrs=(v, r, s))
    ```

  https://eips.ethereum.org/EIPS/eip-155
    ```
    The currently existing signature scheme using v = 27 and v = 28 remains valid and continues to operate under the same rules as it did previously.
    ```

----------

* https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-messages
* https://medium.com/mycrypto/the-magic-of-digital-signatures-on-ethereum-98fe184dc9c7

### The recovery identifier (`v`)

https://www.secg.org/sec1-v2.pdf

The extra value that Ethereum uses makes it possible to recover the public key from the signature which means that an
Ethereum transaction does not include the public key. The purpose is to save space here.

If given, ethereum determines `v` via the chainid to implement a replay protection. Since that KMS is signing the tx, a
fallback to the `[27, 28]` is necessary. Solidity offers `ecrecover`.

`v` is constantly fluctuating between `27` and `28` due to the unstable signatures due to a random value `k` as
mentioned above.

https://eips.ethereum.org/EIPS/eip-155

v is the last byte of the signature, and is either 27 (0x1b) or 28 (0x1c). This identifier is important because since we
are working with elliptic curves, multiple points on the curve can be calculated from r and s alone. This would result
in two different public keys (thus addresses) that can be recovered. The v simply indicates which one of these points to
use.

https://ethereum.github.io/yellowpaper/paper.pdf

```
    The value 27 represents an even y value and 28 represents an odd y value.
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.