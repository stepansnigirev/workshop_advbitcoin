# Creating PSBT manually

Bitcoin Core doesn't know how to create PSBT for our addresses. We can't even use `importmulti` as taproot descriptors don't exist.

But we want to use Core's functionality as much as we can, and we don't want to store all the keys and addresses ourselves.

We had similar problem with `sortedmulti` as back then stable version of Core didn't support this descriptor type, and we used similar workaround. In principle it is pretty universal for any kind of script types that Core doesn't understand.

So here is what we gonna do for now:

1. We will also import a standard descriptor (let's say `wpkh`) to get information about public keys and derivation paths
2. We will derive a bunch of taproot addresses and import them to the wallet. Then Core will watch our addresses and we will at least see what's our utxo and overall balance
3. To create a PSBT transaction we will first construct a raw unsigned transaction, then convert it to PSBT
4. To get derivation paths we will convert our address from taproot to `wpkh` and ask Core about derivation path for this address
5. Finally we will inject derivation paths to our PSBT

## Importing addresses to Core

Let's start with importing a standard `wpkh` descriptor into Core:

```py
from rpc import BitcoinCLI

rpc = BitcoinCLI("specter","TruckWordTrophySolidVintageFieldGalaxyOrphanSeek", 
    protocol="https", host="schnorr.specterwallet.io", port=443)

# replace with yours
xpub = "[b317ec86/84h/1h/0h]tpubDCKVXMvGq2YRczuCLcfcY8TaxHGjFTuhFrkRGpBk4DXmQeJXM3JAz8ijxTS59PZQBUtiq5wkstpzgvow7A25F4vDbmiAEy3rE4xHcR2XUUq"

wallet_name = "xpubwallet"+xpub[-8:]
rpc.createwallet(wallet_name, True)
w = rpc.wallet(wallet_name)

# add checksum helper function
def add_checksum(desc):
    return rpc.getdescriptorinfo(desc)["descriptor"]

# importing keys
recv_desc = add_checksum("wpkh(%s/0/*)" % xpub)
change_desc = add_checksum("wpkh(%s/1/*)" % xpub)

w.importmulti([
    {
        "desc":recv_desc,
        "timestamp":"now",
        "range":[0,100],
        "internal":False,
        "watchonly":True,
        "keypool":True
    },{
        "desc":change_desc,
        "timestamp":"now",
        "range":[0,100],
        "internal":True,
        "watchonly":True,
        "keypool":True}
],{"rescan": False})
```

Now let's write a function that would derive a taproot addresses for us:

```py
import bech32, hashlib

def get_taproot_address(idx, change=False):
    desc = change_desc if change else recv_desc
    # getting address
    address = w.deriveaddresses(desc, [idx, idx])[0]
    # x-only pubkey
    xonly = bytes.fromhex(w.getaddressinfo(address)["pubkey"])[1:]
    # human readable part of address, "sb" in our case
    hrp = address.split("1")[0]
    # taproot address
    tap_addr = bech32.encode(hrp, 1, xonly)
    return tap_addr
```

Let's import a bunch of them to Core. We can either use the same wallet or a different one, doesn't matter really.

```py
# first 10 receving addresses
args = [{
    "scriptPubKey":{"address": get_taproot_address(i)},
    "timestamp": "now",  
    "internal":False,
    "watchonly":True,
    "keypool":True,
} for i in range(10)]
# first 10 change addresses
args += [{
    "scriptPubKey":{"address": get_taproot_address(i, change=True)},
    "timestamp": "now",  
    "internal":True,
    "watchonly":True,
    "keypool":True,
} for i in range(10)]
w.importmulti(args)
```

## Getting derivation path

Now let's get derivation path from the address. We almost have full pubkey in taproot addresses, we only need to bruteforce firt byte - it will be either `02` or `03`.

```py
def hash160(data):
    return hashlib.new("ripemd160",
                       hashlib.sha256(data).digest()
                      ).digest()

def get_derivation(address):
    hrp = address.split("1")[0]
    ver, prog = bech32.decode(hrp, address)
    prog = bytes(prog)

    address_candidates = [
        bech32.encode(hrp, 0, hash160(b'\x02'+prog)),
        bech32.encode(hrp, 0, hash160(b'\x03'+prog))
    ]
    addr_info = [w.getaddressinfo(addr) for addr in address_candidates]
    # one of them should have "hdkeypath" key
    result = [info for info in addr_info if "hdkeypath" in info][0]
    # get pubkey
    pub = bytes.fromhex(result["pubkey"])
    # get fingerprint
    der = [int.from_bytes(bytes.fromhex(result["hdmasterfingerprint"]),"little")]
    # parse path
    path = result["hdkeypath"].replace("'","h").split("/")[1:] # skip m/
    der += [int(p) if "h" not in p else int(p[:-1])+0x80000000 for p in path]
    # return (pub, der)
    return bytes.fromhex(result["pubkey"]), der
```

## Creating PSBT

Let's say we want to send a certain amount back to the faucet. As Core doesn't know how to sign / solve taproot addresses it won't pick inputs for us automagicaly, so we need to make it manually.

We will take as many unspent outputs as we need to cover the spending amount, and send the rest to our 0'th change address (for now)

```py
send_addr = "sb1qkndcdkl7j8adskqnl3mxt3c9uhufa06qvhdzv3"
send_amount = 0.02
fee = 500/1e8 # hardcoded fee for now
change_address = get_taproot_address(0, change=True)

total_in = 0
inputs = []
# find enough inputs
for tx in w.listunspent(0):
    inputs.append({"txid": tx["txid"], "vout": tx["vout"]})
    total_in += tx["amount"]
    if total_in > send_amount+fee:
        break

rawtx = w.createrawtransaction(inputs,[
                { send_addr: send_amount },
                { change_address: int(1e8*(total_in-amount-fee))/1e8 }, # to handle round errors
            ])
b64psbt = w.converttopsbt(rawtx)
```

Now we have a PSBT and we can add derivation paths there. To work with PSBT we can use either `hwilib` (we use it as a dependency in Specter-Desktop anyways) or Core testframework. Up to you.

```py
from hwilib.serializations import *

psbt = PSBT()
psbt.deserialize(b64psbt)

# input scope
for i, inp in enumerate(inputs):
    rawtx = bytes.fromhex(w.gettransaction(inp["txid"])["hex"])
    tx = CTransaction()
    tx.deserialize(BytesIO(rawtx))
    psbt.inputs[i].witness_utxo = tx.vout[inp["vout"]]
    pub, der = get_derivation(inp["address"])
    psbt.inputs[i].hd_keypaths[pub] = der
# change address scope
pub, der = get_derivation(change_address)
psbt.outputs[1].hd_keypaths[pub] = der
b64psbt = psbt.serialize()
```

Let's inspect that psbt looks right:

```py
w.decodepsbt(b64psbt)
```

Awesome! We can sign it with our hardware wallet now and get back a signed signature.

On the board now:

```py
# paste your b64psbt here
specter.parse_transaction("copy b64psbt here")
```

Now back to normal python:

```py
res = w.combinepsbt([b64psbt,"copy stuff from hardware wallet here"])
w.finalizepsbt(res)
```

You should get a raw transaction you can broadcast now with `w.sendrawtransaction()`
