# Integration to Specter-Desktop

## Adding new address type: "Taproot"

First we need to change the HTML file to get a new wallet type. 

File `templates/new_simple.html`:

```html
{% if sigs_total %}
...
{% else %}
...
<label>
    <input type="radio" name="type" value="taproot" class="hidden">
    <div class="btn radio right">Taproot</div>
</label>
{% endif %}
```

Now if we select "Taproot" as wallet type we will see that Specter doesn't know which keys to use. So let's tell it that BIP-84 keys are ok for taproot as well.

Routes are defined in `controller.py`:

```py
@app.route('/new_wallet/simple/', methods=['GET', 'POST'])
def new_wallet_simple():
    # ...
    # this lines defines what key types we can use
    allowed_types = [None, wallet_type]
    # this is what we need to add:
    if wallet_type == "taproot":
        allowed_types.append("wpkh")
```

Now we need to tell the wallet logic how to import this type of descriptor as at the moment it will fail.

If we check what happens when we select the key we would see that this call is made:

```py
wallet = app.specter.wallets.create_simple(wallet_name, wallet_type, key, device)
```

This means that we need to tweak the `Wallets.create_simle()` method.

```py
    # ...
    def create_simple(self, name, key_type, key, device):
        # ...
        if key_type == "taproot":
            recv_desc = "wpkh(%s)" % (recv_desc)
            change_desc = "wpkh(%s)" % (change_desc)
        else:
            for el in arr[::-1]:
                recv_desc = "%s(%s)" % (el, recv_desc)
                change_desc = "%s(%s)" % (el, change_desc)
```

Notice that when we create a new wallet it also saves the address type to the dictionary. We can use this `"address_type": addrtypes[key_type]` to detect if the wallet is taproot or not.

We only need to update the `addrtypes` and `purposes` global dict:
```py
purposes = OrderedDict({
    #...
    "taproot": "Single (Taproot)",
})

addrtypes = {
    # ...
    "taproot": "taproot",
}
```

For now nothing really works yet, we need to tune the `Wallet` class further with the code we wrote in the last part.

## Adding Taproot to Wallet class

`Wallet` class needs the following functionality:

- it needs to know it is taproot (`is_taproot` property)
- it should be able to derive addresses (`get_taproot_address(descr, idx, change)`)
- it should create psbt transaction (tweak `createpsbt`, also would require `get_derivation`)
- it should be able to refill addresses it is watching

You will see similar hacks for `is_multisig` everywhere because we had to tweak old Core to support `sortedmulti` descriptor. 

```py
import bech32
from serializations import PSBT, CTransaction
from io import BytesIO
import hashlib

def hash160(data):
    return hashlib.new("ripemd160",
                       hashlib.sha256(data).digest()
                      ).digest()

class Wallet:
    # ...
    @property
    def is_taproot(self):
        return (self._dict["address_type"]=="taproot")

    def get_address(self, index, change=False):
        # ...
        if self.is_taproot:
            return self.get_taproot_address(self[desc], index, change=change)

    def get_taproot_address(self, descriptor, index, change=False):
        if index is not None:
            descriptor = descriptor.replace("*", f"{index}")
        # remove checksum
        descriptor = descriptor.split("#")[0]
        # get address (should be already imported to the wallet)
        address = self.cli.deriveaddresses(AddChecksum(descriptor))[0]

        # get pubkeys involved
        address_info = self.cli.getaddressinfo(address)
        if 'pubkey' in address_info:
            pubkey = address_info["pubkey"]
        else:
            raise Exception("Could not find 'pubkeys' in address info:\n%s" % json.dumps(address_info, indent=2))
        xonly = bytes.fromhex(pubkey)[1:]
        hrp = address.split("1")[0]
        tapaddr = bech32.encode(hrp, 1, xonly)
        return tapaddr

    # ...
    def get_derivation(self, addr):
        hrp = addr.split("1")[0]
        ver, prog = bech32.decode(hrp, addr)
        prog = bytes(prog)
        address_candidates = [
            bech32.encode(hrp, 0, hash160(b'\x02'+prog)),
            bech32.encode(hrp, 0, hash160(b'\x03'+prog))
        ]
        addr_info = [self.cli.getaddressinfo(addr) for addr in address_candidates]
        info = [info for info in addr_info if "pubkey" in info][0]
        fingerprint = info["hdmasterfingerprint"]
        pubkey = bytes.fromhex(info["pubkey"])
        result = info["hdkeypath"]
        return (pubkey, tuple(
        [int.from_bytes(bytes.fromhex(fingerprint),'little')]+
        [
            int(p) if ("'" not in p) and ("h" not in p) else int(p[:-1])+0x80000000 
            for p in result.split("/") if p!="m"
        ]))

    def keypoolrefill(self, start, end=None, change=False):
        # ...
        if self.is_taproot:
            args[0].pop("range")
            args[0].pop("desc")
            for i in range(start,end):
                args[0]["scriptPubKey"] = {"address": self.get_taproot_address(self[desc], i, change=change)}
                self.cli.importmulti(args, timeout=120)

    def createpsbt(self, address:str, amount:float, subtract:bool=False, fee_rate:float=0.0, fee_unit="SAT_B"):
        # ...
        extra_inputs = []
        trusted_balance = self.balance["trusted"]
        extra_in_amount = 0
        if self.is_taproot:
            trusted_balance = 0
        if trusted_balance < amount:
            if self.is_taproot:
                txlist = self.cli.listunspent(0)
            else:
                txlist = self.cli.listunspent(0,0)
            b = amount-self.balance["trusted"]
            for tx in txlist:
                extra_inputs.append({"txid": tx["txid"], "vout": tx["vout"]})
                b -= tx["amount"]
                extra_in_amount += tx["amount"]
                if b < 0:
                    break;

        # subtract fee from amount of this output:
        # currently only one address is supported, so either
        # empty array (subtract from change) or [0]
        subtract_arr = [0] if subtract else []

        if self.is_taproot:
            rawtx = self.cli.createrawtransaction(extra_inputs,[
                            { address:amount },
                            { self["change_address"]: int(1e8*(extra_in_amount-amount)-1500)/1e8 }, # const fee rate
                        ])
            b64psbt = self.cli.converttopsbt(rawtx)
            psbt = PSBT()
            psbt.deserialize(b64psbt)
            for i, inp in enumerate(extra_inputs):
                rawtx = bytes.fromhex(self.cli.gettransaction(inp["txid"])["hex"])
                tx = CTransaction()
                tx.deserialize(BytesIO(rawtx))
                psbt.inputs[i].witness_utxo = tx.vout[inp["vout"]]
                pub, der = self.get_derivation(inp["address"])
                psbt.inputs[i].hd_keypaths[pub] = der
            pub, der = self.get_derivation(self["change_address"])
            psbt.outputs[1].hd_keypaths[pub] = der
            b64psbt = psbt.serialize()
        else:
            # ...
```