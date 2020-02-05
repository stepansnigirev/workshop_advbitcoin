# Building on top of secp256k1

[BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki), [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) and [BIP-342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki) are describing how we should use Schnorr signatures and Taproot in a new upcoming softfork with Segwit version 1 addresses.

And there is even a [pull request](https://github.com/bitcoin/bitcoin/pull/17977) that implements segwit v1 verification for Bitcoin Core.

libsecp256k1 is also getting [schnorr support](https://github.com/jonasnick/secp256k1/tree/schnorrsig).

Looks like we have everything to try out Schnorr and Taproot both on hardware and software.

## Generating segwit v1 addresses

Segwit v1 addresses correspond to a v1 segwit script of the form `OP_1 <x_only_pubkey>`.

Here `OP_1` is actually `0x51` and pubkey is serialized according to BIP-340, so only x-coordinate goes to the script. For every x coordinate there are two possible points corresponging to our private key and negated private key. We always choose a point that has a Y-coordinate that is a quadratic residue (you can take a square root of it).

Let's create a segwit v1 script and address for signet for some public key `P`:

```py
from bitcoin import ec, bech32, script

# terrible private key, use another one
secret = ec.PrivateKey(b'5'*32)
pub = secret.get_public_key()
xonly = pub.sec()[1:]

# OP_1<len><pubkey>
sc = script.Script(b'\x51\x20'+xonly)
# sc.address() - this will fail at the moment

# manually generating address
addr = bech32.encode("sb",1,xonly)
```

Using JUST a public key in the address is ok if only you control the whole pubkey, also it works if you don't use taproot script. In general it's recommended to use an empty tweak to the public key even if you don't use a script. More on that later.

Now we can take this private key and receive some money on it. 
Here is a faucet: https://faucet.specterwallet.io/

*Note: save the transaction details you got from the faucet, we will use that later*

## Adding `.address()` support for Segwit v1 scripts

Now when we figured out how to generate segwit v1 scripts and addresses let's integrate it into the library. We want this functionality to appear in `script` module, so we need to edit `bitcoin/script.py` file.

We don't have an abbreviation for segwit v1 scripts yet, it might be `p2wpk`, or `p2taproot`. For now we just need to call it somehow, so let's call it `p2taproot`.

Here is what we need to do:

- change `Script.script_type()` method to detect that it's `p2taproot` script
- change `Script.address()` to encode `p2taproot` script to `bech32` encoding
- write a helper function `p2taproot(pubkey, tweak)` that generates a segwit v1 script

Homework:

- add `tweak` to generate address according to recommendations in BIPs.
- use `tweak` to include Taproot script

If we implemented everything correctly we could refactor our previous code and get the same result:

```py
from bitcoin import script
from bitcoin.networks import NETWORKS

# terrible private key, use another one
secret = ec.PrivateKey(b'5'*32)
pub = secret.get_public_key()

# OP_1<len><pubkey>
sc = script.p2taproot(pub) # (secret will also work)

print(sc.address(NETWORKS["signet"]))# - this will fail at the moment
```

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

Specter uses descriptor language to generate addresses for the wallets. `keystore.DESCRIPTOR_SCRIPTS` dictionary defines all known functions used in descriptors (like `wpkh`,`wsh`,`sortedmulti` etc).

To add segwit v1 address generation we only need to add a new type of descriptor function to `keystore.py` module:

```py
DESCRIPTOR_SCRIPTS = {
    #...
    "taproot": script.p2taproot,
}
```

This extra key in the dictionary tells the wallet that if it finds `taproot()` in the descriptor it needs to pass arguments to the `script.p2taproot` function.

After restarting the device unlock it and recover the key. You can recover the key either manually or set it from console, it will also redirect you to the main screen of the wallet:

```py
# set your entropy
specter.entropy = b'7'*32
# init keys with this entropy and empty password
specter.init_keys("")
# select signet or regtest network
specter.select_network("signet")
```

We could also add these lines to the `main.py` file to init entropy and get to the main screen every time we reboot the device.

Now we can create a descriptor for our new wallet:

```py
from binascii import hexlify

# set up derivation path for the wallet
derivation = "m/84h/1h/0h" # or specter.DEFAULT_XPUBS[0][1]
# get xpub
xpub = specter.keystore.get_xpub(derivation).to_base58()
# get fingerprint
fingerprint = hexlify(specter.keystore.fingerprint).decode()
# construct xpub prefix
prefix = "[%s%s]" % (fingerprint, derivation[1:])
# construct descriptor
descriptor = "taproot(%s%s/_)" % (prefix, xpub)
# let's check what we got
print(descriptor)
# create wallet
specter.keystore.create_wallet("Schnorr", descriptor)
```

**Or** we can add a new **default** wallet with a `taproot` script (add two last lines):

```py
def create_default_wallets():
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

## Preparing Bitcon Core to work with our wallet

Now when we navigate to **Wallets** we see a new wallet called "Schnorr".
When we open it we see the addresses, and these addresses are also printed to the console.

Let's copy the first address and get some money into it. We need Bitcoin Core to watch our addresses in order to contruct transactions for us.

Later we will tune Specter-Desktop to import the addresses and prepare transactions for us, but now let's use JSON-RPC and to it manually. There is an `rpc.py` file in `files` folder that gives us a simple JSON-RPC class that we can connect to our node. 

You can also use command line or AuthProxy from Bitcoin Python testframework if you like.

Create a test wallet where we will import our first address:

```py
from rpc import BitcoinCLI # name is weird, makes sense to rename it

# put your address here
addr = "sb1pwzvw8yfxsupvcgylrlrn6pc376sfxa944vy93p0yegfz3dgsyteqewx2ux"

rpc = BitcoinCLI("specter","TruckWordTrophySolidVintageFieldGalaxyOrphanSeek", 
    protocol="https", host="schnorr.specterwallet.io", port=443)

# test that it works
rpc.getmininginfo()

# some unique name to avoid collisions
wallet_name = "myschnorr"+addr[-4:]
rpc.createwallet(wallet_name, True)
w = rpc.wallet(wallet_name)
w.importmulti()
w.getbalances()
```

Get some money to the wallet here: http://faucet.specterwallet.io/

Now if you call `w.getbalances()` it should show `0.1` BTC in `watchonly` `untrusted_pending`.

We have some money, let's send them back to the faucet.
