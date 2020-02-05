## Implement list on UI
* We want to have the feature below the fee_rate
* That's wallet_send.html line 50 or so
* We want a list, very similiar to the tx-list in wallet_tx.html
* Investigate the list in wallet_tx.html and think what you can reuse
* the List should be coming directly from a bitcoin-core-API-call which lists the unspent transactions. [Research](https://github.com/cryptoadvance/specter-desktop/blob/1aae2fb5c15d865acdf75f2787ab5e8a9b03fde3/tests/test_rpc.py) the way you can access the Bitcoin-Core-API and call it (Another [Hint](https://github.com/cryptoadvance/specter-desktop/search?q=wallet.cli.&unscoped_q=wallet.cli.))
