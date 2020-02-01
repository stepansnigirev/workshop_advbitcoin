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

```py
class Wallet:
    # ...
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
        # add to the address index
        self._dict["derivations"][tapaddr] = {"pubkey": pubkey, "der": [int(change), index]}
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
                derivation = self._dict["derivations"][inp["address"]]
                #  = {"pubkey": pubkey, "der": [int(change), index]}
                pub = bytes.fromhex(derivation["pubkey"])
                der = (
                    int.from_bytes(bytes.fromhex(self._dict["key"]["fingerprint"]),'little'),
                    0x80000000+84,
                    0x80000000+1,
                    0x80000000,
                    derivation["der"][0],
                    derivation["der"][1])
                psbt.inputs[i].hd_keypaths[pub] = der
            derivation = self._dict["derivations"][self["change_address"]]
            pub = bytes.fromhex(derivation["pubkey"])
            der = (
                    int.from_bytes(bytes.fromhex(self._dict["key"]["fingerprint"]),'little'),
                    0x80000000+84,
                    0x80000000+1,
                    0x80000000,
                    derivation["der"][0],
                    derivation["der"][1])
            psbt.outputs[1].hd_keypaths[pub] = der
            b64psbt = psbt.serialize()
        else:
            # ...
```