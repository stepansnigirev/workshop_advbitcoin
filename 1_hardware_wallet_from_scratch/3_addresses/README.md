## Addresses

Now we can generate first 5 receiving addresses from our master public key. First we need to derive public keys, and then generate corresponding scripts and convert them to addresses. Address is not a feature of the public key, it's a feature of the output script. We have a few helper functions in the `script` module to build them.

Common single-key bitcoin scripts are:
- legacy pay-to-pubkey-hash (`script.p2pkh(pubkey)`)
- modern pay-to-witness-pubkey-hash that use bech32 encoding for addresses (`script.p2wpkh(pubkey)`)
- modern pay-to-witness-pubkey-hash nested in legacy pay-to-script-hash for backward compatibility with legacy wallets (`script.p2sh(script.p2wpkh(pubkey))`)

```python
from bitcoin import script

xpub_bip44 = root_key.derive("m/44h/1h/0h").to_public()
# version parameter is optional - by default it uses mainnet xpub.
print("\nLegacy xpub:", xpub_bip44.to_base58(version=network["xpub"]))
print("Legacy addresses:")
for i in range(5):
    # m/0/i is used for receiving addresses and m/1/i for change addresses
    # derive function also accepts lists of indexes
    pub = xpub_bip44.derive([0, i])
    # get p2pkh script
    sc = script.p2pkh(pub)
    print("Address %i: %s" % (i, sc.address(network)))

xpub_bip84 = root_key.derive("m/84h/1h/0h").to_public()
print("\nSegwit zpub:", xpub_bip84.to_base58(version=network["zpub"]))
print("Segwit addresses:")
for i in range(5):
    pub = xpub_bip44.derive([0, i])
    # get p2wsh script
    sc = script.p2wpkh(pub)
    print("Address %i: %s" % (i, sc.address(network)))

xpub_bip49 = root_key.derive("m/49h/1h/0h").to_public()
print("\nNested Segwit ypub:", xpub_bip49.to_base58(version=network["ypub"]))
print("Nested segwit addresses:")
for i in range(5):
    pub = xpub_bip44.derive([0, i])
    # get p2sh(p2wpkh) script
    sc = script.p2sh(script.p2wpkh(pub))
    print("Address %i: %s" % (i, sc.address(network)))
```

Let's move on and make a GUI for what we just did: a simple screen where we could navigate between addresses and display them as QR codes.

Continue to the [next part](../4_gui)