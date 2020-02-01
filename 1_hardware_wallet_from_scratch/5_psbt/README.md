# Working with PSBT transactions and Bitcoin Core

Partially Signed Bitcoin Transaction format is a standard for unsigned bitcoin transactions defined in [BIP-174](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki). It was developed specifically for hardware wallets that have very limited resources and doesn't have enough knowledge about current state of the blockchain, UTXO set, used keys etc.

PSBT transaction is basically a raw bitcoin transaction with additional metadata that hardware wallet can use to sign the transaction and to display relevant information to the user. Normally it includes derivation pathes for all inputs and change outputs, scriptpubkeys and amounts of previous outputs we are spending, sometimes it may have redeem or witness script and so on. It is very well documented in the BIP so it makes sense to go through it and read.

## Using Specter-Desktop to get PSBT

If you used https://app.specterwallet.io to import your keys, you can just create a segwit wallet there - you will instantly get the money on your first address and you can prepare a PSBT transaction right away in the `Send` tab.

Plaintext PSBT is displayed under the QR code.

## Using Bitcoin Core

### Getting some money to the wallet

We have two ways to generate addresses - on the hardware wallet or in bitcoin core.

On the hardware wallet we can use our address navigator from the previous part of the tutorial, or just write a small script:

```python
from bitcoin import script

child = bip84_xpub.derive("m/0/0")
first_addr = script.p2wpkh(child).address(NETWORKS["regtest"])
print(first_addr)
```

With Bitcoin Core we can do the same using this command:

```
bitcoin-cli -regtest -rpcwallet=myhardwarewallet getnewaddress "" bech32
```

We explicitly tell Bitcoin Core that we want to get bech32 address (native segwit). 

Now we can send some funds to this address. Let's generate 101 blocks to this address:

```
bitcoin-cli -regtest generatetoaddress 101 bcrt1q685z47r72vmqxskvrgc6y6vln7rgwaldnuruwk
```

### Creating PSBT in Bitcoin Core

Let's create a PSBT that sends some money to some random address (for example `2MyMDviGxP8jkTBZiuLPwWfy2jKCTAoFoxP`). Don't forget to define that we want to use bech32 for change and that we want to include derivation information.

```
bitcoin-cli -regtest -rpcwallet=myhardwarewallet walletcreatefundedpsbt '[]' '[{"2MyMDviGxP8jkTBZiuLPwWfy2jKCTAoFoxP":1}]' 0 '{"includeWatching":true,"change_type":"bech32"}' true
```

We will get the psbt we can start working with:
```
cHNidP8BAHICAAAAAcAiqnT66whblrAy+sRnAxMqusYBCt5CObq1YdO7RDqUAAAAAAD+////AgAgECQBAAAAFgAU1wt1dfsk78kR1EeF4fPPzj6jTw0A4fUFAAAAABepFELzMvZSa13zYflKwHse4o/VbF/mhwAAAAAAAQEfGAwGKgEAAAAWABTR6Cr4flM2A0LMGjGiaZ+fhod37SIGAhHf737H1jCUjkJ1K5DqFkaY0keihxeWBQpm1kDtVZyxGLMX7IZUAACAAQAAgAAAAIAAAAAAAAAAAAAiAgI4QR+S6RWCsMCkH7+oe1/v4wH90b7rbx9hWWgwk2fXHBizF+yGVAAAgAEAAIAAAACAAQAAAAIAAAAAAA==
```

## Parsing PSBT in MicroPython

