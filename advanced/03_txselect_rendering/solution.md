* endresult would be something like this (intentionally a bit more complex than it's needed):

```
<div>
				<table style="table-layout:fixed">
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

```
