# Integration to Specter-Desktop

## Adding new address type: "Taproot"

`new_simple.html`:

```html
<label>
    <input type="radio" name="type" value="taproot" class="hidden">
    <div class="btn radio right">Taproot</div>
</label>
```

## Adding Taproot to Wallet class

helpers

```py
def hash160(data):
    return hashlib.new("ripemd160",
                       hashlib.sha256(data).digest()
                      ).digest()
```

wallet

```py
class Wallet:
    # ...
    def get_derivation(self, address):
        hrp = addr.split(1)[0]
        ver, prog = bech32.decode(hrp, addr)
        prog = bytes(prog)
        address_candidates = [
            bech32.encode(hrp, 0, hash160(b'\x02'+prog)),
            bech32.encode(hrp, 0, hash160(b'\x03'+prog))
        ]
        addr_info = [self.cli.getaddressinfo(addr) for addr in address_candidates]
        info = [info for info in addr_info if "pubkey" in info][0]
        fingerprint = info["hdmasterfingerprint"]
        pubkey = info["pubkey"]
        result = info["hdkeypath"]
        return (pubkey, tuple(
        [int.from_bytes(bytes.fromhex(fingerprint),'little')]+
        [
            int(p) if ("'" not in p) and ("h" not in p) else int(p[:-1])+0x80000000 
            for p in result.split("/") if p!="m"
        ]))

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
    def createpsbt(self, address:str, amount:float, subtract:bool=False, fee_rate:float=0.0, fee_unit="SAT_B"):
        # ...
        # creating a PSBT transaction
        if self.is_taproot:
            rawtx = self.cli.createrawtransaction(extra_inputs,[
                            { address:amount },
                            { self["change_address"]: int(1e8*(total_in-amount)-1500)/1e8 }, # const fee rate
                        ])
            b64psbt = self.cli.converttopsbt(rawtx)
            psbt = PSBT()
            psbt.deserialize(b64psbt)
            for i, inp in enumerate(inputs):
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