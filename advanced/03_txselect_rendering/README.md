## Implement list on UI
* We want to have the feature below the fee_rate
* That's wallet_send.html line 50 or so
* We want a list, very similiar to the tx-list in wallet_tx.html
* Investigate the list in wallet_tx.html and think what you can reuse
* the List is coming directly from a bitcoin-core-API-call which lists the unspent transactions. Research the call and call it. ["wallet.cli"](https://github.com/cryptoadvance/specter-desktop/blob/master/src/specter/logic.py#L458) exposes you to the Bitcoin-API.