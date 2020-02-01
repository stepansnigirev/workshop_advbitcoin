# Sign transactions with Schnorr

MicroPython bindings are already there, new functions in `secp256k1` module:

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

Now let's use this to sign the transaction.

```py
# add here transaction construction example maybe
```

In `transaction` module, we can add a `sighash_taproot` method to the `Transaction` class.

That's basically everything we need. Read more about transaction signing in [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki).

There are a few changes in how we calculate the message to sign in segwit v1:

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
    # ...
```

Now when we can calculate the message hash for the input we can sign it:

```py
import secp256k1

sig = secp256k1.schnorrsig_sign(msg_hash, pk._secret)
```

and add this signature to the Witness script:

```py
from script import Witness

tx.vin[0].witness = Witness([sig])
```