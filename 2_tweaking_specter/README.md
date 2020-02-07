# Setup

# Prerequisites
* Python >= 3.7 installed via your preferred installation method
* `pip install virtualenv`
* You'll need either bitcoind available (> 0.18.1) on the commandline or docker installed
* your favorite IDE, VisualStudioCode if you don't have one. If you use your own, we assume that you know how you can debug flask applications
* If you want to run the tests with docker (optional) or run a (taproot-) regtest-node very easily via docker, please do:
```
docker pull registry.gitlab.com/cryptoadvance/specter-desktop/python-bitcoind:latest
docker pull registry.gitlab.com/cryptoadvance/specter-desktop/python-bitcoind:taproot
```

## The firmware
1. Clone this repo:
```
git clone https://github.com/stepansnigirev/workshop_advbitcoin.git
```
2. Connect the board via MiniUSB cable to your computer.
3. Check that it mounts  `DIS_F69NI`

4. cop the `firmware.bin` out of the files-folder of this repo to the `DIS_F69NI` mountpoint

5. copy the file to the  `DIS_F69NI` mount-point
6. Wait until the flashing (of the lights) stop and the mount reconnects

# The python-part (bitcoin python library + specter)

1. Connect the board via MicroUSB cable
2. Check that it mounts as `PYBFLASH`
4. Check that the board is also visible as a Virtual COM Port:
	- on **MacOS** it should be `/dev/tty.usb<something>` (on my PC it's `/dev/tty.usbmodem3379374D33382`)
	- on **Linux** it should be `/dev/ttyACM0`
	- on **Windows** check `Device Manager` - `COM ports`
5. Copy the files from this repository `/files/` to the `PYFLASH` directory so that you have about such a structure:
```
➜  PYBFLASH ls       
gui          main.py      __pycache__   rng.py
keystore.py  pin.py       qrscanner.py  specter.py
lib          platform.py  repl.py       usbhost.py
➜  PYBFLASH ls lib   
bitcoin  lvqr.py
➜  PYBFLASH 

```

# How to connect

On Linux and MacOS you can use `screen` (`screen /dev/ttySomeDevice 115200`, `Ctrl+A` - `Ctrl+K` to quit), on Windows [Putty](https://www.putty.org/) is a good choice.

Other alternatives: `picocom`, `minicom`, `miniterm.py` from `pyserial` package.

### USB Permissioning on Linux

On some Linux distributions it may be necessary to add additional udev rules in order to allow the REPL to work:

copy the following text to `/etc/udev/rules.d/49-micropython.rules`
```
# f055:9800 - MicroPython board
ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", ENV{ID_MM_DEVICE_IGNORE}="1"
ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", ENV{MTP_NO_PROBE}="1"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", MODE:="0666"
KERNEL=="ttyACM*", ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", MODE:="0666"
```

And then restart the udev service:

```bash
sudo udevadm control --reload-rules
```

# Running Specter-DIY

Create `main.py` on `PYBFLASH` with the following content:

```py
import specter

specter.run()
```

Restart the board (`pyb.hard_reset()` or press black button below LEDs on the backside)

## Running Specter-Desktop

in a nutshell:
```
git clone https://github.com/cryptoadvance/specter-desktop.git
cd specter-desktop
virtualenv --python=python3 .env
source .env/bin/activate
pip3 install -r requirements.txt

# run the server
cd specter-desktop
python3 src/specter/server.py
```

# Workshop content

Every section has a `README.md` file with explanation and code snippets, and a final `main.py` file that you can use to catch up if you are lost.

1. [Segwit v1 addresses](./01_schnorr) - generate addresses for segwit v1
2. [Signing](./02_signing) - sign transaction with Schnorr
3. [PSBT in Core](./03_psbt) - create Taproot-PSBT with Bitcoin Core
4. [Setup Desktop](./04_setup_desktop) Getting an effective development environment for Specter-Desktop
5. [Specter-Desktop](./05_specter_desktop) - Integrate Taproot-PSBT creation to Specter-Desktop
6. [Investigate for coin selection](./06_txselect_investigate) look at the stuff which is relevant for coin selection
7. [Unspents List](./07_txselect_rendering) Render the unspent transactions
8. [coinselection_controller_logic](./08_txselect_controller_logic) Implement controller and logic
9. [Implement Selection Viewing](./09_txselect_diy) Coinselection on hardware-side
10. [Vue.js crashcourse](./10_vuejs_crashcourse) Get an idea how vuejs works in minimum time
11. [Coinselection UX part1](./11_txselect_ux_part1) Make Coinselection an extended feature UX-wise
12 [Coinselection UX part2](./12_txselect_ux_part2) Calculate selected coins and compare with amount to spend

# References

- Library docs: ???
- [Repository](https://github.com/diybitcoinhardware/f469-disco/) with MicroPython build ([`taproot`](https://github.com/diybitcoinhardware/f469-disco/tree/taproot) branch for experimental taproot support).
- [Tutorial](https://github.com/diybitcoinhardware/f469-disco/tree/master/docs/tutorial/) section of the documentation
- [Youtube playlist](https://www.youtube.com/playlist?list=PLn2qRQUAAg0z_-R0swVuSsNS9bzRu6oP5) covering the content of this workshop + some theory
- GitHub repository of [Specter-DIY](https://github.com/cryptoadvance/specter-diy) hardware wallet ([`taproot`](https://github.com/cryptoadvance/specter-diy/tree/taproot) branch for experimental taproot support)
- GitHub repository of [Specter-Desktop](https://github.com/cryptoadvance/specter-desktop) ([`taproot`](https://github.com/cryptoadvance/specter-desktop/tree/taproot) branch for experimental taproot support)
- [How to](https://github.com/diybitcoinhardware/f469-disco/tree/master/jupyter_kernel)  get Jupyter notebook kernel that works with the board
