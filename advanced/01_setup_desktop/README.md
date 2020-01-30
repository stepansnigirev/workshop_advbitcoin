# Goal
Effective development needs an effective Developer-setup:
* Let the solution run on your desktop
* Run tests and debug tests in your IDE
* Debug the solution in your IDE
This is a command and contemplation exercise.

# Basic Setup

* Git clone and get the server to run as described in [how to run](https://github.com/cryptoadvance/specter-desktop#how-to-run)
* Choose your IDE. If you're not familiar wirh python and an IDE:
  * Download and run [Visual Studio Code](https://code.visualstudio.com/)
  * Install the [python-extension](https://code.visualstudio.com/docs/languages/python#_install-python-and-the-python-extension)
* Make a dummy change in any HTML-page (e.g. base.html) and watch how source-changes get immediately detected
* The same is true for any python-code changes. In that case, the server get restarted automatically
* Create a device based on Specter-DIY
* Without a running bitcoin-core-node, it's difficult to do anything reasonable. Change that with the help of [this section](https://github.com/cryptoadvance/specter-desktop/blob/master/DEVELOPMENT.md#more-on-the-bitcoind-requirements)
* Create two single wallets based on the specter-device (one segwit, one nested-segwit)
* Restart the docker-container to get both wallets funded 
* send a coin from one wallet to the other

# Test Setup
* [Run the tests](https://github.com/cryptoadvance/specter-desktop/blob/master/DEVELOPMENT.md#run-the-tests)
* Run a single test in a specific file
* [Run a single-test](https://github.com/cryptoadvance/specter-desktop/blob/master/DEVELOPMENT.md#unit-tests-in-vs-code) in your IDE as described here (for Visual-Studio-code)
* On the IDE run all the tests via the test-pane

# Debugging Setup
* In order to be able to do debugging, create a launch-configuration as described [here](https://github.com/cryptoadvance/specter-desktop/blob/master/DEVELOPMENT.md#debugging-in-vs-code)
* Add breakpoints and debug a test
* Add breakpoints and debug the application (port 5000)

Contemplate about what you just did. Is anything missing which would support you with development work?
