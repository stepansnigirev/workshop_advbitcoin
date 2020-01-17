
## Check whether selected coins are sufficient (Skipped, Homework)
* If someone IS selecting coins, he should/want to select ALL of them.
* If he doesn't do it, Core might add coins to that, which don't want to use
* So let's first make sure that we test that server-side and adjust the test. Add this to the end:
```
    # Now let's spend more coins then we have selected. This should result in an exception:
    try:
        psbt = wallet.createpsbt(random_address, number_of_coins_to_spend +1, True, 10, selected_coins=selected_coins)
        assert False, "should throw an exception!"
    except SpecterError as e:
        pass
```
* And implement it serverside (after the if/else-statement):
```
            if still_needed > 0:
                raise SpecterError("Selected coins does not cover Full amount! Please select more coins!")
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
* Now let's move the ```{{amount}}``` from the input-field to the data and bind the data to the input-field similiar to the checkbox. v-model is your friend
* you can check whether you're right by evaluating ``` spend_coins.amount ``` in the console
* Now we need to show a warning if the counselection is active AND the selected coins are not > then the amount the user wants to transfer
```
<div class="notification error" v-if="amount > selected_coins_sum && coinselectionActive != 'hidden'"> You need to select more coins to match your amount!</div>
```
* Something very similiar is wanted for the submit-button. Let's disable the button if we have issues (same condition than the error-message above):
```
v-bind:disabled="amount > selected_coins_sum && coinselectionActive != 'hidden'"
```
* There is however, a change in appearance if you hover over the button. Let's get rid of that (not very nice, though):
```
button:disabled,
button[disabled]{
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
}
.btn:not(.disabled):hover {  
	border: 1px solid #999999;
	background-color: #cccccc;
	color: #666666; 
}
```
