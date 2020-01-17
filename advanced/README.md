# prerequisites
* Your laptop with linux, Windows or Mac-OS
* Python >= 3.7 installed via your preferred installation method
* pip install virtualenv
* You'll need either bitcoind available (> 0.18.1) on the commandline or docker installed
* your favorite IDE, VisualStudioCode if you don't have one. If you use your own, we assume that you know how you can debug flask applications
* optional: Have a testing hardwarewallet, one of coldcard, Specter-DIY or any other compatible HWI-compatible hardwarewallet

# Table of contents

- [Step 1. Setup Desktop](./1_setup_desktop/README.md) The foundation of effective Development is a good Development-Setup
- [Step 2. Investigate for coin selection](./2_coinselection_investigate/README.md) look at the stuff which is relevant for coin selection
- [Step 3. Unspents List](./3_coinselection_list_rendering/README.md) Render the unspent transactions
- [Step 4. coinselection_controller_logic](./4_coin_selection_controller_logic/README.md) Implement controller and logic
- [Step 5. Setup Specter-DIY](./5_setup_diy/README.md) The foundation of effective Development is a good Development-Setup
- [Step 6. Implement Selection Viewing](./6_coin_selection_diy/README.md) Implement on hardware-side