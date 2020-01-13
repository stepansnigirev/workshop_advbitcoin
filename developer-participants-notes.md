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


# Coinselection (Kim)

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

'''
Some code for cut&paste here
'''

## adjust controller (test?!)
* '''request.form.getlist('hello')''' is the magic here

## adjust createpsbt-method (test!)
* Investigate test_specter.py[] last function.

## take unconfimed transaction into account

## Hide UI (extended functionality) with javascript

# Advanced Transaction-verification on hardwarewallet (Stepan)

