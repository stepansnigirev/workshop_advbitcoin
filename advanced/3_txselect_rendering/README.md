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