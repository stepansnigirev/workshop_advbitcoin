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


# Coinselection

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


# Advanced Transaction-verification on hardwarewallet (Stepan)


# CoinSelection UI/UX optimized
All the improvements in this chapter will be done with the help of vue.js. We're not assuming you have any knowledge about vue.js. So let's have a crashcourse in vue.js first

## Crash Course in vue.js
* copy these lines somewhere in controller.py
```
@app.route('/vuejs/crashcourse/', methods=['GET'])
def vuejs_crashcourse():
    return render_template("vuejscrashcourse.html", some_Value="Hello Vue.js", some_array=["one","two","three"])
```
* Create a new file in src/specter/templates/vuejscrashcourse.html with this content:
```
{% extends "base.html" %}
Have a look in base.html. It consists of several blocks which we can override.<br> 
The main usecase is probably to override the block main:<br> 
{% block main %}

flask is using jinja2-templating. We render values like this:<br><br> 
{{ some_Value }}<br> <br> 
<br> <br> 
We have control-flow like this:<br> 
{% if not some_bool %} 
    Something<br> <br> 
{% else %}
    Something else<br> <br> 
{%endif %}


Vue.js uses the same delimeters for rendering values then flask: double curly brackets<br> 
For heaven sake one can change that. See the delimiter-stance below.<br> <br> 

So vue-js manages a specific part of the html-page that's marked with an id defined via "el" in the definition of the VUE-app (see below).<br> <br> 
<br> <br> 
<div id="app">
    We can now render stuff from the data-section (which will get rendered by jinja2):<br> 
    * some_bool: [[some_bool]]<br> 
    * some_array: [[some_array]]<br> 
    * but also computed values:
    [[some_computed_value]]

    You can have buttons which call methods:<br> 
    <button v-on:click="some_method" type="button">Coinselection</button>
    Here is an example of rendering an array via an implicit loop. <br>
    We can loop back the status of the checkbox in the data by "v-model" and "v-bind:value"<br>
    The change of the data is immediately reflexted in rendering.<br>
    <div v-for="x in some_array">
        <input type="checkbox" v-model="x.selected" v-bind:value="x" >[[ x ]]</input>
    </div>
    End of crashcourse.

</div>

<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
<script>
var app = new Vue({
	el: '#app',
	delimiters: ["[[", "]]"],
	data: {
		some_array: {{ some_array|tojson }},
		some_bool: {{ some_bool|tojson }},
	},
	computed: {
		some_computed_value: function () {
            return this.some_array.reverse()
        }
	},
	methods: {
        some_method: function() {
			alert("Hello!")
		}
   }

})
</script>

{% endblock %}
```
* Investigate what you just have created!


## Hide UI (extended functionality) with vue.js
* Let's do a toggling of the feature and unexpand by default
* let's use vue.js at the bottom of the page (to be fixed! Maybe in main-template?!):
```
<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
```
* So after that, we'll create a vue.js application which fulffills these requirements:
  * need to adjust the delimiters as the flask is using the same: ``` delimiters: ["[[", "]]"] ```
  * has data which simply shows whether the table is expanded: ``` data: { coinselection: "hidden" } ```
  * has one method which toggles from "hidden" to "visible":
```
  methods: {
        toggleExpand: function() {
			if (this.coinselectionActive =="hidden") {
				this.coinselectionActive ="visible"
			} else {
				this.coinselectionActive ="hidden"
			}
		}
   }
```
* Now modify the div to have is under control of vuejs: ``` <div id="coinselect"> ```
* add a button which will toggle: ``` <button v-on:click="toggleExpand" type="button">Expand</button> ```
* bind the table's style attribute to the value of the coinselection: ``` <table v-bind:style="{ visibility: coinselectionActive }"> ```
* Done

## 

## Check whether selected coins are sufficient (Skipped, Homework)
* If someone IS selecting coins, he should/want to select ALL of them.
* If he doesn't do it, Core might add coins to that, which don't want to use
* So let's first make sure that we test that server-side and adjust the test:
```
ToBeDone
```
* And implement it serverside
```
ToBeDone
```
* Let's implement that now client-side and check it via Vue.js
* Add the list of unspent to the vue.js-data: unspents: ``` {{ wallet.cli.listunspent()|tojson }} ```
* As we wamt to sumup the checked amounts and we want to do that in the model, we need to replace the jinja2 created list with a vue-js rendered list. We can replace the whole ```{% for tx in wallet... %}...{% endfor %}``` with this:
```
						<tr v-for="tx in unspents" v-bind:key="tx.txid">
							<!-- <img v-if="tx.category == 'immature'" src="/static/img/unconfirmed_receive_icon.svg"/>
							<img v-if="tx.confirmations == 0'" src="/static/img/unconfirmed_[[ tx.category ]]_icon.svg"/>
							<img v-else src="/static/img/[[ tx.category ]]_icon.svg"/> -->
							<td><input type="checkbox" name="coinselect" value="[[ tx.txid ]]"></td> 
							<td class="tx scroll"><a target="blank" >[[ tx.txid ]]</a></td>
							<td class="tx scroll"><a target="blank" >[[ tx.address ]]</a></td>
							<td>[[ tx.amount ]]</td>
							<td v-if="tx.confirmations == 0">Pending</td>
							<td v-else>[[ tx.confirmations ]]</td>
						</tr>
```
* We've lost some features like the href and the conditional image rendering (commented) but let's deal with that later (TODO)
* There is also an issue with "in-attribute-rendering" for the checkbox. Replace it with: ```v-bind:value="tx.txid"```
* This should already render properly, but now we need to bind that back to the data. That's done with v-model which binds the checkbox to a non-existinmg attribute inside the data: "selected"
```
<input type="checkbox" v-model="tx.selected" name="coinselect" v-bind:value="tx.txid"><
```
* This can now be tested inside the console by evaluating ```coinselection._data.unspents[0].selected```
* It should be undefined in the beginning and true/false depending on the check
* We're not struggling on the undefined and now we can compute the sum of Amounts of all txs which are selected
```
	computed: {
		selected_coins_sum: function () {
            		amount_sum = 0
			for(var i=0;i<this.unspents.length;i++){
				if (this.unspents[i].selected) {
					amount_sum += this.unspents[i].amount
				}
			}
			return amount_sum
        	}
	}
```
* Now, we have to compare that against the Amount-value in the input-box and print-out some warning if amount < selected_coins_sum (in the case that the coinselection is expanded)
* However, the Amount-input-box is not (yet) managed by Vue. So let's change that, wrap the form in a div, rename the app to "spend_coins" ( ```el: '#spend_coins'```) and mark the div with that id: ``` <div id="spend_coins"> ```
* Now let's move the ```{{amount}}``` from the input-field to the data and bind the data to the input-field similiar to the checkbox. v-model and v-bind:value is your friend
* you can check whether you're right by evaluating ``` spend_coins.amount ``` in the console
* Now we need to show a warning if the counselection is active AND the selected coins are not > then the amount the user wants to transfer
```
<div class="notification error" v-if="amount > selected_coins_sum && coinselectionActive != 'hidden'"> You need to select more coins to match your amount!</div>
```

## take unconfimed transaction into account


