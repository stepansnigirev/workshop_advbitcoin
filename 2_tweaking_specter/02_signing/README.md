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

Now let's add this functionality to our bitcoin classes and sign transaction


