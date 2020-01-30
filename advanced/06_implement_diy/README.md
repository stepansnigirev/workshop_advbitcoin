# Coinselection on a hardware wallet

We want to verify that we are signing a transaction with correct inputs and outputs.

By default the wallet only shows the spending address, spending amount and the fee.

We want to change it and to display:
- where the money are coming from (address & amount)
- what is our change address
- what is the spending address and the amount we are spending
- fee

Last two parts are already implemented, we need to implement the first two.

First we need to find a place where the transaction is parsed. In case of both QR scanning and USB communication `parse_transaction` function from `main.py` is called, so let's check it out:

First let's write a small script that will get to the right screen for us - bypass the PIN code, set entropy and password, and trigger `parse_transaction` function with the right transaction:

```py
import main

main.main(blocking=False)
main.entropy = b'\x06^\x9d\xdeh\x03\x03\x15\xd2\x11-\xb0\xa4<\xad#'
main.init_keys("")
b64_tx = "cHNidP8BAHICAAAAAYy/irkURQej+KSpUP8Mj4z7hu55HvS38tiqEFuabZuJAQAAAAD+////AtgNWAgAAAAAFgAUQ7ZZwmeagBjqnBbjzw5O3/bXyb+AlpgAAAAAABepFPPNvp1TAyho+Kys4wwejY8iakgQhwAAAAAAAQEfcK/wCAAAAAAWABTXC3V1+yTvyRHUR4Xh88/OPqNPDSIGAjhBH5LpFYKwwKQfv6h7X+/jAf3RvutvH2FZaDCTZ9ccGLMX7IZUAACAAQAAgAAAAIABAAAAAgAAAAAiAgK0Sr4YiELDJ1sUmCpFjIRpEEOoAKyjAstZuMtDUMSTsxizF+yGVAAAgAEAAIAAAACAAQAAAAMAAAAAAA=="
main.parse_transaction(b64_tx)
```

The important line is:

```py
data = keystore.check_psbt(tx)`
```

We pass our parsed transaction to the `keystore` object that knows everything about our wallets and keys, and get back a simple dictionary that we then display as a message with a `popup.promt()` function.

We try to separate all the bitcoin-related stuff from the GUI, now we need to investigate what happens in `keystore.check_psbt(tx)` function. It is implemented in `keystore.py`, class `KeyStore`.

Returned object contains the following keys: 
- `total_in` - sum of all inputs, 
- `spending` - amount we send away from the wallet,
- `wallet` - the wallet that inputs belong to (we don't support mixed inputs for security reasons),
- `send_outputs` - array of `{"value", "address"}` dicts that show what outputs we are sending to, but without change outputs
- `fee` - fee

Let's add two new field here, `inputs` and `change_outputs`, and put there again `{"value", "address"}` dicts:

```py
obj["change_outputs"] = [{"value": out.value, "address": out.script_pubkey.address(self.network)} for out in tx.tx.vout if out not in send_outputs]
obj["inputs"] = [{"value": inp.witness_utxo.value, "address": inp.witness_utxo.script_pubkey.address(self.network)} for inp in tx.inputs]
```

Now in `parse_transaction` function of `main.py` we just need to display that:

```py
message = "Inputs:\n"
for inp in data["inputs"]:
    message += "%u sat from %s\n" % (inp["value"], inp["address"])
message += "\nOutputs:\n"
for out in data["send_outputs"]:
    message += "%u sat to %s\n" % (out["value"], out["address"])
message += "\nChange:\n"
for out in data["change_outputs"]:
    message += "%u sat to %s\n" % (out["value"], out["address"])
message += "\nFee: %u satoshi" % data["fee"]
```

That's it! The only thing that this screen looks ugly now, so maybe let's slightly change the appearence.

We won't work on this too much, some small things we can do to make it slightly better - add some recoloring, change fonts to smaller size, align to the left:

```py
title = "Spending %u\nfrom %s" % (data["spending"], data["wallet"].name)
message = "Inputs:\n"
for inp in data["inputs"]:
    message += "%u sat from %s\n" % (inp["value"], inp["address"])
message += "\n#ffffff Outputs:\n"
for out in data["send_outputs"]:
    message += "#ffffff %u sat to\n#ffffff %s\n" % (out["value"], out["address"])
message += "\nChange:\n"
for out in data["change_outputs"]:
    message += "%u sat to %s\n" % (out["value"], out["address"])
message += "\n#ffffff Fee: %u satoshi" % data["fee"]
scr = popups.prompt(title, message, ok=cb_with_args(sign_psbt, wallet=data["wallet"], tx=tx, success_callback=success_callback), cancel=cb_with_args(error_callback, "user cancel"))
scr.message.set_align(lv.label.ALIGN.LEFT)
scr.message.set_recolor(True)
scr.message.set_style(lv.label.STYLE.MAIN, gui.common.styles['hint'])
```
