# Setup

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

# The bitcoin python library

1. Connect the board via MicroUSB cable
2. Check that it mounts as `PYBFLASH`
4. Check that the board is also visible as a Virtual COM Port:
	- on **MacOS** it should be `/dev/tty.usb<something>` (on my PC it's `/dev/tty.usbmodem3379374D33382`)
	- on **Linux** it should be `/dev/ttyACM0`
	- on **Windows** check `Device Manager` - `COM ports`
5. Copy the files from this repository `/files/` to the `PYFLASH` directory so that you have about such a structure:
```
➜  PYBFLASH ls -l
total 2
drwxr-xr-x 3 kim kim 2048 Feb  3 12:27 lib
➜  PYBFLASH ls -l lib 
total 4
drwxr-xr-x 2 kim kim 2048 Feb  3 12:27 bitcoin
-rw-r--r-- 1 kim kim 1258 Feb  3 12:27 lvqr.py

```

# How to connect

Install `pyserial` module:

```
pip3 install pyserial
```

This module includes a very handy tool to talk to serial ports called `miniterm.py`. 
Connect to the board using: 
```
miniterm.py <port_name>
```

On Linux and MacOS you can also use `screen`, on Windows [Putty](https://www.putty.org/) is a good choice.

Other alternatives: `picocom`, `minicom` and many others.

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

specter.start()
```

Restart the board (`pyb.hard_reset()` or press black button)

## Running Specter-Desktop

*copy-paste here*

`pip3 install -r requirements.txt`

# Workshop content

Every section has a `README.md` file with explanation and code snippets, and a final `main.py` file that you can use to catch up if you are lost.

1. [Segwit v1 addresses](./01_schnorr) - generate addresses for segwit v1
2. [Signing](./02_signing) - sign transaction with Schnorr
3. [PSBT in Core](./03_psbt) - create Taproot-PSBT with Bitcoin Core
4. [Specter-Desktop](./04_specter_desktop) - Integrate Taproot-PSBT creation to Specter-Desktop
5. Coin Selection - Kim:
	- 02_txselect_investigate
	- 03_txselect_rendering
	- 04_txselect_controller_logic
6. Taproot

# References

- Library docs: ???
- [Repository](https://github.com/diybitcoinhardware/f469-disco/) with MicroPython build ([`taproot`](https://github.com/diybitcoinhardware/f469-disco/tree/taproot) branch for experimental taproot support).
- [Tutorial](https://github.com/diybitcoinhardware/f469-disco/tree/master/docs/tutorial/) section of the documentation
- [Youtube playlist](https://www.youtube.com/playlist?list=PLn2qRQUAAg0z_-R0swVuSsNS9bzRu6oP5) covering the content of this workshop + some theory
- GitHub repository of [Specter-DIY](https://github.com/cryptoadvance/specter-diy) hardware wallet ([`taproot`](https://github.com/cryptoadvance/specter-diy/tree/taproot) branch for experimental taproot support)
- GitHub repository of [Specter-Desktop](https://github.com/cryptoadvance/specter-desktop) ([`taproot`](https://github.com/cryptoadvance/specter-desktop/tree/taproot) branch for experimental taproot support)
- [How to](https://github.com/diybitcoinhardware/f469-disco/tree/master/jupyter_kernel)  get Jupyter notebook kernel that works with the board
