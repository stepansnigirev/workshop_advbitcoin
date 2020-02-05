## Investigate current aspects relevant to coinselection
* Start Specter-desktop, go to the spend-page: http://127.0.0.1:25441/wallets/simple/send/
* Searching for the last part of the url guides us to the controller: controller.py[274]
* The return-statement guides us to the relevant template: wallet_send.html
* Also it guides us as well to the createpsbt-method which will use the coins selected to create the psbt: logic.py[677]
* That means we now know which places we have to modify in specter-desktop:
  * [wallet_send.html](https://github.com/cryptoadvance/specter-desktop/blob/master/src/specter/templates/wallet_send.html) - create the UI-list of potential coins selectable
  * [wallet_send-controller.py](https://github.com/cryptoadvance/specter-desktop/blob/8fd67008ff480ed06b14ae4ab6d87a5fcf473cbd/src/specter/controller.py#L306-L343) - grabbing the selected coins from the request.form + passing it in createpsbt
  * [wallet.createpsbt](https://github.com/cryptoadvance/specter-desktop/blob/1aae2fb5c15d865acdf75f2787ab5e8a9b03fde3/src/specter/logic.py#L692-L747) - adjusting the code there to forward the selected coins to bitcoin-core
