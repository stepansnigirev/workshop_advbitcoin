# Adapting the controller
* The controller-method just need to add one line and adjust another one:
* one for obtaining the list:
```
selected_coins = request.form.getlist('coinselect')
```
* The "coinselect" is referring to the value of the name-attribute of the input-tag of type checkbox
* and adjust the call to createpsbt:
```
psbt = wallet.createpsbt(address, amount, subtract=subtract, fee_rate=fee_rate, selected_coins=selected_coins)
```

# Adapting the logic

* The if-statement is checking whether you need to spend unconfirmed coins in order to be able to send the amount chosen
* In that case, selecting coins doesn't make much sense as you would need to choose all of them.
* So we can use a new else-statement here to fill up the extra_inputs with the selected coins
```
        else:
            txlist = self.cli.listunspent()
            still_needed = amount
            for tx in txlist:
                if tx['txid'] in selected_coins:
                    extra_inputs.append({"txid": tx["txid"], "vout": tx["vout"]})
                    still_needed -= tx["amount"]
                    if still_needed < 0:
                        break;
```

The whole method:
```
    def createpsbt(self, address:str, amount:float, subtract:bool=False, fee_rate:float=0.0, selected_coins=[]):
        """
            fee_rate: in sat/B. Default (None) bitcoin core sets feeRate automatically.
        """
        if self.fullbalance < amount:
            return None
        extra_inputs = []
        if self.balance["trusted"] < amount:
            txlist = self.cli.listunspent(0,0)
            b = amount-self.balance["trusted"]
            for tx in txlist:
                extra_inputs.append({"txid": tx["txid"], "vout": tx["vout"]})
                b -= tx["amount"]
                if b < 0:
                    break;
        else:
            txlist = self.cli.listunspent()
            still_needed = amount
            for tx in txlist:
                if tx['txid'] in selected_coins:
                    extra_inputs.append({"txid": tx["txid"], "vout": tx["vout"]})
                    still_needed -= tx["amount"]
                    if still_needed < 0:
                        break;


        # subtract fee from amount of this output:
        # currently only one address is supported, so either
        # empty array (subtract from change) or [0]
        subtract_arr = [0] if subtract else []

        options = {   
            "includeWatching": True, 
            "changeAddress": self["change_address"],
            "subtractFeeFromOutputs": subtract_arr
        }
        if fee_rate > 0.0:
            # bitcoin core needs us to convert sat/B to BTC/kB
            options["feeRate"] = fee_rate / 10 ** 8 * 1024

        # Dont reuse change addresses - use getrawchangeaddress instead
        r = self.cli.walletcreatefundedpsbt(
            extra_inputs,           # inputs
            [{address: amount}],    # output
            0,                      # locktime
            options,                # options
            True                    # replaceable
        )
        b64psbt = r["psbt"]
        psbt = self.cli.decodepsbt(b64psbt)
        psbt['base64'] = b64psbt
        # adding xpub fields for coldcard
        cc_psbt = PSBT()
        cc_psbt.deserialize(b64psbt)
        if self.is_multisig:
            for k in self._dict["keys"]:
                key = b'\x01'+helpers.decode_base58(k["xpub"])
                value = bytes.fromhex(k["fingerprint"])+der_to_bytes(k["derivation"])
                cc_psbt.unknown[key] = value
        psbt["coldcard"]=cc_psbt.serialize()
        return psbt
```

to catchup:
```
git checkout training/step04
```
