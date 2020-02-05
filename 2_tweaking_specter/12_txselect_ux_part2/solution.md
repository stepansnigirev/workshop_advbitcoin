
# Server-side check for sufficient coin-selection

* The test could be fulfilled with this statement after the for-loop:
```
            if still_needed > 0:
                raise SpecterError("Selected coins does not cover Full amount! Please select more coins!")
```

* However the test won't suceed! Why not?
* The selected coins is empty, we're still entering the else-part. That's not intended and so we have to adjust the else part:
```
elif selected_coins != []: # Let's only do that if the user have selected coins!
```

# Migrate the list of unspent coins to Vue.js

* Add the list of unspent to the vue.js-data: unspents: ``` {{ wallet.cli.listunspent()|tojson }} ```

* As we want to sumup the checked amounts and we want to do that in the model, we need to replace the jinja2 created list with a vue-js rendered list. We can replace the whole ```{% for tx in wallet... %}...{% endfor %}``` with this:
```
						<tr v-for="tx in unspents" v-bind:key="tx.txid">
							<td>
								<input type="checkbox" v-model="tx.selected" name="coinselect" v-bind:value="tx.txid">
							</td>
							<td class="tx scroll"><a target="blank">[[ tx.txid ]]</a></td>
							<td class="tx scroll"><a target="blank">[[ tx.address ]]}</a></td>
							<td>[[ tx.amount ]]</td>
						</tr>
```

## Bind back the checkbox-checks to the data

* Modify the input-box like this:
```
<input type="checkbox" v-model="tx.selected" name="coinselect" v-bind:value="tx.txid"><
```

## Compute the sums of all selected txs

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

## Warning message and Disabling the submit-button

* The whole vue-js-application-definition:
```
<script>
var spend_coins = new Vue({
	el: '#spend_coins',
	delimiters: ["[[", "]]"],
	data: {
		unspents: {{ wallet.cli.listunspent()|tojson }},
		coinselectionActive: "hidden",
		amount: {{amount}}
	},
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
	},
	methods: {
        toggleExpand: function() {
			if (this.coinselectionActive =="hidden") {
				this.coinselectionActive ="visible"
			} else {
				this.coinselectionActive ="hidden"
			}
		}
   }

})
</script>
```

* The notification div
```
<div class="notification error" v-if="amount > selected_coins_sum && coinselectionActive != 'hidden'"> You need to select more coins to match your amount!</div>
```

* the (deactivated) submit-button
```
v-bind:disabled="amount > selected_coins_sum && coinselectionActive != 'hidden'"
```
* In addition to that the css-style is not very ux-friendly. If you hover over the button, you can't see that the button is disabled.
* You could fix that e.g. with:
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

to catchup:
```
git checkout upstream training/step12
```
