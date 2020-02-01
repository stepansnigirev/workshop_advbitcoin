# Working with Bitcoin in MicroPython

Now let's take our entropy, convert it to the recovery phrase ([BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)), convert the recovery phrase to HD key ([BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)) and derive first 5 native segwit addresses from it ([BIP-84](https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki)). 

We can check that we did everything correctly using this [great tool from Ian Coleman](https://iancoleman.io/bip39/).

## Recovery phrase: BIP-39

`gospel palace choice either lawsuit divorce manual turkey pink tuition fat pair` - you've seen phrases like this before. These recovery phrases became standards in the industry and almost every wallet uses them. We will stick to the standard ([BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)) and use them as well.

Fundamentally it is just a convenient way of representing some random number in a human-readable form. It contains a checksum and uses a fixed dictionary so if you make a mistake while typing it the wallet will spot it. Then this recovery phrase together with the password can be converted to a 64-byte seed used for key derivation in [BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki).

`bip39` module provides all necessary functionality to convert bytes to recovery phrases and back as well as calculating the seed for the recovery phrase and the password.

Entropy corresponding to the recovery phrase above is `64d3e4a0a387e28021df55a51d454dcf`. We could generate it at random using TRNG on the board (`os.urandom()`), mix some user entropy and environmental noise there to get good overall randomness. 

We already generated entropy in the [previous part](../blinky) and maybe even saved it to flash. Let's keep working with this entropy.

The code below converts entropy bytes to recovery phrase and then converts recovery phrase to the 64-byte seed using password `mysecurepassword`:

```python
from bitcoin import bip39
from binascii import hexlify

# put your entropy here, or load from file:
# with open("/flash/entropy", "rb"):
#     entropy = f.read()
entropy = b"a"*16 # very bad entropy

phrase = bip39.mnemonic_from_bytes(entropy)
print("Your recovery phrase:\n%s\n" % phrase)

# uncomment this line to make invalid mnemonic:
# phrase += " satoshi"

# you can check if recovery phrase is valid or not:
if not bip39.mnemonic_is_valid(phrase):
    raise ValueError("Meh... Typo in the recovery?")

# convert mnemonic and password to bip-32 seed
seed = bip39.mnemonic_to_seed(phrase, password="mysecurepassword")
print("Seed:", hexlify(seed).decode())
```

## HD wallets: BIP-32

Back in the days we were generating all private keys independently. And it was awful - we had to make backups very often, backup size was growing, we sometimes even reused addresses... Dark times.

[BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) solved this. Using small amount of initial entropy and magic of hash functions we are able to derive any amount of private keys. And even better, we can use master public keys to generate new public keys without any knowledge about private keys (*note:* only if non-hardened children are used).

Derivation paths are also kinda standartized. We have [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki), [BIP-49](https://github.com/bitcoin/bips/blob/master/bip-0049.mediawiki) and [BIP-84](https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki) for that. Some of the wallets (i.e. Bitcoin Core, Green Wallet) don't use these standards for derivation, others do.

Let's use BIP-84 and generate an extended public key for signet. We can import this extended public key to Bitcoin Core or Electrum and watch our addresses.

```python
from bitcoin import bip32
# NETWORKS contains all constants for HD keys and addresses
from bitcoin.networks import NETWORKS
# we will use signet:
network = NETWORKS["signet"]

# create HDKey from 64-byte seed
root_key = bip32.HDKey.from_seed(seed)
# generate an account child key:
# purpose: 84h - BIP-84
# coin type: 1h - Testnet
# account: 0h - first account
account = root_key.derive("m/84h/1h/0h")
# convert HD private key to HD public key
account_pub = account.to_public()
# for Bitcoin Core: pure BIP-32 serialization
print("Your xpub:", account_pub.to_base58(version=network["xpub"]))
# for Electrum and others who cares about SLIP-0132
# used for bip-84 by many wallets
print("Your zpub:", account_pub.to_base58(version=network["zpub"]))
```

## Master key that Bitcoin Core likes

Bitcoin Core wants a derivation path and a parent fingerprint in order to create PSBT transactions for you. So let's get it in the form that Bitcoin Core likes. It should be `[fingerprint/derivation]xpub`.

Fingerprint is a `hash160` of the root public key and works as an identifier of our root key. The easiest way to get the fingerprint is to get a parent fingerprint of the root's child.

```python
fingerprint = root_key.child(0).fingerprint
print("Your xpub: [%s/84h/1h/0h]%s" % (hexlify(fingerprint).decode(), account_pub.to_base58(version=network["xpub"])))
```

## Importing to Specter-Desktop

We have a web-wallet running and connected to the signet node:

https://app.specterwallet.io

Create a new device, call it somehow unique and import your zpub there.

You could do the same with your own Bitcoin Core node.

*Hint: `importmulti` command is what your want.*

## Importing to Bitcoin Core

Descriptor for native segwit addresses looks like this: `wpkh([fingerprint/derivation]tpub/0/*)` for receiving addresses and `.../1/*` for change addresses. Let's get this descriptor from our wallet:

Create a new wallet in Bitcoin Core with private keys disabled (watch-only):

```
bitcoin-cli -regtest createwallet myhardwarewallet true
```

To import keys to the wallet we need to add checksums to the descriptor. `getdescriptorinfo` will help us to do it.

```
bitcoin-cli -regtest getdescriptorinfo "wpkh([b317ec86/84h/1h/0h]tpubDCKVXMvGq2YRczuCLcfcY8TaxHGjFTuhFrkRGpBk4DXmQeJXM3JAz8ijxTS59PZQBUtiq5wkstpzgvow7A25F4vDbmiAEy3rE4xHcR2XUUq/0/*)"
```

From the result copy the checksums and add them after the descriptor like this: `wsh(.../0/*)#2e3mrc2y`

Great, now we can import 1000 receiving and change addresses to our wallet using descriptors with checksums:

```
bitcoin-cli -regtest -rpcwallet=myhardwarewallet importmulti '[{"desc":"wpkh([b317ec86/84h/1h/0h]tpubDCKVXMvGq2YRczuCLcfcY8TaxHGjFTuhFrkRGpBk4DXmQeJXM3JAz8ijxTS59PZQBUtiq5wkstpzgvow7A25F4vDbmiAEy3rE4xHcR2XUUq/0/*)#2e3mrc2y","timestamp":"now","range":[0,1000],"internal":false,"watchonly":true,"keypool":true},{"desc":"wpkh([b317ec86/84h/1h/0h]tpubDCKVXMvGq2YRczuCLcfcY8TaxHGjFTuhFrkRGpBk4DXmQeJXM3JAz8ijxTS59PZQBUtiq5wkstpzgvow7A25F4vDbmiAEy3rE4xHcR2XUUq/1/*)#md567d6u","timestamp":"now","range":[0,1000],"internal":true,"watchonly":true,"keypool":true}]' '{"rescan":false}'
```

Notice that first descriptor is marked as external (`"internal":false`) and second as internal. Also as it is a new wallet without any history we've set `rescan` option to `false`. 

Using bitcoin-cli is not super convenient, but doable.

## Solution

Here is the final [`main.py`](./main.py) file. 

Copy it to the board and reset it (`Ctrl+D` or press the black button on the back).

## Next

Next we will use these master keys to generate addresses.

Continue to [3 - Addresses](../3_addresses)