```python
from bitcoin import psbt
from ubinascii import a2b_base64

# parse psbt transaction
b64_psbt = "cHNidP8BAHICAAAAAcAiqnT66whblrAy+sRnAxMqusYBCt5CObq1YdO7RDqUAAAAAAD+////AgAgECQBAAAAFgAU1wt1dfsk78kR1EeF4fPPzj6jTw0A4fUFAAAAABepFELzMvZSa13zYflKwHse4o/VbF/mhwAAAAAAAQEfGAwGKgEAAAAWABTR6Cr4flM2A0LMGjGiaZ+fhod37SIGAhHf737H1jCUjkJ1K5DqFkaY0keihxeWBQpm1kDtVZyxGLMX7IZUAACAAQAAgAAAAIAAAAAAAAAAAAAiAgI4QR+S6RWCsMCkH7+oe1/v4wH90b7rbx9hWWgwk2fXHBizF+yGVAAAgAEAAIAAAACAAQAAAAIAAAAAAA=="
# first convert it from base64 to raw bytes
raw = a2b_base64(b64_psbt)
# then parse
tx = psbt.PSBT.parse(raw)

# print how much we are spending and where
print("Parsing PSBT transaction...")
total_in = 0
for inp in tx.inputs:
    total_in += inp.witness_utxo.value
print("Inputs:", total_in, "satoshi")
change_out = 0 # value that goes back to us
send_outputs = []
for i, out in enumerate(tx.outputs):
    # check if it is a change or not:
    change = False
    # should be one or zero for single-key addresses
    for pub in out.bip32_derivations:
        # check if it is our key
        if out.bip32_derivations[pub].fingerprint == fingerprint:
            hdkey = root.derive(out.bip32_derivations[pub].derivation)
            mypub = hdkey.key.get_public_key()
            if mypub != pub:
                raise ValueError("Derivation path doesn't look right")
            # now check if provided scriptpubkey matches
            sc = script.p2wpkh(mypub)
            if sc == tx.tx.vout[i].script_pubkey:
                change = True
                continue
    if change:
        change_out += tx.tx.vout[i].value
    else:
        send_outputs.append(tx.tx.vout[i])
print("Spending", total_in-change_out, "satoshi")
fee = total_in-change_out
for out in send_outputs:
    fee -= out.value
    print(out.value,"to",out.script_pubkey.address(NETWORKS["test"]))
print("Fee:",fee,"satoshi")
```

## Signing PSBT

```python
# sign the transaction
tx.sign_with(root)
raw = tx.serialize()
# convert to base64
b64_psbt = b2a_base64(raw)
# somehow b2a ends with \n...
if b64_psbt[-1:] == b"\n":
    b64_psbt = b64_psbt[:-1]
# print
print("\nSigned transaction:")
print(b64_psbt.decode('utf-8'))
```

Transaction is ready to be finalized and broadcasted.

## Using Specter-Desktop

Click "Paste PSBT" and... paste psbt :)
The app will finalize it for you and broadcast.

## Using Bitcoin Core

First finalize the transaction:

```
bitcoin-cli -regtest finalizepsbt cHNidP8BAHICAAAAAcAiqnT66whblrAy+sRnAxMqusYBCt5CObq1YdO7RDqUAAAAAAD+////AgAgECQBAAAAFgAU1wt1dfsk78kR1EeF4fPPzj6jTw0A4fUFAAAAABepFELzMvZSa13zYflKwHse4o/VbF/mhwAAAAAAAQEfGAwGKgEAAAAWABTR6Cr4flM2A0LMGjGiaZ+fhod37SICAhHf737H1jCUjkJ1K5DqFkaY0keihxeWBQpm1kDtVZyxRzBEAiARkaZfb7U3UzxTnmjrmIF82a/ky8eOegV/alKHTIa+eAIgSO45ZkAWoutrGoiHpfSTfR2RKzdXxmA9f06iIVVWNuoBIgYCEd/vfsfWMJSOQnUrkOoWRpjSR6KHF5YFCmbWQO1VnLEYsxfshlQAAIABAACAAAAAgAAAAAAAAAAAACICAjhBH5LpFYKwwKQfv6h7X+/jAf3RvutvH2FZaDCTZ9ccGLMX7IZUAACAAQAAgAAAAIABAAAAAgAAAAAA
```

Then broadcast:

```
bitcoin-cli -regtest sendrawtransaction 02000000000101c022aa74faeb085b96b032fac46703132abac6010ade4239bab561d3bb443a940000000000feffffff020020102401000000160014d70b7575fb24efc911d44785e1f3cfce3ea34f0d00e1f5050000000017a91442f332f6526b5df361f94ac07b1ee28fd56c5fe6870247304402201191a65f6fb537533c539e68eb98817cd9afe4cbc78e7a057f6a52874c86be78022048ee39664016a2eb6b1a8887a5f4937d1d912b3757c6603d7f4ea221555636ea01210211dfef7ec7d630948e42752b90ea164698d247a2871796050a66d640ed559cb100000000
```

## Next step: [Taproot!](../6_taproot)

We will generate segwit version 1 addresses, send some money to it and try to spend :)
