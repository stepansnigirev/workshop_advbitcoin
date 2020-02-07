# Sign transactions with Schnorr

The relevant functions for schnorr-signatures can be found in the `secp256k1` module:

- `schnorrsig_serialize(sig)` - serializes schnorr signature to 64 byte sequence
- `schnorrsig_parse(bytes)` - parses 64-byte schnorr signature
- `schnorrsig_sign(msg, secret)` - signs the message with secret key
- `schnorrsig_verify(sig, msg, pubkey)` - verifies the signature against the message and public key
- `xonly_pubkey_create(secret)` - creates a x-only public key from secret key
- `xonly_pubkey_from_pubkey(pubkey)` - returns `P` or `-P` depending on which one is right
- `xonly_pubkey_serialize(pubkey)` - serializes pubkey as xonly
- `xonly_pubkey_parse(bytes)` - parses 32-byte pubkey
- `xonly_pubkey_tweak_add(pubkey, tweak)` - adds `tweak*G` to public key (and negates if necessary)
- `xonly_seckey_tweak_add(secret, tweak)` - adds tweak to secret key

## Exkurs: How does these functions got in there? (Skip and revisit later if interested!)

This module is injected via the [usermods-folder of the f469-disco repo](https://github.com/diybitcoinhardware/f469-disco/tree/master/usermods/usecp256k1) and it comes from [bitcoin-core/secp256k1](https://github.com/bitcoin-core/secp256k1/tree/0d9540b13ffcd7cd44cc361b8744b93d88aa76ba). The [Taproot branch](https://github.com/diybitcoinhardware/f469-disco/tree/master/usermods/usecp256k1) of f469-disco is therefore pointing to
[jonasnick's fork](https://github.com/jonasnick/secp256k1/tree/6603c32a10eb0025ac35adc159bf9c57b8e29334) of secp256k1. 

Now let's use this to sign the transaction.

## Create a transaction to sign

First we need to create a raw transaction.

An RPC-call `w.listunspent(0)` gives us a list of utxo we can use to make a new one.

```py
from bitcoin import bech32
from bitcoin.script import Script
from bitcoin.transaction import Transaction, TransactionInput, TransactionOutput
from ubinascii import hexlify, unhexlify

# inputs - copy relevant data from RPC call w.listunspent(0)
inputs = [{
    'txid': unhexlify('82591064c6aa6696e6ed8ee2edbc458888733ff0bdf5ba977e1d4081324c8a0c'),
    'vout': 0,
    'scriptPubKey': Script(unhexlify('51207098e391268702cc209f1fc73d0711f6a09374b5ab085885e4ca1228b51022f2')),
    'amount': 10000000 # don't forget to convert to satoshi
}]

# inputs vector
vin = [TransactionInput(inp["txid"],inp["vout"]) for inp in inputs]

# destination
out_addr = "sb1qkndcdkl7j8adskqnl3mxt3c9uhufa06qvhdzv3"
# get segwit version and data
ver, d = bech32.decode("sb",out_addr)
# convert to script
sc_out = Script(bytes([ver,len(d)])+bytes(d))
# outputs vector
vout = [
    TransactionOutput(10000000//2, sc_out),
    TransactionOutput(10000000//2-500, inputs[0]["scriptPubKey"]),
]

tx = Transaction(vin=vin, vout=vout)
print("Unsigned transaction:")
print(hexlify(tx.serialize()).decode())
```

## Signing Taproot transaction

Check out [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki#common-signature-message) to figure out how to get the hash of the transaction we need to sign.

```py
from hashlib import sha256
import secp256k1
from bitcoin.script import Witness

def tagged_hash(tag, msg):
    tag_hash = sha256(tag.encode()).digest()
    return sha256(tag_hash + tag_hash + msg).digest()

# account hd key
hd = specter.keystore.root
# private key for this address
pk = hd.derive(der).derive([0,0]).key
secret = pk._secret

# calculating the hash

d = b'\x00' # sighash_all (default)
d += tx.version.to_bytes(4, 'little')
d += tx.locktime.to_bytes(4, 'little')

# prevouts
d += tx.hash_prevouts()

# amounts
h = sha256()
for inp in inputs:
    h.update(inp["amount"].to_bytes(8, 'little'))
d += h.digest()

# sequences
d += tx.hash_sequence()

# outputs
d += tx.hash_outputs()

# spend_type
d += b"\x00"

# prevout
d += inputs[0]["scriptPubKey"].serialize()

# index
d += b'\x00'*4

# ???
d = b'\x00' + d

print("sighash:", hexlify(d))
msg = tagged_hash("TapSighash",d)
sig = secp256k1.schnorrsig_sign(msg, secret)
ser_sig = secp256k1.schnorrsig_serialize(sig)
print(hexlify(ser_sig))
tx.vin[0].witness = Witness([ser_sig])

print("Signed transaction:")
print(hexlify(tx.serialize()))

```

# Adding `sighash_taproot` to the library

In `transaction` module, we can add a `sighash_taproot` method to the `Transaction` class.

Notice that there are a few changes how we calculate the message to sign in segwit v1:

- it commits to **all** amounts => we can always calculate the fee
- it commits to scriptpubkey as well
- we use `tagged_hash` hash function with different tags for different purposes
- we don't use double_sha256 any more, just a simple sha256

```py
class Transaction:
    # ...
    def sighash_taproot(self, input_index, script_pubkey, values):
        if len(values) != len(self.vin):
            raise ValueError("Provide values for every input")
        inp = self.vin[input_index]
        h = hashlib.sha256()
        tag_hash = hashlib.sha256(b"TapSighash").digest()
        h.update(tag_hash)
        h.update(tag_hash)
        h.update(b'\x00\x00') # ?? + sighash all
        h.update(self.version.to_bytes(4, 'little'))
        h.update(self.locktime.to_bytes(4, 'little'))
        h.update(self.hash_prevouts())
        h.update(self.hash_amounts(values))
        h.update(self.hash_sequence())
        h.update(self.hash_outputs())
        h.update(b'\x00') # spend time
        h.update(script_pubkey.serialize())
        h.update(input_index.to_bytes(4, 'little'))
        return h.digest()

    def hash_amounts(self, amounts):
        h = hashlib.sha256()
        for amount in amounts:
            h.update(amount.to_bytes(8, 'little'))
        return h.digest()
    # ...
```

We can also extend the `ec.py` module to have a new signature type - `ScnorrSignature`, and implement `sign_schnorr()` method in private key.

```py
class PrivateKey:
    # ...
    def sign_schnorr(self, msg_hash):
        return SchnorrSignature(secp256k1.schnorrsig_sign(msg_hash, self._secret))
# ...

class SchnorrSignature:
    def __init__(self, sig):
        self._sig = sig

    def serialize(self):
        return secp256k1.schnorrsig_serialize(self._sig)

    @classmethod
    def parse(cls, ser):
        return cls(secp256k1.schnorrsig_parse(ser))
```

Also makes sense to add `sign_schnorr()` method to HDKey (`bip32.py`:

```py
class HDKey:
    # ...
    def sign_schnorr(self, msg_hash):
        """signs a hash of the message with the private key with Schnorr"""
        if not self.is_private:
            raise RuntimeError("HD public key can't sign")
        return self.key.sign_schnorr(msg_hash)
    # ...
```

Now when we can refactor the code from previous part:

```py
for i, inp in enumerate(tx.vin):
    msg = tx.sighash_taproot(i, inputs[i]["scriptPubKey"],[inpt["amount"] for inpt in inputs])
    sig = pk.sign_schnorr(msg)
    tx.vin[i].witness = Witness([sig.serialize()])
print(hexlify(tx.serialize()))
```

# Sign PSBT with Schnorr

We can add the last thing to the library - signing Taproot inputs in PSBT.

We have a `PSBT.sign_with(root)` method that we need to extend slightly:

```py
from bitcoin.script import Witness
# ...
class PSBT:
    # ...
    def sign_with(self, root):
        # ...
                    elif inp.witness_utxo is not None:
                        if inp.witness_utxo.script_pubkey.script_type() == "p2taproot":
                            values = [inpt.witness_utxo.value for inpt in self.inputs]
                            h = self.tx.sighash_taproot(i, inp.witness_utxo.script_pubkey, values)
                            sig_schnorr = hdkey.key.sign_schnorr(h)
                            inp.final_scriptwitness = Witness([sig_schnorr.serialize()])
                        else:
                            # segwit
    # ...
```

With this functionality implemented we can try it out with Specter-Desktop we deployed on https://app.specterwallet.io/

Next we will figure out how to manually create PSBT on the host side when Bitcoin Core doesn't know yet how to do it.