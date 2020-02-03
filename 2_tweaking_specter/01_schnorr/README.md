# Building on top of secp256k1

**Here some BIP-Schnorr intro**

We have secp256k1 with schnorr support, let's integrate it in hardware and software.

## Generating segwit v1 addresses

Even without any changes we can do it:

```py
from bitcoin import ec, bech32, script

# terrible private key
secret = ec.PrivateKey(b'5'*32)
pub = secret.get_public_key()
xonly = pub.sec()[1:]

# OP_1<len><pubkey>
sc = script.Script(b'\x51\x20'+xonly)
# sc.address() - this will fail at the moment

# manually generating address
addr = bech32.encode("sb",1,xonly)
```

## Adding `.address()` support for Segwit v1 scripts

File: `bitcoin/script.py`:

- change `self.script_type()` to detect that it's `taproot` script
- change `self.address()` to encode `taproot` script to `bech32` encoding
- write a helper function `p2taproot(pubkey)` that generates correct script

Homework:

- add `tweak` to generate address according to recommendations in BIPs.
- use `tweak` to include Taproot script

Solution:

```py
class Script:
    def address(self, network=NETWORKS["main"]):
    # ...
        if script_type in ["p2wpkh", "p2wsh", "p2taproot"]:
            ver = data[0]
            if ver == 0x51:
                ver = 1
            if ver <= 1:
                return bech32.encode(network["bech32"], ver, data[2:])
    # ...
    # ...
    def script_type(self):
        # ...
        # 1 <32:pubkey>
        if len(data)==34 and data[:2]==b'\x51\x20':
            return "p2taproot"
# ...
def p2taproot(pubkey, tweak=None):
    if tweak is not None:
        # homework ;)
        raise NotImplementedError("Tweaks are not supported yet")
    pub = pubkey.sec()[1:]
    return Script(b'\x51\x20'+pub)
```

## Integration with Specter-DIY

Add a new type of descriptor to `keystore.py` module:

```py
DESCRIPTOR_SCRIPTS = {
    #...
    "taproot": script.p2taproot,
}
```

Just run:

```py
derivation = "m/84h/1h/0h" # specter.DEFAULT_XPUBS[0][1]
xpub = specter.keystore.get_xpub(derivation).to_base58()
fingerprint = hexlify(specter.keystore.fingerprint).decode()
prefix = "[%s%s]" % (fingerprint, derivation[1:])
descriptor = "taproot(%s%s/_)" % (prefix, xpub)
specter.keystore.create_wallet("Schnorr", descriptor)
```

**Or** add a new default wallet with `taproot` script:

```py
def select_network(name):
    #...
    if len(keystore.wallets) == 0:
        # create a wallet descriptor
        # this is not exactly compatible with Bitcoin Core though.
        # '_' means 0/* or 1/* - standard receive and change 
        #                        derivation patterns
        derivation = DEFAULT_XPUBS[0][1]
        xpub = keystore.get_xpub(derivation).to_base58()
        fingerprint = hexlify(keystore.fingerprint).decode('utf-8')
        prefix = "[%s%s]" % (fingerprint, derivation[1:])
        descriptor = "wpkh(%s%s/_)" % (prefix, xpub)
        keystore.create_wallet("Default", descriptor)
        
        # add these two lines to add a taproot-default wallet
        descriptor = "taproot(%s%s/_)" % (prefix, xpub)
        keystore.create_wallet("Schnorr", descriptor)
```
Probably it would be better to refactor the creation of the wallets out of a "select_network" method where no one expect that stuff like that gets done.
