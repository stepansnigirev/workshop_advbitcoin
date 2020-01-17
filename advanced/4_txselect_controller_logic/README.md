
## adjust controller (test?!)
* ```request.form.getlist('hello')``` does the magic here
* pass that into the coinselect-method

## adjust createpsbt-method (test!)
* Investigate test_specter.py[] last function
* At least here we are on a level where we might have tests
* So let's create our own new test which checks the functionality. We'll copy a lot of code from the test before.
  * Spending mined coins has the advantage of stable txids
``` 
def test_wallet_createpsbt(bitcoin_regtest, devices_filled_data_folder, device_manager):
    wm = WalletManager(devices_filled_data_folder,bitcoin_regtest.get_cli(),"regtest")
    # A wallet-creation needs a device
    device = device_manager.get_by_alias('specter')
    key = {
        "derivation": "m/48h/1h/0h/2h",
        "original": "Vpub5n9kKePTPPGtw3RddeJWJe29epEyBBcoHbbPi5HhpoG2kTVsSCUzsad33RJUt3LktEUUPPofcZczuudnwR7ZgkAkT6N2K2Z7wdyjYrVAkXM",
        "fingerprint": "08686ac6",
        "type": "wsh",
        "xpub": "tpubDFHpKypXq4kwUrqLotPs6fCic5bFqTRGMBaTi9s5YwwGymE8FLGwB2kDXALxqvNwFxB1dLWYBmmeFVjmUSdt2AsaQuPmkyPLBKRZW8BGCiL"
    }
    wallet = wm.create_simple('a_second_test_wallet','wpkh',key,device)
    # Let's fund the wallet with ... let's say 40 blocks a 50 coins each --> 200 coins
    address = wallet.getnewaddress()
    assert address == 'bcrt1qtnrv2jpygx2ef3zqfjhqplnycxak2m6ljnhq6z'
    wallet.cli.generatetoaddress(20, address)
    # in two addresses
    address = wallet.getnewaddress()
    wallet.cli.generatetoaddress(20, address)
    # newly minted coins need 100 blocks to get spendable
    # let's mine another 100 blocks to get these coins spendable
    random_address = "mruae2834buqxk77oaVpephnA5ZAxNNJ1r"
    wallet.cli.generatetoaddress(110, random_address)
    # Now we have loads of potential inputs
    # Let's spend 500 coins
    assert wallet.getfullbalance() >= 500
    # From this print-statement, let's grab some txids which we'll use for coinselect
    unspents = wallet.cli.listunspent()
    # Lets take 3 more or less random txs from the unspents:
    selected_coins = [unspents[5]['txid'], 
                    unspents[9]['txid'],
                    unspents[12]['txid']]
    selected_coins_amount_sum = unspents[5]['amount'] + unspents[9]['amount'] + unspents[12]['amount']
    number_of_coins_to_spend = selected_coins_amount_sum - 0.1 # Let's spend almost all of them 
    psbt = wallet.createpsbt(random_address, number_of_coins_to_spend, True, 10, selected_coins=selected_coins)
    assert len(psbt['tx']['vin']) == 3
    psbt_txs = [ tx['txid'] for tx in psbt['tx']['vin'] ]
    for coin in selected_coins:
        assert coin in psbt_txs
``` 
* The implementation should be trivial with this test
  * Ignoring the possibility to have coins selected which are not confirmed
  * Assuming that no one selected coins if his full balance is not even enough and we need unconfirmed coins
  * ==> in that case you simply need to have an else case like this:
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
