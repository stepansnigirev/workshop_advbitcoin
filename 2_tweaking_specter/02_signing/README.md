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
This module is injected via the [usermods-folder of the f469-disco repo](https://github.com/stepansnigirev/f469-disco/tree/master/usermods/usecp256k1) and it comes from [bitcoin-core/secp256k1](https://github.com/bitcoin-core/secp256k1/tree/0d9540b13ffcd7cd44cc361b8744b93d88aa76ba). The Schnorr-branch of Stepans fork of f469-disco is therefore [pointing to](https://github.com/stepansnigirev/f469-disco/commit/3d678c5566fe7ba970be2aea5ab49f2322968242#diff-c4aa1791fc332f8ae84b0825dddc1e19) 
[jonasnick's fork](https://github.com/jonasnick/secp256k1/tree/6603c32a10eb0025ac35adc159bf9c57b8e29334) of secp256k1. 
Now let's use this to sign the transaction.

## create the transaction
```py
# add here transaction construction example maybe
from bitcoin import ec, script, transaction
from bitcoin.networks import NETWORKS
from hashlib import sha256
from ubinascii import hexlify

def tagged_hash(tag, msg):
    tag_hash = sha256(tag.encode()).digest()
    return sha256(tag_hash + tag_hash + msg).digest()

network = NETWORKS['signet']

# super secure secret :)
secret = sha256(b'schnorr test').digest()

# private key
pk = ec.PrivateKey(secret)

# public key
pub = pk.get_public_key()

# pubkey in schnorr serialization
pub_ser = pub.sec()[1:]
print(hexlify(pub_ser))

sc = script.Script(b'\x51\x20'+pub_ser)
myaddr = sc.address(network)
print(myaddr)

print("Tx signing")
prevtx = transaction.Transaction.parse(bytes.fromhex("02000000000107eee2525979cf2616d64e7be9c9e2d5d059635d894e47b47b036696b935c55fe30000000000feffffff72653a29c38263ba484d8b7caed4cfa33d75a9b3a856cf6b2b4c096d9cd560220000000000feffffff2ac6084354c41ee0bf6bb28353ab9f12cf4d4588f9bf5f9d3a13c67fa808b29e0000000000feffffffab1c2de8771b5f561c6dba7285f579b1f45ffca169bad1e153482108566080700000000000feffffff67b10d134582fc5262db44333853e34f6aa623ef2abf239df67bcdd22d4f10b30000000000feffffff86d7c8e52bd2b00941cfb2239102fc85108cc95bb4bda34a1fe3fcc9c32294610000000000feffffff4ee6f92a11689b7cf076d2b1c8500af50d87514eb1be39e45511685a9fe990790000000000feffffff02d1ef052a0100000016001472b67bcbb182de5fb3f7498e6ccb795c333ca7c800ac23fc06000000225120e5ce0c67c1600659e3108565ce2d46d26274a7a7782683227cf6ffb0cfccb8d302473044022036ddeb64f09799218beddc28d99f24c88b2a6cc0e30f5383aa0e5cf963046c77022045ae40f5ad1f1b98bbebb784f25a2e2bd0bdcf830c70f0fe10b3a631ff66ec3a012102d857f2a0374bf3fcffc348a2507c65d37fc5a778561cd6565c3146a99b709fb9024730440220337ad2b1772b8cae2b6e984a45e49172ea58fdabb405c342ac28284bdf23756a02202eac1c5d86db1fe45108f5b423b7a3c346fd114d7997dfd170b1884ade108006012102bb1abcf1db3e7d831140daa57c4ed7b8a424594fc5e6e4492de4eb3d90e7daf102473044022053d2de65be8c8a99cfda0d083e01e88bbfc7ad970596c19bd2b10a9697b194d3022028c045b25ac069ae7ed3a297abec1028d52fb318295f41be4340fa2ba8c0faaf01210367d254b3eafe4b303756ee45768a93577b15cc165da94b1d2c99ca5558b3a97d02473044022011599ee52dc1338a0f67ff546c963e64acf4e71f7240eb502d69a056718fc3b002202b08970c1ef3e6c4a1e54feadc168668ff41dd0e32a6e9c5641ad5557769e4290121022b240499b1f92d517b8642f92cfcd115576dc57627ac5d24c4df7147aa381c62024730440220623b3c30d5d1fca6d3c6bc62e93b26172e13662bb0d4bd1a0a71cc54790908fb02205678fbb184c4b822448193a93d9db43b299e564711425c93f2fb65360aff1417012102bda055b146c85fe5b0da85ed6a9696160e5fb74daa0fa6e3377eb128a64ccad1024730440220326a9820ab061144c62a7b29a84ca21197297b0e1e0fbb807340aab96d56084202205f31f095900e14d0d0625e517d360d7722d086977039e9a4f41be91a891d8bf0012103c132aa61f472548a39905b54a8d945f728e520d226897f5b820441e7934d52f802473044022043332a3a53a7224a261f609809d9bac6b92af56eb6c0bc5aafaf51e1d5cd1fd8022021c4f090478d47043d0b54f8409f80f6ddf773adb2577e757a8988f7b8a6a651012103cd81dbb57374fd6b933934981e8a31dcc0f4fa0d341a68ccc54565351ff9662972000000"))
prevout = None
vout = None
for i, out in enumerate(prevtx.vout):
    addr = out.script_pubkey.address(network)
    print(addr)
    if addr == myaddr:
        vout = i
        prevout = out
        break

inputs = [
    # taproot
    {
        "txid": bytes.fromhex("3a715c1decb9a34638b56790abe40a8cd6254ad97d1542906ec4b0e689f3ffa0"),
        "vout": vout,
        "value": prevout.value,
        "script": prevout.script_pubkey
    }
]
# sending back almost the same amount
vin = [transaction.TransactionInput(inp["txid"], inp["vout"]) for inp in inputs]
vout = [transaction.TransactionOutput(inp["value"]-1500, inp["script"]) for inp in inputs]
tx = transaction.Transaction(vin=vin,vout=vout)
print("Unsigned transaction:")
print(tx.serialize().hex())

d = b'\x00' # sighash_all (default)
d += tx.version.to_bytes(4, 'little')
d += tx.locktime.to_bytes(4, 'little')

print("prevouts")
h = sha256()
for inp in tx.vin:
    h.update(bytes(reversed(inp.txid)))
    h.update(inp.vout.to_bytes(4, 'little'))
raw = h.digest()
print(raw.hex())
d += raw

print("amounts")
h = sha256()
for inp in inputs:
    h.update(inp["value"].to_bytes(8, 'little'))
raw = h.digest()
print(raw.hex())
d += raw

print("sequences")
h = sha256()
for inp in tx.vin:
    h.update(inp.sequence.to_bytes(4, 'little'))
raw = h.digest()
print(raw.hex())
d += raw

print("outputs")
h = sha256()
for out in tx.vout:
    h.update(out.serialize())
raw = h.digest()
print(raw.hex())
d += raw

print("spend_type")
raw = b"\x00"
print(raw.hex())
d += raw

print("prevout")
raw = prevout.script_pubkey.serialize()
print(raw.hex())
d += raw

print("index")
raw = b'\x00'*4
print(raw.hex())
d += raw

# ???
d = b'\x00' + d
print(len(d))
print("sighash:", d.hex())
msg = tagged_hash("TapSighash",d)
sig = secp256k1.schnorrsig_sign(msg, secret)
print(sig.hex())
tx.vin[0].witness = script.Witness([sig])

print("Signed transaction:")
print(tx.serialize().hex())

print(msg)
print(sig)
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

    def hash_amounts(self, amounts):
        h = hashlib.sha256()
        for amount in amounts:
            h.update(amount.to_bytes(8, 'little'))
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

# Sign PSBT with Schnorr

Add one condition to the `PSBT.sign_with(root)` method:

```py
class PSBT:
    # ...
    def sign_with(self, root):
        # ...
        # for now only single key, no taproot scripts
        if inp.witness_utxo.script_pubkey.script_type() == "p2taproot":
            values = [inpt.witness_utxo.value for inpt in self.inputs]
            h = self.tx.sighash_taproot(i, inp.witness_utxo.script_pubkey, values)
            sig_schnorr = hdkey.key.schnorr_sign(h)
            inp.final_scriptwitness = Witness([sig_schnorr.serialize()])
        else:
            # segwit
    # ...
```
