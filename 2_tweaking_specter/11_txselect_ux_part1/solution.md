* You don't need to define vue.js at the bottom of the page but you would do it like this:
```
<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
```
* after that, the definition of the vue.js application:
  * need to adjust the delimiters as the flask is using the same: ``` delimiters: ["[[", "]]"] ```
  * has data which simply shows whether the table is expanded: ``` data: { coinselection: "hidden" } ```
  * has one method which toggles from "hidden" to "visible"
  
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

* modifying the div to have is under control of vuejs: ``` <div id="coinselect"> ```
* add a button which will toggle: ``` <button v-on:click="toggleExpand" type="button">Expand</button> ```
* bind the table's style attribute to the value of the coinselection: ``` <table v-bind:style="{ visibility: coinselectionActive }"> ```

Here are the two modified sections:
```
			<div id="coinselect">
				<button v-on:click="toggleExpand" type="button">Coinselection</button>
				<table style="table-layout:fixed" v-bind:style="{ visibility: coinselectionActive }">
					<thead>
					<tr>
						<th></th><th>TxID</th><th>Address</th><th>Amount</th>
					</tr>
					</thead>
					<tbody>
						{% for tx in wallet.cli.listunspent() %}
						<tr>
							<td>
								<input type="checkbox" name="coinselect" value="{{tx['txid']}}">
							</td>
							<td class="tx scroll"><a target="blank" href="{{url}}tx/{{tx['txid']}}">{{tx["txid"]}}</a></td>
							<td class="tx scroll"><a target="blank" href="{{url}}address/{{tx['address']}}">{{tx["address"]}}</a></td>
							<td>{{tx["amount"]}}</td>
						</tr>
						{% endfor %}
					</tbody>
				</table>
			</div>

			<button type="submit" name="action" value="createpsbt" class="btn centered">Create unsigned transaction</button>&nbsp; &nbsp; &nbsp; 
		</div>
```
* And the script-block
```
<script>
var app = new Vue({
	el: '#coinselect',
	delimiters: ["[[", "]]"],
	data: {
		coinselectionActive: "hidden",
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

To catchup:
```
git checkout workshop/step11
```
