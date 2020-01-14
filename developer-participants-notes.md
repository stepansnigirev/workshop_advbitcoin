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
* At least here we are on a level where we might have testst
* Let's look at the tests


## take unconfimed transaction into account

## Hide UI (extended functionality) with javascript

# Advanced Transaction-verification on hardwarewallet (Stepan)

