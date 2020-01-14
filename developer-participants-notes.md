# prerequisites
* Your laptop with linux, Windows or Mac-OS
* Python >= 3.7 installed via your preferred installation method
* pip install virtualenv
* You'll need either bitcoind available (> 0.18.1) on the commandline or docker installed
* your favorite IDE, VisualStudioCode if you don't have one. If you use your own, we assume that you know how you can debug flask applications
* optional: Have a testing hardwarewallet, one of coldcard, Specter-DIY or any other compatible HWI-compatible hardwarewallet

# Setup (Kim)
Goal and intermediate steps:
* Run the software in development-mode (modifyable sources immediately detected) without a bitcoincore on port 25441
* Creating a device based on Specter-DIY
* a docker-running-regtest-bitcoind, configuring in specter-desktop
* Create a two simple wallets, get them coins funded, send a coin from one wallet to the other (regtest)
* Run the tests:
  * on the commandline, choose file and specific test
  * On the IDE run all the tests or soecific ones
* Add breakpoints and debug the tests
* Add breakpoints and debug the application (port 5000)

# Setup hardware-hacking (Stepan)
* Download the firmware from somewhere and deploy on hardware


# Coinselection (Kim)

## Investigate current aspects relevant to coinselection
* Start Specter-desktop, go to the spend-page: http://127.0.0.1:25441/wallets/simple/send/
* guides us to the controller: controller.py[274]
* guides us to the template: wallet_send.html
* guides us as well to the createpsbt-method which will use the coins selected to create the psbt
* That means we now know which places we have to modify in specter-desktop:
  * wallet_send.py - create the UI-list of potential coins selectable
  * wallet_send-controller - grabbing the selected coins from the request.form + passing it in createpsbt
  * wallet.createpsbt - adjusting the code there to select the coins

## Implement list on UI
* We want to have the feature below the fee_rate
* That's wallet_send.html line 50 or so
* We want a list, very similiar to the tx-list in wallet_tx.html
* so let's copy and paste the table there
```

```
* endresult would be something like this (intentionally a bit more complex than it's needed):

```
			<table>
				<thead>
				<tr>
					<th></th><th>TxID</th><th>Address</th><th>Amount</th>
				</tr>
				</thead>
				<tbody>
					{% for tx in wallet.cli.listunspent() %}
					{%if tx["confirmations"] == 0 %}
					<tr class="unconfirmed">
					{%else%}
					<tr>
					{%endif%}
						<td>
							{# coinbase txs are 'immature' until 100 confs #}
							{% if tx['category'] == 'immature' %}0
								<img src="/static/img/unconfirmed_receive_icon.svg"/>
							{% else %}
								{% if tx["confirmations"] == 0 %}
								<img src="/static/img/unconfirmed_{{tx['category']}}_icon.svg"/>
								{% else %}
								<img src="/static/img/{{tx['category']}}_icon.svg"/>
								{% endif %}
							{% endif %}
							<input type="checkbox" name="coinselect" value="{{tx['txid']}}">
						</td>
						<td class="tx scroll"><a target="blank" href="{{url}}tx/{{tx['txid']}}">{{tx["txid"]}}</a></td>
						<td class="tx scroll"><a target="blank" href="{{url}}address/{{tx['address']}}">{{tx["address"]}}</a></td>
						<td>{{tx["amount"]}}</td>
						<td>
						{%if tx["confirmations"] == 0 %}
							Pending
						{% else %}
							{{tx["confirmations"]}}
						{% endif %}
						</td>
					{% endfor %}
				</tbody>
			</table>

```

## adjust controller (test?!)
* ```request.form.getlist('hello')``` does the magic here
* pass that into the coinselect-method

## adjust createpsbt-method (test!)
* Investigate test_specter.py[] last function
* At least here we are on a level where we might have tests
* So let's create our own new test which checks the functionality. We'll copy a lot of code from the test before.
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
    #print(wallet.cli.listunspent())
    selected_coins = ['dc229dfd4b1f99de7a6284ba90dbbeb2ed13dfdd5829b56a0378301a50e30a57', 
                    'c119ab140fd0da414476e5dfd52c0f83c0e2e09fcab8d830d3898e74432a2567',
                    '8b4fdc339a32351c5eeef546d5b8a336f287727fbb427c8676d3d552bfdb0397']
    # Let's make sure the selected_coins are really in the listunspent
    all_unspent = [ tx['txid'] for tx in wallet.cli.listunspent() ]
    assert set(selected_coins).issubset(all_unspent)
    psbt = wallet.createpsbt(random_address, 154, True, 10, selected_coins=selected_coins)
    assert len(psbt['tx']['vin']) == 4
    psbt_txs = [ tx['txid'] for tx in psbt['tx']['vin'] ]
    for coin in selected_coins:
        assert coin in psbt_txs
``` 
* Let's look at the tests


## take unconfimed transaction into account

## Hide UI (extended functionality) with javascript

# Advanced Transaction-verification on hardwarewallet (Stepan)

