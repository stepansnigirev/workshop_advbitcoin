* Use vue.js at the bottom of the page in the scripts-block:
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
			</div>
```
* And the script-block
```
<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>

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
